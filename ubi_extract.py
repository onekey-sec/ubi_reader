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
        img_path = os.path.join(out_path, 'img-%s.ubi' % image.image_seq)
        if os.path.exists(img_path):
            print 'File exists skipping: %s' % img_path
        else:
            print 'Writing to:  %s' % img_path
            f = open(img_path, 'wb')
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
    
    parser.add_argument('-o', '--output-dir', dest='output_path',
                        help='Specify output directory path.')

    parser.add_argument('filepath', help='File to extract UBI contents of.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    
    args = parser.parse_args()

    if args.filepath:
        path = args.filepath
        if not os.path.exists(path):
            parser.error("filepath doesn't exist.")

    if args.output_path:
        output_path = args.output_path
    else:
        img_name = os.path.splitext(os.path.basename(path))[0]
        output_path = os.path.join(output_dir, img_name)

    # Determine block size if not provided
    if args.block_size:
        block_size = args.block_size
    else:
        block_size = get_peb_size(path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)


    # Create file object.
    ufile = ubi_file(path, block_size)
    # Create UBI object
    uubi = ubi(ufile)
    # Run extract UBI.
    extract_ubi(uubi, output_path)
    sys.exit()