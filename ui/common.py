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

from ubifs import walk, output

output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'output')


def extract_files(ubifs, out_path, perms=False):
    """Extract UBIFS contents to_path/

    Arguments:
    Obj:ubifs    -- UBIFS object.
    Str:out_path  -- Path to extract contents to.
    """
    try:
        inodes = {}
        walk.index(ubifs, ubifs.master_node.root_lnum, ubifs.master_node.root_offs, inodes)

        for dent in inodes[1]['dent']:
            output.dents(ubifs, inodes, dent, out_path, perms)

    except Exception, e:
        import traceback
        ubifs.log.write('%s' % e)
        traceback.print_exc()