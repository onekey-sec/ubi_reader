#!/usr/bin/env python
#############################################################
# ubi_reader/ubifs
# (c) 2013 Jason Pruitt (jrspruitt@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################

from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict
from lzallright import LZOCompressor
import struct
import zlib
from ubireader.ubifs.defines import *
from ubireader.debug import error, verbose_log
from ubireader.debug import error
from ubireader.ubifs.decrypt import lookup_inode_nonce, derive_key_from_nonce, datablock_decrypt

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ubireader.ubifs import ubifs as Ubifs
    from ubireader.ubifs.walk import Inode

# For happy printing
ino_types = ['file', 'dir','lnk','blk','chr','fifo','sock']
node_types = ['ino','data','dent','xent','trun','pad','sb','mst','ref','idx','cs','orph']
key_types = ['ino','data','dent','xent']

class ParsedKey(TypedDict):
    type: str
    ino_num: int
    khash: int

def parse_key(key: bytes) -> ParsedKey:
    """Parse node key

    Arguments:
    Str:key    -- Hex string literal of node key.

    Returns:
    Int:key_type   -- Type of key, data, ino, dent, etc.
    Int:ino_num    -- Inode number.
    Int:khash      -- Key hash.
    """
    hkey, lkey = struct.unpack('<II',key[0:UBIFS_SK_LEN])
    ino_num = hkey & UBIFS_S_KEY_HASH_MASK
    key_type = lkey >> UBIFS_S_KEY_BLOCK_BITS
    khash = lkey

    #if key_type < UBIFS_KEY_TYPES_CNT:
    return {'type':key_type, 'ino_num':ino_num, 'khash': khash}


def decompress(ctype: int, unc_len: int, data: bytes) -> bytes | None:
    """Decompress data.

    Arguments:
    Int:ctype    -- Compression type LZO, ZLIB (*currently unused*).
    Int:unc_len  -- Uncompressed data lenth.
    Str:data     -- Data to be uncompessed.

    Returns:
    Uncompressed Data.
    """
    if ctype == UBIFS_COMPR_LZO:
        try:
            return LZOCompressor.decompress(data, output_size_hint=unc_len)
        except Exception as e:
            error(decompress, 'Warn', 'LZO Error: %s' % e)
    elif ctype == UBIFS_COMPR_ZLIB:
        try:
            return zlib.decompress(data, -11)
        except Exception as e:
            error(decompress, 'Warn', 'ZLib Error: %s' % e)
    else:
        return data


def process_reg_file(ubifs: Ubifs, inode: Inode, path: str, inodes: Mapping[int, Inode]) -> bytes:
    try:
        buf = bytearray()
        start_key = (UBIFS_DATA_KEY << UBIFS_S_KEY_BLOCK_BITS)
        if 'data' in inode:
            compr_type = 0
            sorted_data = sorted(inode['data'], key=lambda x: x.key['khash'])
            last_khash = start_key - 1

            for data in sorted_data:
                # If data nodes are missing in sequence, fill in blanks
                # with \x00 * UBIFS_BLOCK_SIZE
                if data.key['khash'] - last_khash != 1:
                    while 1 != (data.key['khash'] - last_khash):
                        buf += b'\x00' * UBIFS_BLOCK_SIZE
                        last_khash += 1

                compr_type = data.compr_type
                ubifs.file.seek(data.offset)
                d = ubifs.file.read(data.compr_len)

                if ubifs.master_key is not None:
                    nonce = lookup_inode_nonce(inodes, inode)
                    block_key = derive_key_from_nonce(ubifs.master_key, nonce)
                    # block_id is based on the current hash
                    # there could be empty blocks
                    block_id = data.key['khash']-start_key
                    block_iv = struct.pack("<QQ", block_id, 0)
                    d = datablock_decrypt(block_key, block_iv, d)
                    # if unpading is needed the plaintext_size is valid and set to the
                    # original size of current block, so we can use this to get the amout
                    # of bytes to unpad
                    d = d[:data.plaintext_size]

                buf += decompress(compr_type, data.size, d)

                last_khash = data.key['khash']
                verbose_log(process_reg_file, 'ino num: %s, compression: %s, path: %s' % (inode['ino'].key['ino_num'], compr_type, path))

    except Exception as e:
        error(process_reg_file, 'Warn', 'inode num:%s path:%s :%s' % (inode['ino'].key['ino_num'], path, e))

    # Pad end of file with \x00 if needed.
    if inode['ino'].size > len(buf):
        buf += b'\x00' * (inode['ino'].size - len(buf))

    return bytes(buf)
