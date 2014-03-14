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

from ubi.defines import PRINT_COMPAT_LIST, PRINT_VOL_TYPE_LIST, UBI_VTBL_AUTORESIZE_FLG

def ubi(ubi, tab=''):
    print '%sUBI File' % (tab) 
    print '%s---------------------' % (tab)
    print '\t%sMin I/O: %s' % (tab, ubi.min_io_size)
    print '\t%sLEB Size: %s' % (tab, ubi.leb_size)
    print '\t%sPEB Size: %s' % (tab, ubi.peb_size)
    print '\t%sTotal Block Count: %s' % (tab, ubi.block_count)
    print '\t%sData Block Count: %s' % (tab, len(ubi.data_blocks_list))
    print '\t%sLayout Block Count: %s' % (tab, len(ubi.layout_blocks_list))
    print '\t%sInternal Volume Block Count: %s' % (tab, len(ubi.int_vol_blocks_list))
    print '\t%sUnknown Block Count: %s' % (tab, len(ubi.unknown_blocks_list))
    print '\t%sFirst UBI PEB Number: %s' % (tab, ubi.first_peb_num)


def image(image, tab=''):
    print '%s%s' % (tab, image)
    print '%s---------------------' % (tab)
    print '\t%sImage Sequence Num: %s' % (tab, image.image_seq)
    for volume in image.volumes:
        print '\t%sVolume Name:%s' % (tab, volume)
    print '\t%sPEB Range: %s - %s' % (tab, image.peb_range[0], image.peb_range[1])


def volume(volume, tab=''):
    print '%s%s' % (tab, volume)
    print '%s---------------------' % (tab)
    print '\t%sVol ID: %s' % (tab, volume.vol_id)
    print '\t%sName: %s' % (tab, volume.name)
    print '\t%sBlock Count: %s' % (tab, volume.block_count)

    print '\n'
    print '\t%sVolume Record' % (tab) 
    print '\t%s---------------------' % (tab)
    vol_rec(volume.vol_rec, '\t\t%s' % tab)

    print '\n'


def block(block, tab='\t'):
    print '%s%s' % (tab, block)
    print '%s---------------------' % (tab)
    print '\t%sFile Offset: %s' %  (tab, block.file_offset)
    print '\t%sPEB #: %s' % (tab, block.peb_num)
    print '\t%sLEB #: %s' % (tab, block.leb_num)
    print '\t%sBlock Size: %s' % (tab, block.size)
    print '\t%sInternal Volume: %s' % (tab, block.is_internal_vol)
    print '\t%sIs Volume Table: %s' % (tab, block.is_vtbl)
    print '\t%sIs Valid: %s' % (tab, block.is_valid)

    if not block.ec_hdr.errors:
        print '\n'
        print '\t%sErase Count Header' % (tab)
        print '\t%s---------------------' % (tab)
        ec_hdr(block.ec_hdr, '\t\t%s' % tab)

    if block.vid_hdr and not block.vid_hdr.errors:
        print '\n'        
        print '\t%sVID Header Header' % (tab)
        print '\t%s---------------------' % (tab)
        vid_hdr(block.vid_hdr, '\t\t%s' % tab)

    if block.vtbl_recs:
        print '\n'
        print '\t%sVolume Records' % (tab) 
        print '\t%s---------------------' % (tab)
        for vol in block.vtbl_recs:
            vol_rec(vol, '\t\t%s' % tab)

    print '\n'


def ec_hdr(ec_hdr, tab=''):
    for key, value in ec_hdr:
        if key == 'errors':
            value = ','.join(value)

        print '%s%s: %r' % (tab, key, value)


def vid_hdr(vid_hdr, tab=''):
    for key, value in vid_hdr:
        if key == 'errors':
            value = ','.join(value)

        elif key == 'compat':
            if value in PRINT_COMPAT_LIST:
                value = PRINT_COMPAT_LIST[value]
            else:
                value = -1

        elif key == 'vol_type':
            if value  < len(PRINT_VOL_TYPE_LIST):
                value = PRINT_VOL_TYPE_LIST[value]
            else:
                value = -1

        print '%s%s: %s' % (tab, key, value)


def vol_rec(vol_rec, tab=''):
    for key, value in vol_rec:
        if key == 'errors':
            value = ','.join(value)
        elif key == 'vol_type':
            if value < len(PRINT_VOL_TYPE_LIST):
                value = PRINT_VOL_TYPE_LIST[value]
            else:
                value = -1
        elif key == 'flags' and value == UBI_VTBL_AUTORESIZE_FLG:
            value = 'autoresize'
        elif key == 'name':
            value = value.strip('\x00')

        print '%s%s: %s' % (tab, key, value)
