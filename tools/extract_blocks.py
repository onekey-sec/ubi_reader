#!/usr/bin/env python
#############################################################
# ubi_reader/tools/extract_blocks.py
# (c) 2017 Jason Pruitt (jrspruitt@gmail.com)
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

#############################################################
# Extract blocks that match search query into the raw PEB
# data and a text file of the attritubes.
#############################################################

import os
import sys
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file
from ubireader import settings

settings.use_overrides = True
settings.overrides_path = 'override.ini'
block_size = 131072

if len(sys.argv) < 4:
    print """
Usage:
    extract_blocks.py dump.no_oob "{'block.attr': value,...}"
        Extracts UBI blocks into PEB data files, and text description files.

    The second arg is a double quoted string, which contains a Dict of
    ubireader.ubi.block.description attributes. Attr names must be 
    single quoted, and value quoted for strings, or not for Ints.
    This runs through eval() so any valid python is okay.

    Example:
        "{'peb_num':[0, 1] + range(100, 102), 'ec_hdr.ec': 1, 'is_valid': True}"
        This matches block.peb_num 0, 1, 100, 101, and 102 
        with a block.ec_hdr.ec (erase count) of 1, that are valid PEB blocks.
        For a full list reference check ubireader.ubi.defines.py
        and ubireader.ubi.headers.py 
    """
    sys.exit(1)

fpath = sys.argv[1]
opath = sys.argv[3]
try:
    search = eval(sys.argv[2])
except NameError as e:
    print '\nDict key block attrs must be single quoted.'
    sys.exit(1)

if not os.path.exists(fpath):
    print '\nFile %s does not exist.' % fpath
    sys.exit(0)

if not isinstance(search, dict):
    print """
    Search terms must be a Dict of block PEB object items:value pairs.
    """
    sys.exit(1)

if os.path.exists(opath):
    a = raw_input('Output directory "%s" already exists. Merge/Overwrite contents? [y/N]:  ' % opath)

    if not a.lower() in ['yes', 'y']:
        print 'Exiting program.'
        sys.exit(0)
    print 'Merging and Overwriting "%s"' % opath

ufile_obj = ubi_file(fpath, block_size)
ubi_obj = ubi_base(ufile_obj)
blocks = []

for block in ubi_obj.blocks:
    match = True

    for key in search:
        b = ubi_obj.blocks[block]
        for attr in key.split('.'):
            if hasattr(b, attr):
                b = getattr(b, attr)

        if isinstance(search[key], list):
            if isinstance(b, list):
                for value in b:
                    if value in search[key]:
                        break
                else:
                    match = False
            elif b not in search[key]:
                match = False

        elif b != search[key]:
            match = False
            break

    if match:                
        blocks.append(ubi_obj.blocks[block])

print '\nBlock matches: %s' % len(blocks)

if len(blocks):
    os.mkdir(opath)

for block in blocks:
    with open('%s/PEB-%s_LEB:%s.block' % (opath, block.peb_num, block.leb_num), 'wb') as f:
        f.write(ubi_obj.file.read_block(block))
    with open('%s/PEB-%s_LEB:%s.block.display' % (opath, block.peb_num, block.leb_num), 'wb') as f:
        f.write(block.display())
            
