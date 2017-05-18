#!/usr/bin/env python

#############################################################
# ubi_reader
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

from ubireader.debug import error
from ubireader import settings
from ConfigParser import ConfigParser

class overrides(object):
    def __init__(self):
        if settings.use_overrides:
            try:
                self._cp = ConfigParser()
                self._cp.readfp(open(settings.overrides_path))

            except Exception as e:
                error(overrides, 'fatal', e)

    def check(self, name, value):
        if not settings.use_overrides:
            return value

        if hasattr(self, name):
            return getattr(self, name)() or value

        return value

    def _get(self, section, option, otype='int'):
        if not self._cp.has_section(section):
            return None

        if not self._cp.has_option(section, option):
            return None

        try:
            if otype == 'list':
                value = self._cp.get(section, option)
                if not value:
                    return None

                if value.find(',') > 0:
                    value = [int(i.strip()) for i in value.split(',')]
                    return value

                elif value.find('-'):
                    value = [int(i.strip()) for i in value.split('-')]

                    if len(value) != 2:
                        raise Exception()
                    elif value[0] > value[1]:
                        raise Exception()

                    return range(value[0], value[1])
                   
            else:
                try:
                    return self._cp.getint(section, option)
                    # Empty option returns '' catch and return None
                    # won't alert on bad types, should fix this.
                except ValueError:
                    return None

        except Exception as e:
            error(overrides, 'Error', 'Override: Bad config option: %s: %s' % (option, e))
            return None

    def peb_size(self):
        return self._get('ubi', 'peb_size')

    def leb_size(self):
        return self._get('ubi', 'leb_size')

    def start_offset(self):
        return self._get('ubi', 'start_offset')

    def end_offset(self):
        return self._get('ubi', 'end_offset')

    def min_io_size(self):
        return self._get('ubi', 'min_io_size')

    def data_offset(self):
        return self._get('ubi', 'data_offset')

    def vid_hdr_offset(self):
        return self._get('ubi', 'vid_hdr_offset')

    def layout_blocks(self):
        return self._get('ubi', 'layout_blocks', 'list')
