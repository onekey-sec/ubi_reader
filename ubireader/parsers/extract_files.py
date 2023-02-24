import os
import struct

from ubireader import settings
from ubireader.debug import error, log, verbose_log
from ubireader.parsers import ArgHandler, makedir
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs, walk
from ubireader.ubifs.misc import decompress
from ubireader.ubifs.defines import *
from ubireader.ubi_io import ubi_file, leb_virtual_file

# Process file.
def parse(filepath, *args, **kwargs):
    args = ArgHandler(filepath, *args, **kwargs)

    # Create file object.
    ufile_obj = ubi_file(args.filepath, args.block_size, args.start_offset, args.end_offset)

    if args.filetype == UBI_EC_HDR_MAGIC:
        # Create UBI object
        ubi_obj = ubi(ufile_obj)

        # Loop through found images in file.
        for image in ubi_obj.images:

            # Create path for specific image
            # In case multiple images in data
            img_outpath = os.path.join(args.output_dir, '%s' % image.image_seq)

            # Loop through volumes in each image.
            for volume in image.volumes:

                # Get blocks associated with this volume.
                vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)

                # Create volume data output path.
                vol_outpath = os.path.join(img_outpath, volume)
                
                # Create volume output path directory.
                makedir(vol_outpath, False)

                # Skip volume if empty.
                if not len(vol_blocks):
                    continue

                # Create LEB backed virtual file with volume blocks.
                # Necessary to prevent having to load entire UBI image
                # into memory.
                lebv_file = leb_virtual_file(ubi_obj, vol_blocks)

                # Extract files from UBI image.
                ubifs_obj = ubifs(lebv_file)
                print('Extracting files to: %s' % vol_outpath)
                extract(ubifs_obj, vol_outpath, args.permissions)


    elif args.filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)

        # Create directory for files.
        makedir(args.output_dir, False)

        # Extract files from UBIFS image.
        print('Extracting files to: %s' % args.output_dir)
        extract(ubifs_obj, args.output_dir, args.permissions)

    else:
        print('Something went wrong to get here.')


def is_safe_path(basedir, path):
    basedir = os.path.realpath(basedir)
    path = os.path.realpath(os.path.join(basedir, path))
    return True if path.startswith(basedir) else False


def extract(ubifs, out_path, perms=False):
    """Extract UBIFS contents to_path/

    Arguments:
    Obj:ubifs    -- UBIFS object.
    Str:out_path  -- Path to extract contents to.
    """
    try:
        inodes = {}
        bad_blocks = []

        walk.index(ubifs, ubifs.master_node.root_lnum, ubifs.master_node.root_offs, inodes, bad_blocks)

        if len(inodes) < 2:
            raise Exception('No inodes found')

        for dent in inodes[1]['dent']:
            extract_dents(ubifs, inodes, dent, out_path, perms)

        if len(bad_blocks):
            error(extract, 'Warn', 'Data may be missing or corrupted, bad blocks, LEB [%s]' % ','.join(map(str, bad_blocks)))

    except Exception as e:
        error(extract, 'Error', '%s' % e)


