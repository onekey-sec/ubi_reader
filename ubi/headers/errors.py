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
from zlib import crc32
from ubi.defines import *

def ec_hdr(ec_hdr, buf):
    if ec_hdr.hdr_crc != (~crc32(buf[:-4]) & 0xFFFFFFFF):
        ec_hdr.errors.append('crc')

    return ec_hdr

def vid_hdr(vid_hdr, buf):
    vid_hdr.errors = []
        
    if vid_hdr.hdr_crc != (~crc32(buf[:-4]) & 0xFFFFFFFF):
        vid_hdr.errors.append('crc')

    return vid_hdr

def vtbl_rec(vtbl_rec, buf):
    likely_vtbl = True

    if vtbl_rec.name_len != len(vtbl_rec.name.strip('\x00')):
        likely_vtbl = False

    elif vtbl_rec.vol_type not in [1,2]:
        likely_vtbl = False

    if vtbl_rec.crc != (~crc32(buf[:-4]) & 0xFFFFFFFF):
        vtbl_rec.errors.append('crc')

    if not likely_vtbl:
        vtbl_rec.errors = ['False']
        
    return vtbl_rec
