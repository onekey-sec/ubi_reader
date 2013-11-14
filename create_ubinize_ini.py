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
import ConfigParser
import argparse

from ubi_io import ubi_file
from ubi import ubi, get_peb_size
from ui.common import output_dir
from ubi.defines import UBI_VTBL_AUTORESIZE_FLG, PRINT_VOL_TYPE_LIST


def create_ubinize_ini(ubi, out_path):
    for image in ubi.images:
        config = ConfigParser.ConfigParser()
        f = open('%s-%s.ini' %  (os.path.join(output_dir, out_path), image.image_seq), 'w')
        print 'Wrote to: %s-%s.ini' % (os.path.join(output_dir, out_path), image.image_seq)

        for volume in image.volumes:
            config.add_section(volume)
            config.set(volume, 'mode', 'ubi')
            config.set(volume, 'image', 'path/to/ubifs.img')
            config.set(volume, 'vol_id', image.volumes[volume].vol_id)

            # Print volume attribtures and UBI headers
            for key, value in image.volumes[volume].vol_rec:
                if key == 'alignment':
                    config.set(volume, 'vol_alignment', value)
                elif key == 'vol_type':
                    config.set(volume, 'vol_type', PRINT_VOL_TYPE_LIST[value])
                elif key == 'name':
                    config.set(volume, 'vol_name', value.rstrip('\x00'))
                elif key == 'flags':
                    if value == UBI_VTBL_AUTORESIZE_FLG:
                        config.set(volume, 'vol_flags', 'autoresize')
                elif key == 'reserved_pebs':
                    config.set(volume, 'vol_size', ubi.leb_size * value)


        config.write(f)
        f.close()

if __name__ == '__main__':
    description = """Parse UBI image and create ubinize ini for use in creating a new UBI image. 
image: will need to be changed to your ubifs image path.
Warning: vol_size may not accurately reflect on device size."""
    usage = 'create_ubinize_ini.py [options] filepath'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    
    parser.add_argument('-p', '--peb-size', type=int, dest='block_size',
                        help='Specify PEB size.')

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
        block_size = get_peb_size(path)

    # Create file object
    ufile = ubi_file(path, block_size)
    # Create UBI object
    uubi = ubi(ufile)
    # Create output file path and run ini creation.
    out_path = os.path.splitext(os.path.basename(path))[0]
    create_ubinize_ini(uubi, out_path)
    sys.exit()