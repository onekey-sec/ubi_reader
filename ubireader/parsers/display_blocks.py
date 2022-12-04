import argparse
import os

from ubireader.exceptions import UBIReaderParseError
from ubireader.parsers import parser_base
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file
from ubireader import settings
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.utils import guess_filetype, guess_start_offset, guess_leb_size, guess_peb_size


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

    if filepath:
        path = filepath
        if not os.path.exists(path):
            raise UBIReaderParseError("File path doesn't exist.")
    else:
        raise UBIReaderParseError('File path must be provided.')

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

    if block_search_params:
        try:
            search_params = eval(block_search_params)

            if not isinstance(search_params, dict):
                raise UBIReaderParseError('Search Param Error: Params must be a Dict of block PEB object items:value pairs.')

        except NameError as e:
            raise UBIReaderParseError('Search Param Error: Dict key block attrs must be single quoted.')

        except Exception as e:
            raise UBIReaderParseError('Search Param Error: %s' % e)

    else:
        raise UBIReaderParseError('No search parameters given, -b arg is required.')


    ufile_obj = ubi_file(path, block_size, start_offset, end_offset)
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


description = 'Search for specified blocks and display information.'
usage = """
ubireader display-blocks "{'block.attr': value,...}" path/to/image
    Search for blocks by given parameters and display information about them.
    This is block only, no volume or image information is created, which can
    be used to debug file and image extraction.
Example:
    "{'peb_num':[0, 1] + range(100, 102), 'ec_hdr.ec': 1, 'is_valid': True}"
    This matches block.peb_num 0, 1, 100, 101, and 102 
    with a block.ec_hdr.ec (erase count) of 1, that are valid PEB blocks.
    For a full list of parameters check ubireader.ubi.block.description.
"""
parser = argparse.ArgumentParser(
    usage=usage,
    description=description,
    parents=[parser_base],
    add_help=False
)
parser.set_defaults(func=display_blocks)

parser.add_argument('-e', '--leb-size', type=int, dest='block_size',
                    help='Specify LEB size. (UBIFS Only)')

parser.add_argument('block_search_params',
                    help="""
                    Double quoted Dict of ubi.block.description attributes, which is run through eval().
                    Ex. "{\'peb_num\':[0, 1], \'ec_hdr.ec\': 1, \'is_valid\': True}"
                    """)
