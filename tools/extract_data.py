#!/usr/bin/env python
#############################################################
# ubi_reader/tools/extract_data.py
# (c) 2017 Jason Pruitt (jrspruitt@gmail.com)
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

#############################################################
# Split file assuming Layout blocks/vtbls are the first blocks
# then sorts by vol_id into seperate files.
# Requires an overrides.ini file if block data is inaccurate.
#
#############################################################

import os
import re
import sys
from zlib import crc32
from ubireader.ubifs.defines import *
from ubireader.ubifs import nodes
from ubireader.ubifs.misc import decompress
from ubireader import settings
from ubireader.debug import *


def extract_dents(ufile, inodes, dent_node, path=''):
    """Extract Directory Entry nodes.
    Taken from ubireader.ubifs.output to make it easier to modify
    if needed for bad data.
    
    Caution in _process_reg_file() it normally inserts 0x00 where
    blank data would be, this saves space, but with broken sequences
    of data, or bad node values, this can quickly us up all the RAM
    and computer.
    """

    if dent_node.inum not in inodes:
        log(extract_dents, dent_node.display())
        error(extract_dents, 'Error', 'inum: %s not found in inodes' % (dent_node.inum))
        return

    inode = inodes[dent_node.inum]
    dent_path = os.path.join(path, dent_node.name)
        
    if dent_node.type == UBIFS_ITYPE_DIR:
        try:
            if not os.path.exists(dent_path):
                os.mkdir(dent_path)
                log(extract_dents, 'Make Dir: %s' % (dent_path))

        except Exception, e:
            error(extract_dents, 'Warn', 'DIR Fail: %s' % e)

        if 'dent' in inode:
            for dnode in inode['dent']:
                extract_dents(ufile, inodes, dnode, dent_path)

    elif dent_node.type == UBIFS_ITYPE_REG:
        try:
            if inode['ino'].nlink > 1:
                if 'hlink' not in inode:
                    inode['hlink'] = dent_path
                    buf = _process_reg_file(ufile, inode, dent_path)
                    _write_reg_file(dent_path, buf)
                else:
                    print dent_node.name
                    os.link(inode['hlink'] ,dent_path)
                    log(extract_dents, 'Make Link: %s > %s' % (dent_path, inode['hlink']))
            else:
                buf = _process_reg_file(ufile, inode, dent_path)
                _write_reg_file(dent_path, buf)

        except Exception, e:
            error(extract_dents, 'Warn', 'FILE Fail: %s' % e)

    elif dent_node.type == UBIFS_ITYPE_LNK:
        try:
            # probably will need to decompress ino data if > UBIFS_MIN_COMPR_LEN
            os.symlink('%s' % inode['ino'].data, dent_path)
            log(extract_dents, 'Make Symlink: %s > %s' % (dent_path, inode['ino'].data))

        except Exception, e:
            error(extract_dents, 'Warn', 'SYMLINK Fail: %s' % e) 

    elif dent_node.type in [UBIFS_ITYPE_BLK, UBIFS_ITYPE_CHR]:
        try:
            dev = struct.unpack('<II', inode['ino'].data)[0]
            if True:
                os.mknod(dent_path, inode['ino'].mode, dev)
                log(extract_dents, 'Make Device Node: %s' % (dent_path))
            else:
                log(extract_dents, 'Create dummy node.')
                _write_reg_file(dent_path, str(dev))
                
        except Exception, e:
            error(extract_dents, 'Warn', 'DEV Fail: %s' % e)

    elif dent_node.type == UBIFS_ITYPE_FIFO:
        try:
            os.mkfifo(dent_path, inode['ino'].mode)
            log(extract_dents, 'Make FIFO: %s' % (path))
        except Exception, e:
            error(extract_dents, 'Warn', 'FIFO Fail: %s : %s' % (dent_path, e))

    elif dent_node.type == UBIFS_ITYPE_SOCK:
        try:
            _write_reg_file(dent_path, '')
        except Exception, e:
            error(extract_dents, 'Warn', 'SOCK Fail: %s : %s' % (dent_path, e))
    
def _write_reg_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    log(_write_reg_file, 'Make File: %s' % (path))

def _process_reg_file(ufile, inode, path):
    try:
        buf = ''
        if 'data' in inode:
            compr_type = 0
            sorted_data = sorted(inode['data'], key=lambda x: x.key['khash'])
            last_khash = sorted_data[0].key['khash']-1

            for data in sorted_data:
                
                # If data nodes are missing in sequence, fill in blanks
                # with \x00 * UBIFS_BLOCK_SIZE
                #print 'khash difference: %s' % (data.key['khash'] - last_khash)
                # This is causing huge memory issues on broken image, not sure why.
                if False: #data.key['khash'] - last_khash != 1:
                    while 1 != (data.key['khash'] - last_khash):
                        buf += '\x00'*UBIFS_BLOCK_SIZE
                        last_khash += 1

                compr_type = data.compr_type
                ufile.seek(data.offset)
                d = ufile.read(data.compr_len)
                buf += decompress(compr_type, data.size, d)
                last_khash = data.key['khash']
                verbose_log(_process_reg_file, 'ino num: %s, compression: %s, path: %s' % (inode['ino'].key['ino_num'], compr_type, path))
        else:
            print inode
    except Exception, e:
        error(_process_reg_file, 'Warn', 'inode num:%s :%s' % (inode['ino'].key['ino_num'], e))
    
    # Pad end of file with \x00 if needed.
    # Causing potential memory issues on broken image.
    #print 'data size difference %s' % (inode['ino'].size, len(buf))
    #if inode['ino'].size > len(buf):
    #    buf += '\x00' * (inode['ino'].size - len(buf))
        
    return buf

