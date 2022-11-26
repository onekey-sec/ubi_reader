#!/usr/bin/env python

#############################################################
# ubi_reader
# (C) Collin Mulliner based on Jason Pruitt's ubireader_extract_images
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

import os

from ubireader import settings
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs
from ubireader.ubifs.list import list_files as _list_files, copy_file
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi_io import ubi_file, leb_virtual_file
from ubireader.utils import UBIReaderError, guess_filetype, guess_start_offset, guess_leb_size, guess_peb_size


def list_files(
        filepath,
        log=False,
        verbose=False,
        block_size=None,
        start_offset=None,
        end_offset=None,
        guess_offset=None,
        warn_only_block_read_errors=False,
        ignore_block_header_errors=False,
        uboot_fix=False,
        listpath=None,
        copyfile=None,
        copyfiledest=None
    ):
    settings.logging_on = log

    settings.logging_on_verbose = verbose

    settings.warn_only_block_read_errors = warn_only_block_read_errors

    settings.ignore_block_header_errors = ignore_block_header_errors

    settings.uboot_fix = uboot_fix

    if not os.path.exists(filepath):
        raise UBIReaderError("File path doesn't exist.")

    if start_offset:
        start_offset = start_offset
    elif guess_offset:
        start_offset = guess_start_offset(filepath, guess_offset)
    else:
        start_offset = guess_start_offset(filepath)

    if end_offset:
        end_offset = end_offset
    else:
        end_offset = None

    filetype = guess_filetype(filepath, start_offset)
    if not filetype:
        raise UBIReaderError('Could not determine file type.')

    if block_size:
        block_size = block_size
    else:
        if filetype == UBI_EC_HDR_MAGIC:
            block_size = guess_peb_size(filepath)
        elif filetype == UBIFS_NODE_MAGIC:
            block_size = guess_leb_size(filepath)

        if not block_size:
            raise UBIReaderError('Block size could not be determined.')

    # Create file object.
    ufile_obj = ubi_file(filepath, block_size, start_offset, end_offset)

    if filetype == UBI_EC_HDR_MAGIC:
        # Create UBI object
        ubi_obj = ubi(ufile_obj)

        # Loop through found images in file.
        for image in ubi_obj.images:

            # Loop through volumes in each image.
            for volume in image.volumes:

                # Get blocks associated with this volume.
                vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)

                # Skip volume if empty.
                if not len(vol_blocks):
                    continue

                # Create LEB backed virtual file with volume blocks.
                # Necessary to prevent having to load entire UBI image
                # into memory.
                lebv_file = leb_virtual_file(ubi_obj, vol_blocks)

                # Create UBIFS object.
                ubifs_obj = ubifs(lebv_file)

                if listpath:
                    _list_files(ubifs_obj, listpath)
                if copyfile and copyfiledest:
                    copy_file(ubifs_obj, copyfile, copyfiledest)

    elif filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)

        if listpath:
            _list_files(ubifs_obj, listpath)
        if copyfile and copyfiledest:
            copy_file(ubifs_obj, copyfile, copyfiledest)

    else:
        print('Something went wrong to get here.')
