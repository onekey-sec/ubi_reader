#!/usr/bin/env python
#############################################################
# ubi_reader/ubi
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
from ubi import display
from ubi.volume import get_volumes
from ubi.block import get_blocks_in_list, sort

class description(object):
    def __init__(self, blocks, image_num, layout_info):
        self._image_num = image_num
        self._image_seq = blocks[layout_info[0]].ec_hdr.image_seq
        self.vid_hdr_offset = blocks[layout_info[0]].ec_hdr.vid_hdr_offset
        
        self._start_peb = layout_info[2][0]
        self._total_pebs = layout_info[2][1]
        seq_blocks_list = sort.by_image_seq(blocks, self._image_seq)
        self._volumes = get_volumes(blocks, seq_blocks_list, layout_info)


    def __repr__(self):
        return 'Image Number: %s' % (self.image_num)


    def get_blocks(self, blocks):
        return get_blocks_in_list(blocks, range(self._start_peb, self._total_pebs))


    def _get_peb_range(self):
        return [self._start_peb, self._total_pebs]
    peb_range = property(_get_peb_range)


    def _get_image_num(self):
        return self._image_num
    image_num = property(_get_image_num)


    def _get_image_seq(self):
        return self._image_seq
    image_seq = property(_get_image_seq)


    def _get_volumes(self):
        return self._volumes
    volumes = property(_get_volumes)


    def display(self, tab=''):
        display.image(self, tab)