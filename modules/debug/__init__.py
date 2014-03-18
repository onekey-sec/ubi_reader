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

import sys
error_action = True
logging_on = True
logging_on_verbose = True

def log(obj, message):
    if logging_on or logging_on_verbose:
    # will out to file or console.
        print obj.__name__, message

def error(obj, level, message):
    if error_action is 'exit':
        print obj.__name__, '%s: %s' % (level, message)
        sys.exit(1)
    else:
        if level.lower() == 'warn':
            print obj.__name__, '%s: %s' % (level, message)
        elif level.lower() == 'fatal':
            print obj.__name__, '%s: %s' % (level, message)
            sys.exit(1)
        else:
            print obj.__name__, '%s: %s' % (level, message)
