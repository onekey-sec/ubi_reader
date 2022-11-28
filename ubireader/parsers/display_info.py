import argparse
import os

from ubireader import settings
from ubireader.exceptions import UBIReaderParseError
from ubireader.parsers import parser_base
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.utils import guess_filetype, guess_start_offset, guess_leb_size, guess_peb_size
from ubireader.ubi_io import ubi_file, leb_virtual_file


def display_info(
        filepath,
        log=False,
        verbose=False,
        ubifs_info=False,
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

    ubifs_info = ubifs_info

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

        # Display UBI info if not UBIFS request.
        if not ubifs_info:
            print(ubi_obj.display())

        # Loop through found images in file.
        for image in ubi_obj.images:
            # Display image information if not UBIFS request.
            if not ubifs_info:
                print('%s' % image.display('\t'))

            # Loop through volumes in each image.
            for volume in image.volumes:
                # Show UBI or UBIFS info.
                if not ubifs_info:

                    # Display volume information.
                    print(image.volumes[volume].display('\t\t'))

                else:
                    # Get blocks associated with this volume.
                    vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)
    
                    # Skip volume if empty.
                    if not len(vol_blocks):
                        continue
    
                    # Create LEB backed virtual file with volume blocks.
                    # Necessary to prevent having to load entire UBI image
                    # into memory.
                    lebv_file = leb_virtual_file(ubi_obj, vol_blocks)
    
                    # Create UBIFS object and print info.
                    ubifs_obj = ubifs(lebv_file)
                    print(ubifs_obj.display())
                    print(ubifs_obj.superblock_node.display('\t'))
                    print(ubifs_obj.master_node.display('\t'))
                    try:
                        print(ubifs_obj.master_node2.display('\t'))
                    except:
                        print('Master Node Error only one valid node.')

    elif filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)
        print(ubifs_obj.display())
        print(ubifs_obj.superblock_node.display('\t'))
        print(ubifs_obj.master_node.display('\t'))
        try:
            print(ubifs_obj.master_node2.display('\t'))
        except:
            print('Master Node Error only one valid node.')

    else:
        print('Something went wrong to get here.')


description = 'Show information about UBI or UBIFS image.'
usage = 'ubireader_display_info [options] filepath'
parser = argparse.ArgumentParser(
    usage=usage,
    description=description,
    parents=[parser_base],
    add_help=False
)
parser.set_defaults(func=display_info)

parser.add_argument('-u', '--ubifs-info', action='store_true', dest='ubifs_info',
                    help='Get UBIFS information from inside a UBI image. (default: false)')

parser.add_argument('-e', '--leb-size', type=int, dest='block_size',
                    help='Specify LEB size. (UBIFS Only)')
