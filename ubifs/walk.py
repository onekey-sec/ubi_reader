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

from ubifs import extract
from ubifs.defines import *

def index(ubifs, lnum, offset, inodes={}):
    """Walk the index gathering Inode, Dir Entry, and File nodes.

    Arguments:
    Obj:ubifs    -- UBIFS object.
    Int:lnum     -- Logical erase block number.
    Int:offset   -- Offset in logical erase block.
    Dict:inodes  -- Dict of ino/dent/file nodes keyed to inode number.

    Returns:
    Dict:inodes  -- Dict of ino/dent/file nodes keyed to inode number.
        'ino'    -- Inode node.
        'data'   -- List of data nodes if present.
        'dent'   -- List of directory entry nodes if present.
    """
    chdr = extract.common_hdr(ubifs, lnum, offset)

    if chdr.node_type == UBIFS_IDX_NODE:
        idxn = extract.idx_node(ubifs, lnum, offset+UBIFS_COMMON_HDR_SZ)

        for branch in idxn.branches:                 
            index(ubifs, branch.lnum, branch.offs, inodes)

    elif chdr.node_type == UBIFS_INO_NODE:
        inon = extract.ino_node(ubifs, lnum, offset+UBIFS_COMMON_HDR_SZ)
        ino_num = inon.key['ino_num']

        if not ino_num in inodes:
            inodes[ino_num] = {}

        inodes[ino_num]['ino'] = inon

    elif chdr.node_type == UBIFS_DATA_NODE:
        datn = extract.data_node(ubifs, lnum, offset+UBIFS_COMMON_HDR_SZ, chdr.len)
        ino_num = datn.key['ino_num']
        
        if not ino_num in inodes:
            inodes[ino_num] = {}

        if not 'data' in inodes[ino_num]:
            inodes[ino_num]['data']= []

        inodes[ino_num]['data'].append(datn)

    elif chdr.node_type == UBIFS_DENT_NODE:
        dn = extract.dent_node(ubifs, lnum, offset+UBIFS_COMMON_HDR_SZ)
        ino_num = dn.key['ino_num']

        if not ino_num in inodes:
            inodes[ino_num] = {}

        if not 'dent' in inodes[ino_num]:
            inodes[ino_num]['dent']= []

        inodes[ino_num]['dent'].append(dn)
