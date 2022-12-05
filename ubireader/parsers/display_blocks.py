from ubireader.parsers import UIParser
from ubireader.exceptions import UBIReaderParseError
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file

# Set up argparser and cli options.
ui = UIParser()
ui.description = 'Search for specified blocks and display information.'
ui.usage = """
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


ui.parser.add_argument('block_search_params',
                        help="""
                        Double quoted Dict of ubi.block.description attributes, which is run through eval().
                        Ex. "{\'peb_num\':[0, 1], \'ec_hdr.ec\': 1, \'is_valid\': True}"
                        """)

ui.arg_log()
ui.arg_verbose_log()
ui.arg_peb_size()
ui.arg_leb_size()
ui.arg_start_offset()
ui.arg_end_offset()
ui.arg_guess_offset()
ui.arg_warn_only_block_read_errors()
ui.arg_ignore_block_header_errors()
ui.arg_u_boot_fix()
ui.arg_output_dir()
ui.arg_filepath()


def display_blocks(*args, **kwargs):
    ui.parse_args(*args, **kwargs)
    if 'block_search_params' in kwargs:
        if kwargs['block_search_params']:
            try:
                search_params = eval(kwargs['block_search_params'])

                if not isinstance(search_params, dict):
                    raise UBIReaderParseError('Search Param Error: Params must be a Dict of block PEB object items:value pairs.')

            except NameError as e:
                raise UBIReaderParseError('Search Param Error: Dict key block attrs must be single quoted.')

            except Exception as e:
                raise UBIReaderParseError('Search Param Error: %s' % e)

        else:
            raise UBIReaderParseError('No search parameters given, -b arg is required.')


    ufile_obj = ubi_file(ui.filepath, ui.block_size, ui.start_offset, ui.end_offset)
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


ui.function=display_blocks