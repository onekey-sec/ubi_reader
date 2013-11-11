#!/usr/bin/env python
#############################################################
# ubi_reader/ubi_io
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

class ubi_file(object):
    """UBI image file object

    Arguments:
    Str:path         -- Path to file to parse
    Int:block_size   -- Erase block size of NAND in bytes.
    Int:start_offset -- (optional) Where to start looking in the file for
                        UBI data.
    Int:end_offset   -- (optional) Where to stop looking in the file.
    
    Methods:
    seek            -- Put file head to specified byte offset.
        Int:offset
    read            -- Read specified bytes from file handle.
        Int:size
    tell            -- Returns byte offset of current file location.
    read_block      -- Returns complete PEB data of provided block
                       description.
        Obj:block
    read_block_data -- Returns LEB data only from provided block.
        Obj:block
    reader          -- Generator that returns data from file.
    reset           -- Reset file position to start_offset

    Handles all the actual file interactions, read, seek,
    extract blocks, etc.
    """

    def __init__(self, path, block_size, start_offset=0, end_offset=None):
        self._fhandle = open(path, 'rb')
        self._start_offset = start_offset

        if end_offset:
            self._end_offset = end_offset
        else:
            self._fhandle.seek(0,2)
            self._end_offset = self.tell() 

        self._block_size = block_size
        
        if start_offset >= self._end_offset:
            raise Exception('Start offset larger than file size!')

        self._fhandle.seek(self._start_offset)


    def _set_start(self, i):
        self._start_offset = i
    def _get_start(self):
        return self._start_offset
    start_offset = property(_get_start, _set_start)

    
    def _get_end(self):
        return self._end_offset
    end_offset = property(_get_end)


    def _get_block_size(self):
        return self._block_size
    block_size = property(_get_block_size)

        
    def seek(self, offset):
        self._fhandle.seek(offset)


    def read(self, size):
        return self._fhandle.read(size)


    def tell(self):
        return self._fhandle.tell()


    def reset(self):
        self._fhandle.seek(self.start_offset)


    def reader(self):
        self.reset()
        while True:
            cur_loc = self._fhandle.tell()
            if self.end_offset and cur_loc > self.end_offset:
                break            
            elif self.end_offset and self.end_offset - cur_loc < self.block_size:
                chunk_size = self.end_offset - cur_loc
            else:
                chunk_size = self.block_size

            buf = self.read(chunk_size)

            if not buf:
                break
            yield buf


    def read_block(self, block):
        """Read complete PEB data from file.
        
        Argument:
        Obj:block -- Block data is desired for.
        """
        self.seek(block.file_offset)
        return self._fhandle.read(block.size)


    def read_block_data(self, block):
        """Read LEB data from file
        
        Argument:
        Obj:block -- Block data is desired for.
        """
        self.seek(block.file_offset + block.ec_hdr.data_offset)
        buf = self._fhandle.read(block.size - block.ec_hdr.data_offset - block.vid_hdr.data_pad)
        return buf


class leb_virtual_file():
    def __init__(self, ubi, volume):
        self._ubi = ubi
        self._volume = volume
        self._blocks = sort.by_leb(self._volume.get_blocks(self._ubi.blocks))
        self._seek = 0
        self.leb_data_size = len(self._blocks) * self._ubi.leb_size
        self._last_leb = -1
        self._last_buf = ''


    def read(self, i):
        buf = ''
        leb = int(self.tell() / self._ubi.leb_size)
        offset = self.tell() % self._ubi.leb_size

        if leb == self._last_leb:
            self.seek(self.tell() + i)
            return self._last_buf[offset:offset+i]
        else:
            buf = self._ubi.file.read_block_data(self._ubi.blocks[self._blocks[leb]])
            self._last_buf = buf
            self._last_leb = leb
            self.seek(self.tell() + i)
            return buf[offset:offset+i]


    def reset(self):
        self.seek(0)


    def seek(self, offset):
        self._seek = offset


    def tell(self):
        return self._seek


    def reader(self):
        last_leb = 0
        for block in self._blocks:
            while 0 != (self._ubi.blocks[block].leb_num - last_leb):
                last_leb += 1
                yield '\xff'*self._ubi.leb_size

            last_leb += 1
            yield self._ubi.file.read_block_data(self._ubi.blocks[block])
