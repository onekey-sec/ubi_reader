#!/usr/bin/env python
#############################################################
# ubi_reader/tools/split_by_volume.py
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
# extract_freshest_lebs.py
#
#############################################################

import os
import sys
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file
from ubireader import settings

settings.use_overrides = True
settings.overrides_path = 'override.ini'

peb_size = 131072

if len(sys.argv) < 3:
    print """
Usage:
    extract_freshest_lebs.py <input.no_oob> <output_file>
        Takes file of PEBs and removes duplicate LEBs saving
        the newest into output_file.
    """
    sys.exit(1)

fpath = sys.argv[1]
opath = sys.argv[2]

if not os.path.exists(fpath):
    print '%s does not exist.' % fpath
    sys.exit(1)

if os.path.exists(opath):
    a = raw_input('Output file "%s" already exists. Merge/Overwrite contents? [y/N]:  ' % opath)

    if not a.lower() in ['yes', 'y']:
        print 'Exiting program.'
        sys.exit(0)
    print 'Merging and Overwriting "%s"' % opath

ufile_obj = ubi_file(fpath, peb_size)
ubi_obj = ubi_base(ufile_obj)
fresh_lebs = {}

sorted_blocks = sorted(ubi_obj.blocks, key=lambda x: ubi_obj.blocks[x].leb_num)

for block in sorted_blocks:
    if not ubi_obj.blocks[block].is_valid:
        continue

    if ubi_obj.blocks[block].leb_num not in fresh_lebs:
        print ubi_obj.blocks[block].leb_num, type(ubi_obj.blocks[block].leb_num)
        fresh_lebs[ubi_obj.blocks[block].leb_num] = ubi_obj.blocks[block]

    elif fresh_lebs[ubi_obj.blocks[block].leb_num].vid_hdr.sqnum < ubi_obj.blocks[block].vid_hdr.sqnum:
        fresh_lebs[ubi_obj.blocks[block].leb_num] = ubi_obj.blocks[block]

with open(opath, 'wb') as f:
    for block in sorted_blocks:   
        if not ubi_obj.blocks[block].is_valid:
            continue

        elif fresh_lebs[ubi_obj.blocks[block].leb_num].peb_num == ubi_obj.blocks[block].peb_num:
            f.write(ufile_obj.read_block_data(ubi_obj.blocks[block]))



