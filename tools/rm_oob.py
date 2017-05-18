#!/usr/bin/env python
#############################################################
# ubi_reader/tools/rm_oob.py
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
# Removes OOB data at end of each page in a NAND Dump
# Adjust page_size and oob_size according to Datasheet
# ./rm_ooob.py input_file output_file
#############################################################
import os
import sys

# From NAND Datasheet
page_size = 2112
oob_size = 64

if len(sys.argv) < 3:
    print """
Usage:
    rm_oob.py <input.dump> <output.no_oob>
        Removes oob_size at end of every page_size
    """
    sys.exit(1)

fpath = sys.argv[1]
opath = sys.argv[2]

if not os.path.exists(fpath):
    print 'Input file "%s" does not exist.' % fpath
    sys.exit(1)

if os.path.exists(opath):
    a = raw_input('Output file "%s" already exists. Overwrite? [y/N]:  ' % opath)

    if not a.lower() in ['yes', 'y']:
        print 'Exiting program.'
        sys.exit(0)
    print 'Overwriting "%s"' % opath

fi_size = os.path.getsize(fpath)

with open(fpath, 'rb') as fi:
    with open(opath, 'wb') as fo:
        print 'Writing to %s' % opath
        for i in xrange(0, fi_size, page_size):
            fi.seek(i)
            fo.write(fi.read(page_size - oob_size))

