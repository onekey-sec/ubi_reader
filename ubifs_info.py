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
import argparse

from ubi_io import ubi_file
from ubifs import ubifs, get_leb_size


if __name__ == '__main__':

    description = """Print superblock and master node information."""
    usage = 'ubifs_info.py [options] filepath'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    
    parser.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size.')

    parser.add_argument('filepath', help='File to get info from.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    
    args = parser.parse_args()

    if args.filepath:
        path = args.filepath
        if not os.path.exists(path):
            parser.error("filepath doesn't exist.")

    # Determine block size if not provided
    if args.block_size:
        block_size = args.block_size
    else:
        block_size = get_leb_size(path)

    # Create file object.
    ufile = ubi_file(path, block_size)
    # Create UBIFS Object.
    uubifs = ubifs(ufile)
    # Write super block node info
    uubifs.log.write_node(uubifs.superblock_node)
    # Write first master node.
    uubifs.log.write_node(uubifs.master_node)
    uubifs.log.write_node(uubifs.master_node2)
    sys.exit()
