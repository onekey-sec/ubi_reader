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

from ubireader.ubifs import nodes
from ubireader.ubifs.defines import *
from ubireader.debug import error, log, verbose_log, verbose_display

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
    try:
        ubifs.file.seek((ubifs.leb_size * lnum) + offset)
        buf = ubifs.file.read(UBIFS_COMMON_HDR_SZ)
        chdr = nodes.common_hdr(buf)
        log(index , '%s file addr: %s' % (chdr, ubifs.file.last_read_addr()))
        verbose_display(chdr)

        node_buf = ubifs.file.read(chdr.len - UBIFS_COMMON_HDR_SZ)
        file_offset = ubifs.file.last_read_addr()

    except Exception as e:
        error(index, 'Fatal', 'leb: %s, ubifs offset: %s, error: %s' % (lnum, ((ubifs.leb_size * lnum) + offset), e))


    if chdr.node_type == UBIFS_IDX_NODE:
        idxn = nodes.idx_node(node_buf)
        log(index, '%s file addr: %s' % (idxn, file_offset))
        verbose_display(idxn)
        branch_idx = 0
        for branch in idxn.branches:
            verbose_log(index, '-------------------')
            log(index, '%s file addr: %s' % (branch, file_offset + UBIFS_IDX_NODE_SZ + (branch_idx * UBIFS_BRANCH_SZ)))
            verbose_display(branch)

            index(ubifs, branch.lnum, branch.offs, inodes)
            branch_idx += 1

    elif chdr.node_type == UBIFS_INO_NODE:
        inon = nodes.ino_node(node_buf)
        ino_num = inon.key['ino_num']
        log(index, '%s file addr: %s, ino num: %s' % (inon, file_offset, ino_num))
        verbose_display(inon)

        if not ino_num in inodes:
            inodes[ino_num] = {}

        inodes[ino_num]['ino'] = inon

    elif chdr.node_type == UBIFS_DATA_NODE:
        datn = nodes.data_node(node_buf, (ubifs.leb_size * lnum) + UBIFS_COMMON_HDR_SZ + offset + UBIFS_DATA_NODE_SZ)
        ino_num = datn.key['ino_num']
        log(index, '%s file addr: %s, ino num: %s' % (datn, file_offset, ino_num))
        verbose_display(datn)

        if not ino_num in inodes:
            inodes[ino_num] = {}

        if not 'data' in inodes[ino_num]:
            inodes[ino_num]['data']= []

        inodes[ino_num]['data'].append(datn)

    elif chdr.node_type == UBIFS_DENT_NODE:
        dn = nodes.dent_node(node_buf)
        ino_num = dn.key['ino_num']
        log(index, '%s file addr: %s, ino num: %s' % (dn, file_offset, ino_num))
        verbose_display(dn)

        if not ino_num in inodes:
            inodes[ino_num] = {}

        if not 'dent' in inodes[ino_num]:
            inodes[ino_num]['dent']= []

        inodes[ino_num]['dent'].append(dn)