def crc_check(buf, ch_crc, chdr):
        crc = ~crc32(buf) & 0xFFFFFFFF
        if crc != chdr.crc:
            #print 'expected %r but got %r' % (ch_crc, crc)
            return False
        return True

def find_nodes(fpath, inodes):
    """Find nodes in file and populate inodes.
    
    Arguments:
        Str:fpath       -- File path.
        Dict:inodes     -- Dict of inodes.

    Essentially the same as ubireader.ubifs.walk.index
    but does not use index or branch nodes to search
    the file for nodes. This finds all of them, and hopes
    for the best.
    
    Good place to print out information on the nodes, uncomment
    node.display() where relevant. Check ubireader.ubifs.defines
    for node properties.
    """

    locs = []
    with open(fpath, 'rb') as f:
        fbuf = f.read()
        locs = [m.start() for m in re.finditer(UBIFS_NODE_MAGIC, fbuf)]
        fbuf = ''
        f.seek(0)

        for loc in locs:
            is_bad = False
            f.seek(loc)
            chdr_buf = f.read(UBIFS_COMMON_HDR_SZ)
            chdr = nodes.common_hdr(chdr_buf)
            buf = f.read(chdr.len - UBIFS_COMMON_HDR_SZ)

            if not crc_check(chdr_buf[8:] + buf, chdr.crc, chdr):
                #pass
                continue

            #print chdr.display()

            if chdr.node_type == UBIFS_DATA_NODE:
                node = nodes.data_node(buf, loc + UBIFS_COMMON_HDR_SZ + UBIFS_DATA_NODE_SZ)
                ino_num = node.key['ino_num']

                if not ino_num in inodes:
                    inodes[ino_num] = {}

                if not 'data' in inodes[ino_num]:
                    inodes[ino_num]['data']= []

                inodes[ino_num]['data'].append(node)
                #print node.display()

            elif chdr.node_type == UBIFS_INO_NODE:
                node = nodes.ino_node(buf)
                ino_num = node.key['ino_num']

                if not ino_num in inodes:
                    inodes[ino_num] = {}
     
                inodes[ino_num]['ino'] = node
                #print node.display()

            elif chdr.node_type == UBIFS_DENT_NODE:
                node = nodes.dent_node(buf)
                ino_num = node.key['ino_num']

                if not ino_num in inodes:
                    inodes[ino_num] = {}

                if not 'dent' in inodes[ino_num]:
                    inodes[ino_num]['dent']= []

                inodes[ino_num]['dent'].append(node)
                #print node.display()

def extract_as_inodes(fpath, inodes, opath):
    """Extract data into inode named directories
    
    Arguments:
        Str:fpath       -- File path.
        Dict:inodes     -- Dict of inodes.
        Str:opath       -- Output path directory.

    An attempt to get around missing or broken links in the data.
    Makes a messy directory tree with dirs named with ino_num
    and little to no heirachy of the file system.
    
    If everything is okay, outpath/1 will contain all the data nice
    and neat. If not you can look through the other directories
    for the pieces.
    """
    
    with open(fpath, 'rb') as ufile:
        for k in inodes:
            if 'dent' not in inodes[k]:
                continue

            for dent in inodes[k]['dent']:
                ipath = '%s/%s' % (opath, k)
                if not os.path.exists(ipath):
                    os.mkdir(ipath)
                extract_dents(ufile, inodes, dent, ipath)

def extract_as_dirs(fpath, inodes, opath):
    """Extract data into normal directory tree.
    
    Arguments:
        Str:fpath       -- File path.
        Dict:inodes     -- Dict of inodes.
        Str:opath       -- Output path directory.

    Normal way of doing things ubi_reader probably would have worked.
    """
    
    with open(fpath, 'rb') as ufile:
        for dent in inodes[1]['dent']:
            extract_dents(ufile, inodes, dent, opath)

if __name__ == '__main__':
    # Check  ubireader.settings for more info
    settings.logging_on = False
    settings.logging_on_verbose = False 

    if len(sys.argv) < 3:
        print """
    Usage:
        extract_data.py <input.vol_split.no_oob> <output_dir>
            Attempts to extract data from file, by searching for
            all dent, ino, and data nodes in file, and trying to
            extract useful data.
        """
        sys.exit(1)

    fpath = sys.argv[1]
    opath = sys.argv[2]

    if not os.path.exists(fpath):
        print '%s does not exist.' % fpath
        sys.exit(1)

    if not os.path.exists(opath):
        os.mkdir(opath)
    else:
        a = raw_input('Output directory "%s" already exists. Merge/Overwrite contents? [y/N]:  ' % opath)

        if not a.lower() in ['yes', 'y']:
            print 'Exiting program.'
            sys.exit(0)
        print 'Merging and Overwriting "%s"' % opath


    inodes = {}
    # populates inodes with node info.
    find_nodes(fpath, inodes)

    # Create output directory
    if not os.path.exists(opath):
        os.mkdir(opath)

    # Start extraction process
    extract_as_inodes(fpath, inodes, opath)
    #extract_as_dirs(fpath, inodes, opath)