def extract_dents(ubifs, inodes, dent_node, path='', perms=False):
    if dent_node.inum not in inodes:
        error(extract_dents, 'Error', 'inum: %s not found in inodes' % (dent_node.inum))
        return

    inode = inodes[dent_node.inum]

    if not is_safe_path(path, dent_node.name):
        error(extract_dents, 'Warn', 'Path traversal attempt: %s, discarding.' % (dent_node.name))
        return
    dent_path = os.path.realpath(os.path.join(path, dent_node.name))

    if dent_node.type == UBIFS_ITYPE_DIR:
        try:
            if not os.path.exists(dent_path):
                os.mkdir(dent_path)
                log(extract_dents, 'Make Dir: %s' % (dent_path))

                if perms:
                    _set_file_perms(dent_path, inode)
        except Exception as e:
            error(extract_dents, 'Warn', 'DIR Fail: %s' % e)

        if 'dent' in inode:
            for dnode in inode['dent']:
                extract_dents(ubifs, inodes, dnode, dent_path, perms)

        _set_file_timestamps(dent_path, inode)

    elif dent_node.type == UBIFS_ITYPE_REG:
        try:
            if inode['ino'].nlink > 1:
                if 'hlink' not in inode:
                    inode['hlink'] = dent_path
                    buf = _process_reg_file(ubifs, inode, dent_path)
                    _write_reg_file(dent_path, buf)
                else:
                    os.link(inode['hlink'], dent_path)
                    log(extract_dents, 'Make Link: %s > %s' % (dent_path, inode['hlink']))
            else:
                buf = _process_reg_file(ubifs, inode, dent_path)
                _write_reg_file(dent_path, buf)

            _set_file_timestamps(dent_path, inode)

            if perms:
                _set_file_perms(dent_path, inode)

        except Exception as e:
            error(extract_dents, 'Warn', 'FILE Fail: %s' % e)

    elif dent_node.type == UBIFS_ITYPE_LNK:
        try:
            # probably will need to decompress ino data if > UBIFS_MIN_COMPR_LEN
            os.symlink('%s' % inode['ino'].data.decode('utf-8'), dent_path)
            log(extract_dents, 'Make Symlink: %s > %s' % (dent_path, inode['ino'].data))

        except Exception as e:
            error(extract_dents, 'Warn', 'SYMLINK Fail: %s' % e) 

    elif dent_node.type in [UBIFS_ITYPE_BLK, UBIFS_ITYPE_CHR]:
        try:
            dev = struct.unpack('<II', inode['ino'].data)[0]
            if not settings.use_dummy_devices:
                os.mknod(dent_path, inode['ino'].mode, dev)
                log(extract_dents, 'Make Device Node: %s' % (dent_path))

                if perms:
                    _set_file_perms(dent_path, inode)
            else:
                log(extract_dents, 'Create dummy device.')
                _write_reg_file(dent_path, str(dev))

                if perms:
                    _set_file_perms(dent_path, inode)
                
        except Exception as e:
            error(extract_dents, 'Warn', 'DEV Fail: %s' % e)

    elif dent_node.type == UBIFS_ITYPE_FIFO:
        try:
            os.mkfifo(dent_path, inode['ino'].mode)
            log(extract_dents, 'Make FIFO: %s' % (path))

            if perms:
                _set_file_perms(dent_path, inode)
        except Exception as e:
            error(extract_dents, 'Warn', 'FIFO Fail: %s : %s' % (dent_path, e))

    elif dent_node.type == UBIFS_ITYPE_SOCK:
        try:
            if settings.use_dummy_socket_file:
                _write_reg_file(dent_path, '')
                if perms:
                    _set_file_perms(dent_path, inode)
        except Exception as e:
            error(extract_dents, 'Warn', 'SOCK Fail: %s : %s' % (dent_path, e))


def _set_file_perms(path, inode):
    os.chown(path, inode['ino'].uid, inode['ino'].gid)
    os.chmod(path, inode['ino'].mode)
    verbose_log(_set_file_perms, 'perms:%s, owner: %s.%s, path: %s' % (inode['ino'].mode, inode['ino'].uid, inode['ino'].gid, path))

def _set_file_timestamps(path, inode):
    os.utime(path, (inode['ino'].atime_sec, inode['ino'].mtime_sec))
    verbose_log(_set_file_timestamps, 'timestamps: access: %s, modify: %s, path: %s' % (inode['ino'].atime_sec, inode['ino'].mtime_sec, path))

def _write_reg_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    log(_write_reg_file, 'Make File: %s' % (path))


def _process_reg_file(ubifs, inode, path):
    try:
        buf = bytearray()
        start_key = 0x00 | (UBIFS_DATA_KEY << UBIFS_S_KEY_BLOCK_BITS)
        if 'data' in inode:
            compr_type = 0
            sorted_data = sorted(inode['data'], key=lambda x: x.key['khash'])
            last_khash = start_key - 1 

            for data in sorted_data:
                # If data nodes are missing in sequence, fill in blanks
                # with \x00 * UBIFS_BLOCK_SIZE
                if data.key['khash'] - last_khash != 1:
                    while 1 != (data.key['khash'] - last_khash):
                        buf += b'\x00'*UBIFS_BLOCK_SIZE
                        last_khash += 1

                compr_type = data.compr_type
                ubifs.file.seek(data.offset)
                d = ubifs.file.read(data.compr_len)
                buf += decompress(compr_type, data.size, d)
                last_khash = data.key['khash']
                verbose_log(_process_reg_file, 'ino num: %s, compression: %s, path: %s' % (inode['ino'].key['ino_num'], compr_type, path))

    except Exception as e:
        error(_process_reg_file, 'Warn', 'inode num:%s path:%s :%s' % (inode['ino'].key['ino_num'], path, e))
    
    # Pad end of file with \x00 if needed.
    if inode['ino'].size > len(buf):
        buf += b'\x00' * (inode['ino'].size - len(buf))
        
    return bytes(buf)
