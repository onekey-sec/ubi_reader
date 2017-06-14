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
# Split file assuming Layout blocks/vtbls are the first blocks
# then sorts by vol_id into seperate files.
# Requires an overrides.ini file if block data is inaccurate.
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
    split_by_volume.py <input.no_oob> <output_dir>
        Cut up file assuming vtbl_rec/layout blocks are start of image.
    """
    sys.exit(1)

fpath = sys.argv[1]
opath = sys.argv[2]

if not os.path.exists(fpath):
    print '%s does not exist.' % fpath
    sys.exit(1)

if not os.path.exists(opath):
    os.mkdir(opath)
else:
    a = raw_input('Output directory "%s" already exists. Merge/Overwrite contents? [y/N]:  ' % opath)

    if not a.lower() in ['yes', 'y']:
        print 'Exiting program.'
        sys.exit(0)
    print 'Merging and Overwriting "%s"' % opath

ufile_obj = ubi_file(fpath, peb_size)
ubi_obj = ubi_base(ufile_obj)
last_block = -2
fileh = []

i = 0
for block in ubi_obj.blocks:
    if ubi_obj.blocks[block].is_vtbl:
        if ubi_obj.blocks[block].peb_num > last_block + 1:
            last_block = ubi_obj.blocks[block].peb_num
        else:
            if fileh:
                for f in fileh:
                    f.close()
                fileh = []
            for vtbl in ubi_obj.blocks[block].vtbl_recs:
                fileh.append(open('%s/img-%s_vol-%s.bin' % (opath, i, vtbl.name), 'wb'))
            i += 1
    else:
        if ubi_obj.blocks[block].is_valid:
            fileh[ubi_obj.blocks[block].vid_hdr.vol_id].write(ufile_obj.read_block_data(ubi_obj.blocks[block]))


