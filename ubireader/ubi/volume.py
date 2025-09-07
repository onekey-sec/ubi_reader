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
from ubireader.ubi.block import sort, get_blocks_in_list, rm_old_blocks

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from ubireader.ubi import ubi as Ubi
    from ubireader.ubi.block import description as Block
    from ubireader.ubi.block.layout import _LayoutInfo
    from ubireader.ubi.headers import _vtbl_rec as VtblRec

class description(object):
    """UBI Volume object

    Attributes:
    Int:vol_id      -- Volume ID
    Str:name    -- Name of volume.
    Obj:vol_rec     -- Volume record object
    Int:block_count -- Number of block associated with volume.

    Methods:
    display(tab)      -- Print Volume information
        Str:tab        -- (optional) '\t' to preface lines with.

    get_blocks(blocks) -- Returns list of block objects tied to this volume

    Volume object is basically a list of block indexes and some metadata
    describing a volume found in a UBI image.
    """
    def __init__(self, vol_id: int, vol_rec: VtblRec, block_list: list[int]) -> None:
        self._vol_id = vol_id
        self._vol_rec = vol_rec
        self._name = self._vol_rec.name
        self._block_list = block_list
        log(description, 'Create Volume: %s, ID: %s, Block Cnt: %s' % (self.name, self.vol_id, len(self.block_list)))


    def __repr__(self) -> str:
        return 'Volume: %s' % (self.name.decode('utf-8'))


    def _get_name(self) -> bytes:
        return self._name
    name = property(_get_name)


    def _get_vol_id(self) -> int:
        return self._vol_id
    vol_id = property(_get_vol_id)


    def _get_block_count(self) -> int:
        return len(self._block_list)
    block_count = property(_get_block_count)


    def _get_vol_rec(self) -> VtblRec:
        return self._vol_rec
    vol_rec = property(_get_vol_rec)

    
    def _get_block_list(self) -> list[int]:
        return self._block_list
    block_list = property(_get_block_list)


    def get_blocks(self, blocks: Mapping[int, Block]) -> dict[int, Block]:
        return get_blocks_in_list(blocks, self._block_list)


    def display(self, tab: str = '') -> str:
        return display.volume(self, tab)


    def reader(self, ubi: Ubi) -> Iterator[bytes]:
        last_leb = 0
        for block in sort.by_leb(self.get_blocks(ubi.blocks)):
            if block == 'x':
                last_leb += 1
                yield b'\xff'*ubi.leb_size
            else:
                last_leb += 1
                yield ubi.file.read_block_data(ubi.blocks[block])


def get_volumes(blocks: Mapping[int, Block], layout_info: _LayoutInfo) -> dict[str, description]:
    """Get a list of UBI volume objects from list of blocks

    Arguments:
    List:blocks            -- List of layout block objects
    List:layout_info    -- Layout info (indexes of layout blocks and
                                        associated data blocks.)

    Returns:
    Dict -- Of Volume objects by volume name, including any
            relevant blocks.
    """
    volumes: dict[str, description] = {}

    vol_blocks_lists = sort.by_vol_id(blocks, layout_info[2])
    for vol_rec in blocks[layout_info[0]].vtbl_recs:
        vol_name = vol_rec.name.strip(b'\x00').decode('utf-8')
        if vol_rec.rec_index not in vol_blocks_lists:
            vol_blocks_lists[vol_rec.rec_index] = []

        vol_blocks_lists[vol_rec.rec_index] = rm_old_blocks(blocks, vol_blocks_lists[vol_rec.rec_index])
        volumes[vol_name] = description(vol_rec.rec_index, vol_rec, vol_blocks_lists[vol_rec.rec_index])
            
    return volumes

