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

import sys

from ubi_io import ubi_file
from ubifs import ubifs, get_leb_size
if __name__ == '__main__':
    if sys.argv[1] in ['-h','--help']:
        print """
Usage:
    ubifs_info.py /path/to/ubifs.img

Prints superblock and master node contents.
            """
    path = sys.argv[1]
    block_size = get_leb_size(path)
    ubi_file = ubi_file(path, block_size)
    ubifs = ubifs(ubi_file)
    ubifs.log.write_node(ubifs.superblock_node)

    ubifs.log.write_node(ubifs.master_node)
    sys.exit()
