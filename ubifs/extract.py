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

import os
import struct

from ubifs.misc import parse_key, decompress
from ubifs.defines import *

def dents(ubifs, inodes, dent_node, path=''):
    inode = inodes[dent_node.inum]
    dent_path = os.path.join(path, dent_node.name)
        
    if dent_node.type == UBIFS_ITYPE_DIR:
        if not os.path.exists(dent_path):
            os.mkdir(dent_path)
        if 'dent' in inode:
            for dnode in inode['dent']:
                dents(ubifs, inodes, dnode, dent_path)

    elif dent_node.type == UBIFS_ITYPE_REG:
        try:
            if inode['ino'].nlink > 1:
                if 'hlink' not in inode:
                    inode['hlink'] = dent_path
                    _process_reg_file(ubifs, inode, dent_path)
                else:
                    os.link(inode['hlink'] ,dent_path)
            else:
                _process_reg_file(ubifs, inode, dent_path)
        except Exception, e:
            ubifs.log.write('_parse_reg:failed:%s' % e)

    elif dent_node.type == UBIFS_ITYPE_LNK:
        try:
            # probably will need to decompress ino data if > UBIFS_MIN_COMPR_LEN
            os.symlink('%s' % inode['ino'].data, dent_path)
        except Exception, e:
            ubifs.log.write('SYMLINK Fail: %s : %s' % (inode['ino'].data, dent_path)) 

    elif dent_node.type in [UBIFS_ITYPE_BLK, UBIFS_ITYPE_CHR]:
        try:
            dev = struct.unpack('<II', inode['ino'].data)[0]
            os.mknod(dent_path, inode['ino'].mode, dev)
        except Exception, e:
            ubifs.log.write('DEV Fail: %s : %s' % (dent_path, e))

    elif dent_node.type == UBIFS_ITYPE_FIFO:
        try:
            os.mkfifo(dent_path, inode['ino'].mode)
        except Exception, e:
            ubifs.log.write('FIFO Fail: %s : %s' % (dent_path, e))

    elif dent_node.type == UBIFS_ITYPE_SOCK:
        try:
            # Just create dummy file.
            _write_reg_file(ubifs, dent_path, inode, '')
        except Exception, e:
            ubifs.log.write('SOCK Fail: %s' % (dent_path))


def _write_reg_file(ubifs, path, inode, data):
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(data)
        os.chmod(path, inode['ino'].mode)
        os.chown(path, inode['ino'].uid, inode['ino'].gid)
    else:
        raise Exception('File collision: %s' % path)


def _process_reg_file(ubifs, inode, path):
    try:
        buf = ''
        if 'data' in inode:
            compr_type = 0
            sorted_data = sorted(inode['data'], key=lambda x: parse_key(x.key)[2])
            last_khash = parse_key(sorted_data[0].key)[2]-1
            
            for data in sorted_data:
                
                # If data nodes are missing in sequence, fill in blanks
                # with \x00 * UBIFS_BLOCK_SIZE
                khash = parse_key(data.key)[2]
                if khash - last_khash != 1:
                    while 1 != (khash - last_khash):
                        buf += '\x00'*UBIFS_BLOCK_SIZE
                        last_khash += 1

                compr_type = data.compr_type
                ubifs.file.seek(data.offset)
                d = ubifs.file.read(data.compr_len)
                buf += decompress(compr_type, data.size, d)
                last_khash = khash

    except Exception, e:
        raise Exception('inode num:%s :%s' % (parse_key(inode['ino'].key)[1], e))
    
    # Pad end of file with \x00
    if inode['ino'].size > len(buf):
        buf += '\x00' * (inode['ino'].size - len(buf))
        
    _write_reg_file(ubifs, path, inode, buf)