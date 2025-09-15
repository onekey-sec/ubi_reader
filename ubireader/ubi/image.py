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

from __future__ import annotations
from typing import TYPE_CHECKING
from ubireader.debug import log
from ubireader.ubi import display
from ubireader.ubi.volume import get_volumes
from ubireader.ubi.block import get_blocks_in_list

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ubireader.ubi.block import description as Block
    from ubireader.ubi.block.layout import _LayoutInfo
    from ubireader.ubi.volume import description as Volume

class description(object):
    def __init__(self, blocks: dict[int, Block], layout_info: _LayoutInfo) -> None:
        self._image_seq = blocks[layout_info[0]].ec_hdr.image_seq
        self.vid_hdr_offset = blocks[layout_info[0]].ec_hdr.vid_hdr_offset
        self.version = blocks[layout_info[0]].ec_hdr.version
        self._block_list = layout_info[2]
        self._start_peb = min(layout_info[2])
        self._end_peb = max(layout_info[2])
        self._volumes = get_volumes(blocks, layout_info)
        log(description, 'Created Image: %s, Volume Cnt: %s' % (self.image_seq, len(self.volumes)))

    def __repr__(self) -> str:
        return 'Image: %s' % (self.image_seq)


    def get_blocks(self, blocks: Mapping[int, Block]) -> dict[int, Block]:
        return get_blocks_in_list(blocks, self._block_list)


    def _get_peb_range(self) -> list[int]:
        return [self._start_peb, self._end_peb]
    peb_range = property(_get_peb_range)


    def _get_image_seq(self) -> int:
        return self._image_seq
    image_seq = property(_get_image_seq)


    def _get_volumes(self) -> dict[str, Volume]:
        return self._volumes
    volumes = property(_get_volumes)


    def display(self, tab: str = '') -> str:
        return display.image(self, tab)
