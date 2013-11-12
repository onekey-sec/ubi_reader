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
from ui.common import extract_files, output_dir

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
    
    # Create path to extract to.
    img_name = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(output_dir, img_name)

    if not os.path.exists(out_path):
        os.mkdir(out_path)
    elif os.listdir(out_path):
        print 'Directory is not empty.'
        sys.exit()

    # Determine blocksize if not provided
    block_size = get_leb_size(sys.argv[1])
    # Create file object
    ufsfile = ubi_file(sys.argv[1], block_size)
    # Create UBIFS object
    uubifs = ubifs(ufsfile)
    # Run extract all files
    extract_files(uubifs, out_path, True)
    sys.exit()
