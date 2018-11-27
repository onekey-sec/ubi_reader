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

from ubireader.debug import error, log
from ubireader.ubi.block import sort

def get_newest(blocks, layout_blocks):
    """Filter out old layout blocks from list

    Arguments:
    List:blocks        -- List of block objects
    List:layout_blocks -- List of layout block indexes

    Returns:
    List -- Newest layout blocks in list
    """
    layout_temp = list(layout_blocks)

    for i in range(0, len(layout_temp)):
        for k in range(0, len(layout_blocks)):
            if blocks[layout_temp[i]].ec_hdr.image_seq != blocks[layout_blocks[k]].ec_hdr.image_seq:
                continue

            if blocks[layout_temp[i]].leb_num != blocks[layout_blocks[k]].leb_num:
                continue

            if blocks[layout_temp[i]].vid_hdr.sqnum > blocks[layout_blocks[k]].vid_hdr.sqnum:
                del layout_blocks[k]
                break

    return layout_blocks


def group_pairs(blocks, layout_blocks_list):
    """Sort a list of layout blocks into pairs

    Arguments:
    List:blocks        -- List of block objects
    List:layout_blocks -- List of layout block indexes

    Returns:
    List -- Layout block pair indexes grouped in a list
    """

    image_dict={}
    for block_id in layout_blocks_list:
        image_seq=blocks[block_id].ec_hdr.image_seq
        if image_seq not in image_dict:
            image_dict[image_seq]=[block_id]
        else:
            image_dict[image_seq].append(block_id)

    log(group_pairs, 'Layout blocks found at PEBs: %s' % list(image_dict.values()))

    return list(image_dict.values())


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
