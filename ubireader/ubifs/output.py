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

from ubireader import settings
from ubireader.ubifs.defines import *
from ubireader.ubifs import walk
from ubireader.ubifs.misc import decompress
from ubireader.debug import error, log, verbose_log

def extract_files(ubifs, out_path, perms=False):
    """Extract UBIFS contents to_path/

    Arguments:
    Obj:ubifs    -- UBIFS object.
    Str:out_path  -- Path to extract contents to.
    """
    try:
        inodes = {}
        walk.index(ubifs, ubifs.master_node.root_lnum, ubifs.master_node.root_offs, inodes)

        #only return if a directory cannot be extracted
        if not 'dent' in inodes[1].keys():
            print("Couldn't read dent for %s" % out_path)
            return

        for dent in inodes[1]['dent']:
            extract_dents(ubifs, inodes, dent, out_path, perms)

    except Exception as e:
        error(extract_files, 'Fatal', '%s' % e)


def extract_dents(ubifs, inodes, dent_node, path='', perms=False):
    inode = inodes[dent_node.inum]
    dent_path = os.path.join(path, dent_node.name)
        
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

    elif dent_node.type == UBIFS_ITYPE_REG:
        try:
            if inode['ino'].nlink > 1:
                if 'hlink' not in inode:
                    inode['hlink'] = dent_path
                    buf = _process_reg_file(ubifs, inode, dent_path)
                    _write_reg_file(dent_path, buf)
                else:
                    os.link(inode['hlink'] ,dent_path)
                    log(extract_dents, 'Make Link: %s > %s' % (dent_path, inode['hlink']))
            else:
                buf = _process_reg_file(ubifs, inode, dent_path)
                _write_reg_file(dent_path, buf)
                
            if perms:
                _set_file_perms(dent_path, inode)

        except Exception as e:
            error(extract_dents, 'Warn', 'FILE Fail: %s' % e)

    elif dent_node.type == UBIFS_ITYPE_LNK:
        try:
            # probably will need to decompress ino data if > UBIFS_MIN_COMPR_LEN
            os.symlink('%s' % inode['ino'].data, dent_path)
            log(extract_dents, 'Make Symlink: %s > %s' % (dent_path, inode['ino'].data))

        except Exception as e:
            error(extract_dents, 'Warn', 'SYMLINK Fail: %s' % e) 

    elif dent_node.type in [UBIFS_ITYPE_BLK, UBIFS_ITYPE_CHR]:
        try:
            dev = struct.unpack('<II', inode['ino'].data)[0]
            if True:
                os.mknod(dent_path, inode['ino'].mode, dev)
                log(extract_dents, 'Make Device Node: %s' % (dent_path))

                if perms:
                    _set_file_perms(path, inode)
            else:
                log(extract_dents, 'Create dummy node.')
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
    os.chmod(path, inode['ino'].mode)
    os.chown(path, inode['ino'].uid, inode['ino'].gid)
    verbose_log(_set_file_perms, 'perms:%s, owner: %s.%s, path: %s' % (inode['ino'].mode, inode['ino'].uid, inode['ino'].gid, path))

    
def _write_reg_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    log(_write_reg_file, 'Make File: %s' % (path))


def _process_reg_file(ubifs, inode, path):
    try:
        buf = b''
        if 'data' in inode:
            compr_type = 0
            sorted_data = sorted(inode['data'], key=lambda x: x.key['khash'])
            last_khash = sorted_data[0].key['khash']-1
            for data in sorted_data:
                
                # If data nodes are missing in sequence, fill in blanks
                # with \x00 * UBIFS_BLOCK_SIZE
                if data.key['khash'] - last_khash != 1:
                    while 1 != (data.key['khash'] - last_khash):
                        buf += '\x00'*UBIFS_BLOCK_SIZE
                        last_khash += 1

                compr_type = data.compr_type
                ubifs.file.seek(data.offset)
                d = ubifs.file.read(data.compr_len)
                buf += decompress(compr_type, data.size, d)
                last_khash = data.key['khash']
                verbose_log(_process_reg_file, 'ino num: %s, compression: %s, path: %s' % (inode['ino'].key['ino_num'], compr_type, path))

    except Exception as e:
        error(_process_reg_file, 'Warn', 'inode num:%s :%s' % (inode['ino'].key['ino_num'], e))
    
    # Pad end of file with \x00 if needed.
    if inode['ino'].size > len(buf):
        buf += '\x00' * (inode['ino'].size - len(buf))
        
    return buf
