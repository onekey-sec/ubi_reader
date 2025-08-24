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

from ubireader.debug import error, log, verbose_display
from ubireader.ubifs.defines import *
from ubireader.ubifs import nodes, display
from typing import Optional
from zlib import crc32

class ubifs():
    """UBIFS object

    Arguments:
    Str:path           -- File path to UBIFS image. 
    
    Attributes:
    Obj:file           -- File object
    Int:leb_size       -- Size of Logical Erase Blocks.
    Int:min_io         -- Size of min I/O from vid_hdr_offset.
    Obj:sb_node        -- Superblock node of UBIFS image LEB0
    Obj:mst_node       -- Master Node of UBIFS image LEB1
    Obj:mst_node2      -- Master Node 2 of UBIFS image LEB2
    """
    def __init__(self, ubifs_file, master_key: Optional[bytes] = None):
        self.__name__ = 'UBIFS'
        self._file = ubifs_file
        self.master_key = master_key
        try:
            self.file.reset()
            sb_chdr = nodes.common_hdr(self.file.read(UBIFS_COMMON_HDR_SZ))
            log(self , '%s file addr: %s' % (sb_chdr, self.file.last_read_addr()))
            verbose_display(sb_chdr)

            if sb_chdr.node_type == UBIFS_SB_NODE:
                self.file.seek(UBIFS_COMMON_HDR_SZ)
                buf = self.file.read(UBIFS_SB_NODE_SZ)
                self._sb_node = nodes.sb_node(buf, self.file.last_read_addr())
                self._min_io_size = self._sb_node.min_io_size
                self._leb_size = self._sb_node.leb_size       
                log(self , '%s file addr: %s' % (self._sb_node, self.file.last_read_addr()))
                verbose_display(self._sb_node)
            else:
                raise Exception('Wrong node type.')
        except Exception as e:
            error(self, 'Fatal', 'Super block error: %s' % e)

        self._mst_nodes = [None, None]
        for i in range(0, 2):
            s_mst_offset = self.leb_size * (UBIFS_MST_LNUM + i)
            mst_offset = s_mst_offset
            mst_nodes = []
            try:
                while mst_offset < self.leb_size + s_mst_offset:
                    print("mst_offset::::: %X"%mst_offset)
                    self.file.seek(mst_offset)
                    mst_chdr = nodes.common_hdr(self.file.read(UBIFS_COMMON_HDR_SZ))
                    log(self , '%s file addr: %s' % (mst_chdr, self.file.last_read_addr()))
                    verbose_display(mst_chdr)
                    # crc
                    cpos = self.file.tell()
                    self.file.seek(mst_offset + 8)
                    crcdata = self.file.read(mst_chdr.len-8)
                    self.file.seek(cpos)
                    crc = (~crc32(crcdata) & 0xFFFFFFFF)
                    if crc != mst_chdr.crc:
                        break

                    self.file.seek(mst_offset + UBIFS_COMMON_HDR_SZ)
                    if mst_chdr.node_type == UBIFS_MST_NODE:
                        buf = self.file.read(UBIFS_MST_NODE_SZ)
                        mst_node = nodes.mst_node(buf, self.file.last_read_addr())
                        mst_nodes.append(mst_node)
                        log(self , '%s%s file addr: %s' % (mst_node, i, self.file.last_read_addr()))
                        verbose_display(mst_node)
                    elif mst_chdr.node_type == UBIFS_PAD_NODE:
                        buf = self.file.read(UBIFS_PAD_NODE_SZ)
                        padnode = nodes.pad_node(buf, self.file.last_read_addr())
                        mst_offset += padnode.pad_len
                        log(self , '%s%s file addr: %s' % (padnode, i, self.file.last_read_addr()))
                        verbose_display(padnode)
                    else:
                        raise Exception('Wrong node type.')
                    mst_offset += mst_chdr.len
            except Exception as e:
                error(self, 'Warn', 'Master block %s error: %s' % (i, e))
            
            # Get the valid master node with the highest sequence number.
            if len(mst_nodes):
                self._mst_nodes[i] = max(mst_nodes, key=lambda x: x.cmt_no)

        if self._mst_nodes[0] is None and self._mst_nodes[1] is None:
            error(self, 'Fatal', 'No valid Master Node found.')

        elif self._mst_nodes[0] is None and self._mst_nodes[1] is not None:
            self._mst_nodes[0] = self._mst_nodes[1]
            self._mst_nodes[1] = None
            log(self , 'Swapping Master Nodes due to bad first node.')


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
        return self._mst_nodes[0]
    master_node = property(_get_master_node)


    def _get_master_node2(self):
        """Master Node Object 2

        Returns:
        Obj:Master Node
        """
        return self._mst_nodes[1]
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
    
    def display(self, tab=''):
        """Print information about this object.
        
        Argument:
        Str:tab    -- '\t' for spacing this object.
        """
        return display.ubifs(self, tab)
