#!/usr/bin/env python
#############################################################
# ubi_reader/tools/list_vtbl_blocks.py
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

##############################################################################
# List Volume Table block's name, PEB, LEB, and location in file.
# Requires an overrides.ini file if block data is inaccurate.
# ./list_vtbl_blocks.py <input file>
##############################################################################

import os
import sys
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file
from ubireader import settings
peb_size = 131072
settings.use_overrides = True
settings.overrides_path = 'override.ini'

if len(sys.argv) < 2:
    print """
Usage:
    list_vtbl_blocks.py <input.no_oob>
        Show locations of vtbl blocks.
    """
    sys.exit(1)

fpath = sys.argv[1]

if not os.path.exists(fpath):
    print 'File %s does not exist.' % fpath
    sys.exit(1)


ufile_obj = ubi_file(fpath, peb_size)
ubi_obj = ubi_base(ufile_obj)
last_vtbl = 0

for block in ubi_obj.blocks:
    if ubi_obj.blocks[block].is_vtbl:
        if last_vtbl + 1 != block:
            print '\n====== Volume Name(s) - %s ======' % ' | '.join([vtbl.name for vtbl in ubi_obj.blocks[block].vtbl_recs])
            print '\t---------------------------------------------'
            print '\tPEB#\t\t| LEB#\t\t| File Offset'
            print '\t---------------------------------------------'
            last_vtbl = block
        print '\t%s\t\t| %s\t\t| %s' % (ubi_obj.blocks[block].peb_num,
                                                ubi_obj.blocks[block].leb_num,
                                                ubi_obj.blocks[block].peb_num * peb_size)

