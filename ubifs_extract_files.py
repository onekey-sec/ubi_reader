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

from ubi_io import ubi_file
from ubifs import ubifs, get_leb_size
from ui.common import extract_files, output_dir

if __name__ == '__main__':
    description = """Extract file contents of UBIFS image."""
    usage = 'ubifs_extract_files.py [options] filepath'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument('-l', '--log-file', dest='logpath',
                      help='Log output to file output/LOGPATH. (default: ubifs_output.log)')

    parser.add_argument('-k', '--keep-permissions', action='store_true', dest='permissions',
                      help='Maintain file permissions, requires running as root. (default: False)')


    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                      help='Suppress warnings and non-fatal errors. (default: False)')
    
    parser.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size.')
    
    parser.add_argument('-o', '--output-dir', dest='output_path',
                        help='Specify output directory path.')
    
    parser.add_argument('filepath', help='File to extract file contents of.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()


    args = parser.parse_args()

    if args.filepath:
        path = args.filepath
        if not os.path.exists(path):
            parser.error("File path doesn't exist.")

    if args.output_path:
        output_path = args.output_path
    else:
        img_name = os.path.splitext(os.path.basename(path))[0]
        output_path = os.path.join(output_dir, img_name)

    if args.logpath:
        log_to_file = True
        log_file = args.logpath
    else:
        log_to_file = None
        log_file = None

    # Determine block size if not provided
    if args.block_size:
        block_size = args.block_size
    else:
        block_size = get_leb_size(path)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    perms = args.permissions
    quiet = args.quiet

    # Create file object
    ufsfile = ubi_file(path, block_size)
    # Create UBIFS object
    uubifs = ubifs(ufsfile)
    # Set up logging
    uubifs.log.log_file = log_file
    uubifs.log.log_to_file = log_to_file
    uubifs.quiet = quiet

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    elif os.listdir(output_path):
        parser.error('Volume output directory is not empty. %s' % output_path)

    # Run extract all files
    print 'Writing to: %s' % output_path
    extract_files(uubifs, output_path, perms)
    sys.exit()
