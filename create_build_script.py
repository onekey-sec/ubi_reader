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
import ConfigParser

from ui.common import get_ubi_params, output_dir
from ubi_io import ubi_file
from ubi import ubi, get_peb_size

def make_files(ubi, output_path):
    ubi_params = get_ubi_params(ubi)

    for img_params in ubi_params:
        config = ConfigParser.ConfigParser()
        output_img_path = os.path.join(output_path, 'img-%s' % img_params)

        if not os.path.exists(output_img_path):
            os.mkdir(output_img_path)

        ini_path = os.path.join(output_img_path, 'img-%s.ini' % img_params)
        ubi_file = os.path.join('img-%s.ubi' % img_params)
        script_path = os.path.join(output_img_path, 'create_ubi_img-%s.sh' % img_params)
        ubifs_files =[]               
        buf = '#!/bin/sh\n'
        print 'Writing to: %s' % script_path 

        with open(script_path, 'w') as fscr:
            with open(ini_path, 'w') as fini:
                print 'Writing to: %s' % ini_path
                vol_idx = 0

                for volume in ubi_params[img_params]:
                    ubifs_files.append(os.path.join('img-%s_%s.ubifs' % (img_params, vol_idx)))
                    ini_params = ubi_params[img_params][volume]['ini']
                    ini_file = 'img-%s.ini' % img_params     
                    config.add_section(volume)
                    config.set(volume, 'mode', 'ubi')
                    config.set(volume, 'image', ubifs_files[vol_idx])
        
                    for i in ini_params:
                        config.set(volume, i, ini_params[i])

                    ubi_flags = ubi_params[img_params][volume]['flags']
                    ubi_args = ubi_params[img_params][volume]['args']
            
                    leb = '%s %s' % (ubi_flags['leb_size'], ubi_args['leb_size'])
                    peb = '%s %s' % (ubi_flags['peb_size'], ubi_args['peb_size'])
                    min_io = '%s %s' % (ubi_flags['min_io_size'], ubi_args['min_io_size'])
                    leb_cnt = '%s %s' % (ubi_flags['max_leb_cnt'], ubi_args['max_leb_cnt'])
                    vid_hdr = '%s %s' % (ubi_flags['vid_hdr_offset'], ubi_args['vid_hdr_offset'])
                    sub_page = '%s %s' % (ubi_flags['sub_page_size'], ubi_args['sub_page_size'])
    
                    buf += '/usr/sbin/mkfs.ubifs %s %s %s -r $%s %s\n' % (min_io, leb, leb_cnt, (vol_idx+1), ubifs_files[vol_idx])

                    vol_idx += 1

                config.write(fini)

            buf += '/usr/sbin/ubinize %s %s %s %s -o %s %s\n' % (peb, min_io, sub_page, vid_hdr, ubi_file, ini_file)
            fscr.write(buf)
        os.chmod(script_path, 0755)

if __name__ == '__main__':
    description = """Gather information from the UBI image and create a
    ubi file along with a shell script to create a UBI image from a given path."""
    usage = 'ubi_utils_info.py [options] filepath'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    
    parser.add_argument('-p', '--peb-size', type=int, dest='block_size',
                        help='Specify PEB size of input image.')
    
    parser.add_argument('-o', '--output-dir', dest='output_path',
                        help='Specify output directory path.')

    parser.add_argument('filepath', help='File to get info from.')

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

    if not os.path.exists(output_path):
        os.makedirs(output_path)

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
    make_files(uubi, output_path)
    sys.exit()