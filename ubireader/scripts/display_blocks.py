#!/usr/bin/env python
#############################################################
# ubi_reader/scripts/ubireader_display_blocks
# (c) 2019 Jason Pruitt (jrspruitt@gmail.com)
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

#############################################################
# Search by block parameters and display information about
# matching blocks.
#############################################################

import os
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file
from ubireader import settings
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.utils import UBIReaderError, guess_filetype, guess_start_offset, guess_leb_size, guess_peb_size


def display_blocks(
        filepath,
        block_search_params,
        log=False,
        verbose=False,
        block_size=None,
        start_offset=None,
        end_offset=None,
        guess_offset=None,
        warn_only_block_read_errors=False,
        ignore_block_header_errors=False,
        uboot_fix=False
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

    try:
        search_params = eval(block_search_params)

        if not isinstance(search_params, dict):
            raise UBIReaderError('Search Param Error: Params must be a Dict of block PEB object items:value pairs.')

    except NameError as e:
        raise UBIReaderError('Search Param Error: Dict key block attrs must be single quoted.')

    except Exception as e:
        raise UBIReaderError('Search Param Error: %s' % e)

    ufile_obj = ubi_file(filepath, block_size, start_offset, end_offset)
    ubi_obj = ubi_base(ufile_obj)
    blocks = []

    for block in ubi_obj.blocks:
        match = True

        for key in search_params:
            b = ubi_obj.blocks[block]

            for attr in key.split('.'):
                if hasattr(b, attr):
                    b = getattr(b, attr)

            if isinstance(search_params[key], list):
                if isinstance(b, list):
                    for value in b:
                        if value in search_params[key]:
                            break
                    else:
                        match = False
                elif b not in search_params[key]:
                    match = False

            elif b != search_params[key]:
                match = False
                break

        if match:                
            blocks.append(ubi_obj.blocks[block])

    print('\nBlock matches: %s' % len(blocks))

    for block in blocks:
        print(block.display())
