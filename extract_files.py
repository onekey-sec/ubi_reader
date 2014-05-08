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
import time
import argparse
from shutil import rmtree

from modules.ubi import ubi, get_peb_size
from modules.ubifs import ubifs
from modules.ubifs.output import extract_files
from modules.ubi_io import ubi_file, leb_virtual_file
from modules import settings
from modules.debug import error, log
from modules.utils import guess_filetype

cur_output_dir = ''

def make_output_dir():
    if not os.path.exists(settings.output_dir):
        try:
            os.mkdir(settings.output_dir)
            log(make_cur_output_dir, ' Created path: %s' % settings.output_dir)
        except Exception, e:
            print e


def make_cur_output_dir(path):
    cur_output_dir = os.path.join(settings.output_dir, path)
    if not os.path.exists(cur_output_dir):
        try:
            os.mkdir(cur_output_dir)
            log(make_cur_output_dir, ' Created path: %s' % cur_output_dir)
        except Exception, e:
            print e


def rm_cur_output_dir():
    path = cur_output_dir
    if os.path.exists(path):
        try:
            rmtree(path)
            log(rm_cur_output_dir, 'Removing path: %s' % cur_output_dir)
        except Exception, e:
            print e


def extract_ubifs(ufile, outpath, perms):
    if ufile.is_valid:
        ubifs_obj = ubifs(ufile)
        print 'Extracting files to: %s' % outpath
        extract_files(ubifs_obj, outpath, perms)
    else:
        error(extract_ubifs, 'Warn', 'UBI file is not valid. Skipping.')


def create_vol_dir(vol_outpath):
    if os.path.exists(vol_outpath):
        if os.listdir(vol_outpath):
            error(create_vol_dir, 'Fatal', 'Volume output directory is not empty. %s' % vol_outpath)
    else:
        try:
            os.makedirs(vol_outpath)
        except Exception, e:
            print e


if __name__=='__main__':
    start = time.time()
    description = 'Extract contents of UBI/UBIFS image.'
    usage = 'ubi_extract_files.py [options] filepath'
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('-k', '--keep-permissions', action='store_true', dest='permissions',
                      help='Maintain file permissions, requires running as root. (default: False)')

    parser.add_argument('-l', '--log', action='store_true', dest='log',
                      help='Print extraction information to screen.')

    parser.add_argument('-v', '--verbose-log', action='store_true', dest='verbose',
                      help='Prints nearly everything about anything to screen.')
    
    parser.add_argument('-p', '--peb-size', type=int, dest='block_size',
                        help='Specify PEB size. (UBI Only)')
    
    parser.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size. (UBIFS Only)')

    parser.add_argument('-s', '--start-offset', type=int, dest='start_offset',
                        help='Specify offset of UBI/UBIFS data in file. (default: 0)')

    parser.add_argument('-o', '--output-dir', dest='output_path',
                        help='Specify output directory path.')

    parser.add_argument('filepath', help='File to extract contents of.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.filepath:
        path = args.filepath
        if not os.path.exists(path):
            parser.error("File path doesn't exist.")

    if args.start_offset:
        start_offset = args.start_offset
    else:
        start_offset = 0

    filetype = guess_filetype(path, start_offset)
    if not filetype:
        parser.error('Could not determine file type.')

    if args.output_path:
        output_path = args.output_path
    else:
        img_name = os.path.splitext(os.path.basename(path))[0]
        output_path = os.path.join(settings.output_dir, img_name)

    settings.logging_on = args.log

    settings.logging_on_verbose = args.verbose

    if args.block_size:
        block_size = args.block_size
    else:
        block_size = get_peb_size(path)

    perms = args.permissions

    # Create file object.
    ufile_obj = ubi_file(path, block_size, start_offset)

    if filetype == 'UBI':
        # Create UBI object
        ubi_obj = ubi(ufile_obj)

        # Loop through found images in file.
        for image in ubi_obj.images:
            # Loop through volumes in each image.
            for volume in image.volumes:
                    
                # Get blocks associated with this volume.
                vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)

                # Skip volume if empty.
                if not len(vol_blocks):
                    print '%s volume empty' % image.volumes[volume].name
                    continue

                # Create volume data output path.
                vol_outpath = os.path.join(output_path, volume)
                
                # Create volume output path directory.
                create_vol_dir(vol_outpath)

                # Create LEB backed virtual file with volume blocks.
                # Necessary to prevent having to load entire UBI image
                # into memory.
                lebv_file = leb_virtual_file(ubi_obj, vol_blocks)

                # Extract files from UBI image.
                extract_ubifs(lebv_file, vol_outpath, perms)

    elif filetype == 'UBIFS':
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)

        # Extract files from UBIFS image.
        extract_files(ubifs_obj, output_path, perms)

    else:
        pass