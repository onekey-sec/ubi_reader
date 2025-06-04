from ubireader.ubifs.defines import UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT
from ubireader.debug import error
from cryptography.hazmat.primitives.ciphers import (
   Cipher, algorithms, modes
)

AES_BLOCK_SIZE = algorithms.AES.block_size // 8

def lookup_inode_nonce(inodes: dict, inode: dict) -> bytes:
    # get the extended attribute 'xent' of the inode
    if 'xent' not in inode or not inode['xent']:
        raise ValueError(f"No xent found for inode {inode}")

    for xattr_inode in inode['xent']:
        if (xattr_inode.name == UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT):
            nonce_ino = inodes[xattr_inode.inum]['ino']
            nonce = nonce_ino.data[-16:]
            if len(nonce) != 16:
                raise ValueError(f"Invalid nonce length for inode {inode}")
            return nonce
    

def derive_key_from_nonce(master_key: bytes, nonce: bytes) -> bytes: 
    encryptor = Cipher(
        algorithms.AES(nonce),
        modes.ECB(),
    ).encryptor() 
    derived_key = encryptor.update(master_key) + encryptor.finalize()
    return derived_key


def filename_decrypt(key: bytes, ciphertext: bytes):
    
    # using AES CTS-CBC mode not supported by pyca cryptography 
    if len(ciphertext) > AES_BLOCK_SIZE:
        # Cipher Text Stealing Step
        pad = AES_BLOCK_SIZE - len(ciphertext) % AES_BLOCK_SIZE
    
        if pad > 0:  # Steal ciphertext only if needed (CTS)
            decryptor = Cipher(
                algorithms.AES(key[:32]),
                modes.ECB(),
            ).decryptor()
            second_to_last = ciphertext[-2*AES_BLOCK_SIZE+pad:-AES_BLOCK_SIZE+pad]
            plaintext = decryptor.update(second_to_last) + decryptor.finalize()
            # Apply padding 
            ciphertext += plaintext[-pad:]
        # Swap the last two blocks
        ciphertext = ciphertext[:-2*AES_BLOCK_SIZE] + ciphertext[-AES_BLOCK_SIZE:] + ciphertext[-2*AES_BLOCK_SIZE:-AES_BLOCK_SIZE]
    
    # AES-CBC step
    NULL_IV = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    decryptor = Cipher(
        algorithms.AES(key[:32]),
        modes.CBC(NULL_IV),
    ).decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.rstrip(b'\x00')
    

def datablock_decrypt(block_key: bytes, block_iv: bytes, block_data: bytes):
    decryptor = Cipher(
        algorithms.AES(block_key),
        modes.XTS(block_iv),
    ).decryptor()
    return decryptor.update(block_data) + decryptor.finalize()


def decrypt_filenames(ubifs, inodes):
    if ubifs.master_key is None:
        for inode in inodes.values():
             for dent in inode['dent']:
                dent.name = dent.raw_name.decode()
        return
    try:
        # for every node holding a cryptographic xattr, lookup the
        # nonce inode from the xattr 'inum' attr
        for inode in inodes.values():
            if "dent" not in inode:
                continue
            nonce = lookup_inode_nonce(inodes, inode)
            dec_key = derive_key_from_nonce(ubifs.master_key, nonce)
            for dent in inode['dent']:
                dent.name = filename_decrypt(dec_key, dent.raw_name).decode()
    except Exception as e:
        error(decrypt_filenames, 'Error', str(e))


def decrypt_symlink_target(ubifs, inodes, dent_node) -> str:
    if ubifs.master_key is None:
        return inodes[dent_node.inum]['ino'].data.decode()
    inode = inodes[dent_node.inum]
    ino = inode['ino']
    nonce = lookup_inode_nonce(inodes, inode)
    # the first two bytes is just header 0x10 0x00 all the time
    # the second byte is a null byte (0x00) added, need to be removed
    # before decryption
    encrypted_name = ino.data[2:-1]
    dec_key = derive_key_from_nonce(ubifs.master_key, nonce)
    lnkname = filename_decrypt(dec_key, encrypted_name)
    return lnkname.decode()
