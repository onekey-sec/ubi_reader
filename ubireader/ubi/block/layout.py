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
from typing import TYPE_CHECKING, Literal, Protocol, overload
from ubireader.debug import log
from ubireader.ubi.block import sort

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from ubireader.ubi.block import description as Block

class _LayoutPair(Protocol):
    def __getitem__(self, idx: Literal[0, 1], /) -> int: ...
    def __contains__(self, key: object, /) -> bool: ...

def group_pairs(blocks: Mapping[int, Block], layout_blocks_list: Iterable[int]) -> list[_LayoutPair]:
    """Sort a list of layout blocks into pairs

    Arguments:
    List:blocks        -- List of block objects
    List:layout_blocks -- List of layout block indexes

    Returns:
    List -- Layout block pair indexes grouped in a list
    """

    image_dict: dict[int, _LayoutPair] = {}
    for block_id in layout_blocks_list:
        image_seq=blocks[block_id].ec_hdr.image_seq
        if image_seq not in image_dict:
            image_dict[image_seq]=[block_id]
        else:
            image_dict[image_seq].append(block_id)

    log(group_pairs, 'Layout blocks found at PEBs: %s' % list(image_dict.values()))

    return list(image_dict.values())

class _LayoutInfo(_LayoutPair, Protocol):
    @overload
    def __getitem__(self, idx: Literal[0, 1], /) -> int: ...
    @overload
    def __getitem__(self, idx: Literal[2], /) -> list[int]: ...

def associate_blocks(blocks: Mapping[int, Block], layout_pairs: list[_LayoutPair]) -> list[_LayoutInfo]:
    """Group block indexes with appropriate layout pairs

    Arguments:
    List:blocks        -- List of block objects
    List:layout_pairs  -- List of grouped layout blocks

    Returns:
    List -- Layout block pairs grouped with associated block ranges.
    """

    seq_blocks: list[int] = []
    for layout_pair in layout_pairs:
        seq_blocks = sort.by_image_seq(blocks, blocks[layout_pair[0]].ec_hdr.image_seq)
        seq_blocks = [b for b in seq_blocks if b not in layout_pair]
        layout_pair.append(seq_blocks)

    return layout_pairs
