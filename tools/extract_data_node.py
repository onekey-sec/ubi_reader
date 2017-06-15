#!/usr/bin/env python
#############################################################
# ubi_reader/tools/extract_data_node.py
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
# Extract single data node.
# Takes input file and offset of UBIFS_NODE_MAGIC '\x31\x18\x10\x06'
# Saves uncompressed data to data_node.bin
#############################################################
import os
import sys
from zlib import crc32
from ubireader.ubifs.defines import *
from ubireader.ubifs import nodes
from ubireader.ubifs.misc import decompress

def crc_check(buf, ch_crc):
        crc = ~crc32(buf) & 0xFFFFFFFF
        if crc != ch_crc:
            print 'Bad Common Header CRC, expected 0x%x but got 0x%x' % (ch_crc, crc)
            return False
        return True

def extract_node(fpath, offset, opath):
    with open(fpath, 'rb') as f:
        f.seek(offset)

        chdr_buf = f.read(UBIFS_COMMON_HDR_SZ)
        chdr = nodes.common_hdr(chdr_buf)
        buf = f.read(chdr.len - UBIFS_COMMON_HDR_SZ)

        if chdr.magic != 101718065: #UBIFS_NODE_MAGIC:
            print "Magic Number failure, probably bad file offset."
            sys.exit(1)

        if not crc_check(chdr_buf[8:] + buf, chdr.crc):
            #pass
            sys.exit(1)

        print chdr.display()

        if chdr.node_type == UBIFS_DATA_NODE:
            node = nodes.data_node(buf, offset + UBIFS_COMMON_HDR_SZ + UBIFS_DATA_NODE_SZ)
            print node.display()

            with open(opath, 'wb') as fdn:
                try:
                    dbuf = decompress(node.compr_type, node.size, buf[UBIFS_DATA_NODE_SZ:])
                    f.seek(node.offset)
                    fdn.write(dbuf)
                except:
                    print "Decompress Error, node.size %s, buffer len(%s), compression type %s" % (node.size, len(buf[UBIFS_DATA_NODE_SZ:]), node.compr_type)
        else:
            print 'Not a data node.'

if __name__ == '__main__':
    # Check  ubireader.settings for more info
    if len(sys.argv) < 3:
        print """
    Usage:
        extract_data_node.py <input_file> <offset> <output_file>
            Extract single data node from UBIFS input_file at offset.
            Offset must be start of UBIFS_NODE_MAGIC '0x31 0x18 0x10 0x06'
            Will save uncompressed data in node to output_file.
        """
        sys.exit(1)

    fpath = sys.argv[1]
    offset = sys.argv[2]
    opath = sys.argv[3]

    if not os.path.exists(fpath):
        print '%s does not exist.' % fpath
        sys.exit(1)

    try:
        if 'x' in offset:
            offset = int(offset, 16)

        offset = int(offset)
    except:
        print 'Offset is not a integer'
        sys.exit(1)

    extract_node(fpath, offset, opath)
