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


from modules.ubi import ubi, get_peb_size
from modules.ubi_io import leb_virtual_file, ubi_file
from modules.ubi.defines import PRINT_VOL_TYPE_LIST, UBI_VTBL_AUTORESIZE_FLG
from modules.ubifs import ubifs
from modules.ubifs.defines import PRINT_UBIFS_KEY_HASH, PRINT_UBIFS_COMPR

def get_ubi_params(ubi):
    """Get UBI utils params

    Arguments:
    Obj:ubi    -- UBI object.

    Returns:
    Dict       -- Dict keyed to volume with Dict of args and flags.
    """
    ubi_flags = {'min_io_size':'-m',
                    'max_bud_bytes':'-j',
                    'leb_size':'-e',
                    'default_compr':'-x',
                    'sub_page_size':'-s',
                    'fanout':'-f',
                    'key_hash':'-k',
                    'orph_lebs':'-p',
                    'log_lebs':'-l',
                    'max_leb_cnt': '-c',
                    'peb_size':'-p',
                    'sub_page_size':'-s',
                    'vid_hdr_offset':'-O',
                    'version':'-x',
                    'image_seq':'-Q',
                    'alignment':'-a',
                    'vol_id':'-n',
                    'name':'-N'}

    ubi_params = {}
    ubi_args = {}
    ini_params = {}

    for image in ubi.images:
        img_seq = image.image_seq
        ubi_params[img_seq] = {}
        ubi_args[img_seq] = {}
        ini_params[img_seq] = {}

        for volume in image.volumes:
            ubi_args[img_seq][volume] = {}
            ini_params[img_seq][volume] = {}

            # Get ubinize.ini settings
            ini_params[img_seq][volume]['vol_type'] = PRINT_VOL_TYPE_LIST[image.volumes[volume].vol_rec.vol_type]

            if image.volumes[volume].vol_rec.flags == UBI_VTBL_AUTORESIZE_FLG:
                ini_params[img_seq][volume]['vol_flags'] = 'autoresize'
            else:
                ini_params[img_seq][volume]['vol_flags'] = image.volumes[volume].vol_rec.flags

            ini_params[img_seq][volume]['vol_id'] = image.volumes[volume].vol_id
            ini_params[img_seq][volume]['vol_name'] = image.volumes[volume].name.rstrip('\x00')
            ini_params[img_seq][volume]['vol_alignment'] = image.volumes[volume].vol_rec.alignment

            ini_params[img_seq][volume]['vol_size'] = image.volumes[volume].vol_rec.reserved_pebs * ubi.leb_size

            # Create file object backed by UBI blocks.
            ufsfile = leb_virtual_file(ubi, image.volumes[volume])
            # Create UBIFS object
            uubifs = ubifs(ufsfile)

            for key, value in uubifs.superblock_node:
                if key == 'key_hash':
                    value = PRINT_UBIFS_KEY_HASH[value]
                elif key == 'default_compr':
                    value = PRINT_UBIFS_COMPR[value]

                if key in ubi_flags:
                    ubi_args[img_seq][volume][key] = value
            
            for key, value in image.volumes[volume].vol_rec:
                if key == 'name':
                    value = value.rstrip('\x00')

                if key in ubi_flags:
                    ubi_args[img_seq][volume][key] = value

            ubi_args[img_seq][volume]['version'] = image.version
            ubi_args[img_seq][volume]['vid_hdr_offset'] = image.vid_hdr_offset
            ubi_args[img_seq][volume]['sub_page_size'] = ubi_args[img_seq][volume]['vid_hdr_offset']
            ubi_args[img_seq][volume]['sub_page_size'] = ubi_args[img_seq][volume]['vid_hdr_offset']
            ubi_args[img_seq][volume]['image_seq'] = image.image_seq
            ubi_args[img_seq][volume]['peb_size'] = ubi.peb_size
            ubi_args[img_seq][volume]['vol_id'] = image.volumes[volume].vol_id

            ubi_params[img_seq][volume] = {'flags':ubi_flags, 'args':ubi_args[img_seq][volume], 'ini':ini_params[img_seq][volume]}

    return ubi_params


def print_ubi_params(ubi):
    ubi_params = get_ubi_params(ubi)
    for img_params in ubi_params:
        for volume in ubi_params[img_params]:
            ubi_flags = ubi_params[img_params][volume]['flags']
            ubi_args = ubi_params[img_params][volume]['args']
            ini_params = ubi_params[img_params][volume]['ini']
            sorted_keys = sorted(ubi_params[img_params][volume]['args'])
    
            print '\nVolume %s' % volume
            for key in sorted_keys:
                if len(key)< 8:
                    name = '%s\t' % key
                else:
                    name = key
                print '\t%s\t%s %s' % (name, ubi_flags[key], ubi_args[key])

            print '\n\t#ubinize.ini#'            
            print '\t[%s]' % ini_params['vol_name']
            for key in ini_params:
                if key != 'name':
                    print '\t%s=%s' % (key, ini_params[key])


if __name__ == '__main__':
    description = """Gather information from the UBI image useful for using mkfs.ubi, ubinize, ubiformat, etc. and print to screen.
Some may be duplicates, be sure to check which ones apply."""
    usage = 'ubi_utils_info.py [options] filepath'
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
    # Print info.
    print_ubi_params(uubi)
    sys.exit(0)
