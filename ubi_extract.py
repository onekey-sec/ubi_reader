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

from ui.common import output_dir
from ubi import ubi, get_peb_size
from ubi_io import ubi_file


def extract_ubi(ubi, out_path):
    for image in ubi.images:
        f = open('%s/img-%s.ubi' % (out_path, image.image_seq), 'wb')
        # iterate through image blocks
        for block in image.get_blocks(ubi.blocks):
            if ubi.blocks[block].is_valid:
                # Write whole block to file
                f.write(ubi.file.read_block(ubi.blocks[block]))


if __name__ == '__main__':
    description = 'Extract UBI image from file. Works with binary dumps containing multiple images if image_seq is not the same.'
    usage = 'ubi_extract.py [options] filepath'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    
    parser.add_argument('-p', '--peb-size', type=int, dest='block_size',
                        help='Specify PEB size.')

    parser.add_argument('filepath', help='File to extract UBI contents of.')

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
        block_size = get_peb_size(path)


    # Create path to extract to.
    img_name = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(output_dir, img_name)

    if not os.path.exists(out_path):
        os.mkdir(out_path)


    # Create file object.
    ufile = ubi_file(path, block_size)
    # Create UBI object
    uubi = ubi(ufile)
    # Run extract UBI.
    extract_ubi(uubi, out_path)
    sys.exit()