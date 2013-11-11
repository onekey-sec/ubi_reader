#!/usr/bin/env python
#############################################################
# ubi_reader
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
import sys
from ubi_io import ubi_file, leb_virtual_file
from ubifs import ubifs, get_leb_size
from ubifs.defines import *
from ubifs.misc import decompress, parse_key
from ubifs import walk, extract
from ubi import ubi, get_peb_size




def extract_all(ubifs, to_path='extracted'):
    """Extract UBIFS contents to_path/

    Arguments:
    Obj:ubifs    -- UBIFS object.
    Str:to_path  -- Path to extract contents to.
    """
    try:
        if not os.path.exists(to_path):
            os.mkdir(to_path)
        elif os.listdir(to_path):
            raise Exception('Directory is not empty.')
        inodes = {}
        walk.index(ubifs, ubifs.master_node.root_lnum, ubifs.master_node.root_offs, inodes)

        for dent in inodes[1]['dent']:
            extract.dents(ubifs, inodes, dent, to_path)

    except Exception, e:
        import traceback
        ubifs.log.write('%s' % e)
        traceback.print_exc()

if __name__ == '__main__':


    try:
        path = sys.argv[1]
        if not os.path.exists(path):
            print 'Path not found.'
            sys.exit(0)
    except:
        path = '-h'
    
    if path in ['-h', '--help']:
        print """
Usage:
    $ ubifs_extract_files.py path/to/file/ubifs.img

    Extracts the files/dirs from a UBI image and saves it
    to extracted/
    
    Only works with UBIFS files.
    Permissions are saved, may require running as root
    depending on files ownership and type.
    """
    sys.exit(1)

    block_size = get_leb_size(sys.argv[1])
    ubifs_file = ubi_file(sys.argv[1], block_size)
    ubifs = ubifs(ubifs_file)
    extract_all(ubifs)
