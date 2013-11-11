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

from ubifs import nodes
from ubifs.defines import *
    

def common_hdr(ubifs, lnum, offset=0):
    """Get common header at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:lnum    -- LEB number common header is in.
    Int:offset  -- Offset in LEB of common header.

    Returns:
    Obj:common_hdr    -- Common header found at lnum/offset.
    """
    ubifs.file.seek((ubifs.leb_size * lnum) + offset)
    # crc checks here
    return nodes.common_hdr(ubifs.file.read(UBIFS_COMMON_HDR_SZ))


def ino_node(ubifs, lnum, offset=0):
    """Get inode node at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:lnum    -- LEB number inode node is in.
    Int:offset  -- Offset in LEB of inode node.

    Returns:
    Obj:ino_node    -- Inode node found at lnum/offset.
    """
    ubifs.file.seek((ubifs.leb_size * lnum) + offset)
    inon = nodes.ino_node(ubifs.file.read(UBIFS_INO_NODE_SZ))
    inon.data = ubifs.file.read(inon.data_len)
    return inon


def mst_node(ubifs, lnum, offset=0):
    """Get master node at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:lnum    -- LEB number master node is in.
    Int:offset  -- Offset in LEB of master node.

    Returns:
    Obj:mst_node    -- Master node found at lnum/offset.
    """
    ubifs.file.seek((ubifs.leb_size * lnum) + offset)
    return nodes.mst_node(ubifs.file.read(UBIFS_MST_NODE_SZ))
    

def sb_node(ubifs, offset=0):
    """Get superblock node at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:offset  -- Offset in LEB of superblock node.

    Returns:
    Obj:sb_node    -- Superblock node found at lnum/offset.
    """
    ubifs.file.seek(offset)
    return nodes.sb_node(ubifs.file.read(UBIFS_SB_NODE_SZ))


def dent_node(ubifs, lnum, offset=0):
    """Get dir entry node at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:lnum    -- LEB number dir entry node is in.
    Int:offset  -- Offset in LEB of dir entry node.

    Returns:
    Obj:dent_node    -- Dir entry node found at lnum/offset.
    """
    ubifs.file.seek((ubifs.leb_size * lnum) + offset)
    den = nodes.dent_node(ubifs.file.read(UBIFS_DENT_NODE_SZ))
    den.name = '%s' % ubifs.file.read(den.nlen)
    return den


def data_node(ubifs, lnum, offset=0, node_len=0):
    """Get data node at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:lnum    -- LEB number data node is in.
    Int:offset  -- Offset in LEB of data node.

    Returns:
    Obj:data_node    -- Data node found at lnum/offset.
    """
    ubifs.file.seek((ubifs.leb_size * lnum) + offset)
    datn = nodes.data_node(ubifs.file.read(UBIFS_DATA_NODE_SZ))
    datn.offset = (ubifs.leb_size * lnum) + offset + UBIFS_DATA_NODE_SZ
    datn.compr_len = node_len - UBIFS_COMMON_HDR_SZ - UBIFS_DATA_NODE_SZ
    return datn


def idx_node(ubifs, lnum, offset=0):
    """Get index node at given LEB number + offset.

    Arguments:
    Obj:ubifs   -- UBIFS object.
    Int:lnum    -- LEB number index node is in.
    Int:offset  -- Offset in LEB of index node.

    Returns:
    Obj:idx_node    -- Index node found at lnum/offset.
    """
    ubifs.file.seek((ubifs.leb_size * lnum) + offset)
    idxn = nodes.idx_node(ubifs.file.read(UBIFS_IDX_NODE_SZ))

    for i in range(0, idxn.child_cnt):
        idxn.branches.append(nodes.branch(ubifs.file.read(UBIFS_BRANCH_SZ)))

    return idxn
    