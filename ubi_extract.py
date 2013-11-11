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
from ubi import ubi, get_peb_size
from ubi_io import ubi_file


def extract_ubi(ubi):
    for image in ubi.images:
        f = open('ubi_%s.ubi' % image.image_num, 'wb')

        # iterate through image blocks
        for block in image.get_blocks(ubi.blocks):
            if ubi.blocks[block].is_valid:
                # Write whole block to file
                f.write(ubi.file.read_block(ubi.blocks[block]))


if __name__ == '__main__':
    try:
        path = sys.argv[1]
        if not os.path.exists(path):
            print 'Path not found.'
            sys.exit(0)
    except:
        path = '-h'
    
    if path in ['-h', '--help']:
        print '''
Usage:
    $ ubi_extract.py path/to/file/dump.bin

    Extracts the  UBI image and saves it
    to ubi_<num>.ubi
    
    Works with binary data with multiple images inside.
        '''
        sys.exit(1)

    else:
        # Create UBI Object
        block_size = get_peb_size(path)
        ubi_file = ubi_file(path, block_size)
        ubi = ubi(ubi_file)
        extract_ubi(ubi)
        sys.exit(1)