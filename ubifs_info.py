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

from ubi_io import ubi_file
from ubifs import ubifs, get_leb_size


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
    ubifs_info.py /path/to/ubifs.img

Prints superblock and master node contents.
            """
        sys.exit()

    path = sys.argv[1]
    # Determine block size if not provided.
    block_size = get_leb_size(path)
    # Create file object.
    ufile = ubi_file(path, block_size)
    # Create UBIFS Object.
    uubifs = ubifs(ufile)
    # Write super block node info
    uubifs.log.write_node(uubifs.superblock_node)
    # Write first master node.
    uubifs.log.write_node(uubifs.master_node)
    sys.exit()
