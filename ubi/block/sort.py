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

def list_by_list(blist, slist):
    """Sort list of block indexes, by another list.

    Argument:
    List:blist           -- List of block indexes.
    List:slist           -- Secondary list of blocks.

    Returns:
    List        -- List of block indexes matching slist from blist.
    """
    slist_blocks = []
    for block in blist:
        if block in slist:
            slist_blocks.append(block)

    return slist_blocks

def by_image_seq(blocks, image_seq):
    """Sort blocks by provided image_seq number.

    Argument:
    List:blocks       -- List of block objects to sort.
    Int:image_seq    -- image_seq number found in ec_hdr.
    
    Returns:
    List        -- List of block indexes matching image_seq number.
    """
    seq_blocks = []
    for block in blocks:
        if blocks[block].ec_hdr.image_seq == image_seq:
            seq_blocks.append(block)

    return seq_blocks


def by_range(blocks, block_range):
    """Sort blocks by Logical Erase Block number.
    
    Arguments:
    List:blocks            -- List of block objects to sort.
    List:block_range  -- range[0] = start number, range[1] = length
    
    Returns:
    List                        -- Indexes of blocks sorted by LEB.
    """
    peb_range = range(block_range[0],block_range[1])
    return [i for i in blocks if i in peb_range]


def by_leb(blocks):
    """Sort blocks by Logical Erase Block number.
    
    Arguments:
    List:blocks -- List of block objects to sort.
    
    Returns:
    List              -- Indexes of blocks sorted by LEB.
    """ 
    slist_len = len(blocks)
    slist = ['x'] * slist_len

    for block in blocks:
        if blocks[block].leb_num >= slist_len:
            add_elements = blocks[block].leb_num - slist_len + 1
            slist += (['x'] * add_elements)
            slist_len = len(slist)

        slist[blocks[block].leb_num] = block
    return slist
    return sorted(blocks.iterkeys(), key=lambda x: blocks[x].leb_num)


def by_vol_id(blocks, slist=None):
    """Sort blocks by volume id

    Arguments:
    Obj:blocks -- List of block objects.
    List:slist     -- (optional) List of block indexes.

    Return:
    Dict -- blocks grouped in lists with dict key as volume id.
    """

    vol_blocks = {}

    # sort block by volume
    # not reliable with multiple partitions (fifo)

    for i in blocks:
        if slist and i not in slist:
            continue
        elif not blocks[i].is_valid:
            continue

        if blocks[i].vid_hdr.vol_id not in vol_blocks:
            vol_blocks[blocks[i].vid_hdr.vol_id] = []

        vol_blocks[blocks[i].vid_hdr.vol_id].append(blocks[i].peb_num)

    return vol_blocks


def clean_bad(blocks, slist=None):
    """Remove blocks from list with errors

    Arguments:
    Obj:blocks -- List of block objects.
    List:slist     -- (optional) List of block indexes.

    Return:
    List -- Of error free block objects.
    """

    clean_blocks = []

    for i in range(0, len(blocks)):
        if slist and i not in slist:
            continue

        if blocks[i].is_valid:
            clean_blocks.append(i)

    return clean_blocks


def by_type(blocks, slist=None):
    """Sort blocks into layout, internal volume, data or unknown

    Arguments:
    Obj:blocks   -- List of block objects.
    List:slist   -- (optional) List of block indexes.

    Returns:
    List:layout  -- List of block indexes of blocks containing the
                    volume table records.
    List:data    -- List of block indexes containing filesystem data.
    List:int_vol -- List of block indexes  containing volume ids 
                    greater than UBI_INTERNAL_VOL_START that are not
                    layout volumes.
    List:unknown -- List of block indexes of blocks that failed validation
                    of crc in ed_hdr or vid_hdr.
    """

    layout = []
    data = []
    int_vol = []
    unknown = []
    
    for i in blocks:
        if slist and i not in slist:
            continue

        if blocks[i].is_vtbl and blocks[i].is_valid:
            layout.append(i)

        elif blocks[i].is_internal_vol and blocks[i].is_valid:
            int_vol.append(i)

        elif blocks[i].is_valid:
            data.append(i)

        else:
            unknown.append(i)

    return layout, data, int_vol, unknown
