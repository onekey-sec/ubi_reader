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
import re
import struct

from ubifs.defines import *
from ubifs import nodes
from ubifs.nodes import extract
from ubifs.log import log

class ubifs():
    """UBIFS object

    Arguments:
    Str:path           -- File path to UBIFS image. 
    
    Attributes:
    Int:leb_size       -- Size of Logical Erase Blocks.
    Int:min_io         -- Size of min I/O from vid_hdr_offset.
    Obj:sb_node        -- Superblock node of UBIFS image LEB0
    Obj:mst_node       -- Master Node of UBIFS image LEB1
    Obj:log            -- Log object for errors.

    Methods:
    key_search    -- Search nodes for matching key.
        Str:key   -- Hex string representation of key.
    """
    def __init__(self, ubifs_file):
        self.log = log()
        self._file = ubifs_file
        self._sb_node = extract.sb_node(self, UBIFS_COMMON_HDR_SZ)
        self._min_io_size = self._sb_node.min_io_size
        self._leb_size = self._sb_node.leb_size
        self._mst_node = extract.mst_node(self, 1, UBIFS_COMMON_HDR_SZ)
        self._mst_node = extract.mst_node(self, 2, UBIFS_COMMON_HDR_SZ)


    def _get_file(self):
        return self._file
    file = property(_get_file)


    def _get_superblock(self):
        """ Superblock Node Object

        Returns:
        Obj:Superblock Node
        """
        return self._sb_node
    superblock_node = property(_get_superblock)


    def _get_master_node(self):
        """Master Node Object

        Returns:
        Obj:Master Node
        """
        return self._mst_node
    master_node = property(_get_master_node)


    def _get_master_node2(self):
        """Master Node Object 2

        Returns:
        Obj:Master Node
        """
        return self._mst_node
    master_node2 = property(_get_master_node2)


    def _get_leb_size(self):
        """LEB size of UBI blocks in file.

        Returns:
        Int -- LEB Size.
        """
        return self._leb_size
    leb_size = property(_get_leb_size)


    def _get_min_io_size(self):
        """Min I/O Size

        Returns:
        Int -- Min I/O Size.
        """
        return self._min_io_size
    min_io_size = property(_get_min_io_size)


def get_leb_size(path):
    """Get LEB size from superblock

    Arguments:
    Str:path    -- Path to file.
    
    Returns:
    Int         -- LEB size.
    
    Searches file superblock and retrieves leb size.
    """

    f = open(path, 'rb')
    f.seek(0,2)
    file_size = f.tell()+1
    f.seek(0)
    block_size = 0

    for i in range(0, file_size, FILE_CHUNK_SZ):
        buf = f.read(FILE_CHUNK_SZ)

        for m in re.finditer(UBIFS_NODE_MAGIC, buf):
            start = m.start()
            chdr = nodes.common_hdr(buf[start:start+UBIFS_COMMON_HDR_SZ])

            if chdr and chdr.node_type == UBIFS_SB_NODE:
                sb_start = start + UBIFS_COMMON_HDR_SZ
                sb_end = sb_start + UBIFS_SB_NODE_SZ

                if chdr.len != len(buf[sb_start:sb_end]):
                    f.seek(sb_start)
                    buf = f.read(UBIFS_SB_NODE_SZ)
                else:
                    buf = buf[sb_start:sb_end]

                sbn = nodes.sb_node(buf)
                block_size = sbn.leb_size
                f.close()
                return block_size

    f.close()
    return block_size