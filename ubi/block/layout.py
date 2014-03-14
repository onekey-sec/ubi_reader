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

from ubi.block import sort


def group_pairs(blocks, layout_blocks_list):
    """Sort a list of layout blocks into pairs

    Arguments:
    List:blocks        -- List of block objects
    List:layout_blocks -- List of layout block indexes

    Returns:
    List -- Layout block pair indexes grouped in a list
    """
    layouts_grouped = [[blocks[layout_blocks_list[0]].peb_num]]

    for l in layout_blocks_list[1:]:
        for lnd in layouts_grouped:
            if blocks[l].vtbl_recs[0].name == blocks[lnd[0]].vtbl_recs[0].name:
                lnd.append(blocks[l].peb_num)
                break

        else:
                layouts_grouped.append([blocks[l].peb_num])

    return layouts_grouped


def associate_blocks(blocks, layout_pairs, start_peb_num):
    """Group block indexes with appropriate layout pairs

    Arguments:
    List:blocks        -- List of block objects
    List:layout_pairs  -- List of grouped layout blocks
    Int:start_peb_num  -- Number of the PEB to start from.

    Returns:
    List -- Layout block pairs grouped with associated block ranges.
    """
    seq_blocks = []
    for layout_pair in layout_pairs:
        seq_blocks = sort.by_image_seq(blocks, blocks[layout_pair[0]].ec_hdr.image_seq)

        layout_pair.append(seq_blocks)

    return layout_pairs
