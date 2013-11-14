#!/usr/bin/env python
#############################################################
# ubi_reader/ubifs
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

import ui

class log():
    def __init__(self):
        self.log_to_file = False
        self.log_file = 'ubifs_output.log' 
        self.exit_on_except = False
        self.quiet = False

    def _out(self, s):
        if not self.quiet:
            if self.log_to_file:
                with open(os.path.join(ui.common.output_dir, self.log_file), 'a') as f:
                    f.write('%s\n' % s)
                f.close()
            else:
                print '%s' % s
    
        if self.exit_on_except:
            sys.exit()

    def write(self, s):
        self._out(s)

    def write_node(self, n):
        buf = '%s\n' % n
        for key, value in n:
            buf += '\t%s: %s\n' % (key, value)
        self._out(buf)