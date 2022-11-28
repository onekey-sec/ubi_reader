import argparse
import os

from ubireader import settings
from ubireader.exceptions import UBIReaderParseError
from ubireader.parsers import parser_base
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs
from ubireader.ubifs.list import list_files, copy_file
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi_io import ubi_file, leb_virtual_file
from ubireader.debug import error, log
from ubireader.utils import guess_filetype, guess_start_offset, guess_leb_size, guess_peb_size


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

    if filepath:
        path = filepath
        if not os.path.exists(path):
            raise UBIReaderParseError("File path doesn't exist.")

    if start_offset:
        start_offset = start_offset
    elif guess_offset:
        start_offset = guess_start_offset(path, guess_offset)
    else:
        start_offset = guess_start_offset(path)

    if end_offset:
        end_offset = end_offset
    else:
        end_offset = None

    filetype = guess_filetype(path, start_offset)
    if not filetype:
        raise UBIReaderParseError('Could not determine file type.')

    if block_size:
        block_size = block_size
    else:
        if filetype == UBI_EC_HDR_MAGIC:
            block_size = guess_peb_size(path)
        elif filetype == UBIFS_NODE_MAGIC:
            block_size = guess_leb_size(path)

        if not block_size:
            raise UBIReaderParseError('Block size could not be determined.')

    # Create file object.
    ufile_obj = ubi_file(path, block_size, start_offset, end_offset)

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
                    list_files(ubifs_obj, listpath)
                if copyfile and copyfiledest:
                    copy_file(ubifs_obj, copyfile, copyfiledest)

    elif filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)

        if listpath:
            list_files(ubifs_obj, listpath)
        if copyfile and copyfiledest:
            copy_file(ubifs_obj, copyfile, copyfiledest)

    else:
        print('Something went wrong to get here.')


description = 'List and Extract files of a UBI or UBIFS image.'
usage = 'ubireader_list_files [options] filepath'
parser = argparse.ArgumentParser(
    usage=usage,
    description=description,
    parents=[parser_base],
    add_help=False
)
parser.set_defaults(func=list_files)

parser.add_argument('-e', '--leb-size', type=int, dest='block_size',
                    help='Specify LEB size. (UBIFS Only)')

parser.add_argument('-P', '--path', dest='listpath',
                    help='Path to list.')

parser.add_argument('-C', '--copy', dest='copyfile',
                    help='File to Copy.')

parser.add_argument('-D', '--copy-dest', dest='copyfiledest',
                    help='Copy Destination.')
