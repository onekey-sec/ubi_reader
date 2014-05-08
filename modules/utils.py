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
from modules.debug import error, log
from modules.ubi.defines import UBI_EC_HDR_MAGIC
from modules.ubifs.defines import UBIFS_NODE_MAGIC

outputdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'output')
cur_outputdir = ''

def guess_filetype(path, start_offset=None):
    if not os.path.exists(path):
        error(guess_filetype, 'Fatal', 'Path not found: %s' % path)

    with open(path, 'rb') as f:
        if start_offset:
            f.seek(start_offset)
        buf = f.read(4)

        if buf == UBI_EC_HDR_MAGIC:
            log(guess_filetype, 'File looks like a UBI image.')
            return 'UBI'

        elif buf == UBIFS_NODE_MAGIC:
            log(guess_filetype, 'File looks like a UBIFS image.')
            return 'UBIFS'
        else:
            return None
    