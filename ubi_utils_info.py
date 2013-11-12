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

from ubi_io import ubi_file, leb_virtual_file
from ubi import ubi, get_peb_size
from ubifs import ubifs
from ubifs.defines import PRINT_UBIFS_KEY_HASH, PRINT_UBIFS_COMPR

def get_ubi_params(ubi):
    
    # From UBIFS Superblock
    ubifs_opt_args = {'min_io_size':'-m',
                    'leb_size':'-e',
                    'default_compr':'-x',
                    'sub_page_size':'-s',
                    'fanout':'-f',
                    'key_hash':'-k',
                    'orph_lebs':'-p',
                    'log_lebs':'-l'}


    ubi_opt_args = {'min_io_size':'-m',
                    'peb_size':'-p',
                    'sub_page_size':'-s',
                    'vid_hdr_offset':'-O',
                    'version':'-x',
                    'image_seq':'-Q',
                    'alignment':'-a',
                    'vol_id':'-n',
                    'name':'-N'}

    ubifs_args = {'min_io_size':0,
            'leb_size':0,
            'default_compr':'lzo',
            'sub_page_size':0,
            'fanout':0,
            'key_hash':'r5',
            'orph_lebs':0,
            'log_lebs':0}

    ubi_args = {'min_io_size':0,
            'peb_size':0,
            'vid_hdr_offset':0,
            'sub_page_size':0,
            'version':0,
            'image_seq':0,
            'alignment':0,
            'vol_id':0,
            'name':''}

    for image in ubi.images:

        for volume in image.volumes:
            # Create file object backed by UBI blocks.
            ufsfile = leb_virtual_file(uubi, image.volumes[volume])
            # Create UBIFS object
            uubifs = ubifs(ufsfile)

            for key, value in uubifs.superblock_node:
                if key == 'key_hash':
                    value = PRINT_UBIFS_KEY_HASH[value]
                elif key == 'default_compr':
                    value = PRINT_UBIFS_COMPR[value]

                if key in ubifs_args:
                    ubifs_args[key] = value
                if key in ubi_args:
                    ubi_args[key] = value
            
            for key, value in image.volumes[volume].vol_rec:
                if key == 'name':
                    value = value.rstrip('\x00')
                if key in ubifs_args:
                    ubifs_args[key] = value
                if key in ubi_args:
                    ubi_args[key] = value

            ubi_args['vid_hdr_offset'] = image.vid_hdr_offset
            ubi_args['sub_page_size'] = ubi_args['vid_hdr_offset']
            ubifs_args['sub_page_size'] = ubi_args['vid_hdr_offset']
            ubi_args['image_seq'] = image.image_seq
            ubi_args['peb_size'] = ubi.peb_size
            ubi_args['vol_id'] = image.volumes[volume].vol_id

            print '\nVolume %s' % volume
            for key in ubifs_args:
                if len(key)< 8:
                    name = '%s\t' % key
                else:
                    name = key
                print '\t%s\t%s %s' % (name, ubifs_opt_args[key], ubifs_args[key])

            for key in ubi_args:
                if len(key)< 8:
                    name = '%s\t' % key
                else:
                    name = key
                print '\t%s\t%s %s' % (name, ubi_opt_args[key], ubi_args[key])

if __name__ == '__main__':
    try:
        path = sys.argv[1]
        if not os.path.exists(path):
            print 'Path not found.'

    except:
        path = '-h'
    
    if path in ['-h', '--help']:
        print """
Usage:
    $ ubi_utils_info.py path/to/file.ubi

    Print mkfs.ubi, ubinize, ubiformat, etc. Options
    with values found in the provided UBI image.
    Double check options for the particular ubi program,
    as there are duplicates.
        """
        sys.exit(1)

    # Determine block size if not provided
    block_size = get_peb_size(path)
    # Create file object
    ufile = ubi_file(path, block_size)
    # Create UBI object
    uubi = ubi(ufile)
    # Create output file path and run ini creation.
    out_path = os.path.splitext(os.path.basename(path))[0]
    get_ubi_params(uubi)
    sys.exit()