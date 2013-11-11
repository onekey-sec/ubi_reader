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
from ubifs import ubifs
from ubi_io import ubi_file, leb_virtual_file
from ui_common import extract_files, output_folder

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
    $ ubi_extract_files.py path/to/file/image.ubi

    Extracts the files/dirs from a UBI image and saves it
    to extracted/
    
    Works with binary data with multiple images inside.
    Permissions are saved, may require running as root
    depending on files ownership and type.
        '''
        sys.exit(1)

    # Create path to extract to.
    img_name = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(output_folder, img_name)

    # Get block size if not provided
    block_size = get_peb_size(path)
    # Create file object.
    ubi_file = ubi_file(sys.argv[1], block_size)
    # Create UBI object
    ubi = ubi(ubi_file)

    # Traverse items found extracting files.
    for image in ubi.images:
        for volume in image.volumes:
            vol_out_path = os.path.join(out_path, volume)

            if not os.path.exists(vol_out_path):
                os.makedirs(vol_out_path)
            elif os.listdir(vol_out_path):
                print 'Volume directory is not empty. %s' % vol_out_path
                sys.exit()
            # Create file object backed by UBI blocks.
            ubifs_file = leb_virtual_file(ubi, image.volumes[volume])
            # Create UBIFS object
            ubifs = ubifs(ubifs_file)
            print 'Extracting Volume: %s' % volume
            extract_files(ubifs,  vol_out_path)

    sys.exit()
