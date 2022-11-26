import argparse
import sys

from ubireader.scripts.display_blocks import display_blocks
from ubireader.scripts.display_info import display_info
from ubireader.scripts.extract_files import extract_files
from ubireader.scripts.extract_images import extract_images
from ubireader.scripts.list_files import list_files
from ubireader.scripts.utils_info import utils_info


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()  # 'required' argument is 3.7+

    # Common options

    parser_base = argparse.ArgumentParser(add_help=False)

    parser_base.add_argument('filepath', help='UBI/UBIFS image file.')

    parser_base.add_argument('-l', '--log', action='store_true', dest='log',
                      help='Print extraction information to screen.')
    
    parser_base.add_argument('-v', '--verbose-log', action='store_true', dest='verbose',
                      help='Prints nearly everything about anything to screen.')
    
    parser_base.add_argument('-p', '--peb-size', type=int, dest='block_size',
                        help='Specify PEB size.')

    parser_base.add_argument('-s', '--start-offset', type=int, dest='start_offset',
                        help='Specify offset of UBI/UBIFS data in file. (default: 0)')

    parser_base.add_argument('-n', '--end-offset', type=int, dest='end_offset',
                        help='Specify end offset of UBI/UBIFS data in file.')

    parser_base.add_argument('-g', '--guess-offset', type=int, dest='guess_offset',
                        help='Specify offset to start guessing where UBI data is in file. (default: 0)')

    parser_base.add_argument('-w', '--warn-only-block-read-errors', action='store_true', dest='warn_only_block_read_errors',
                      help='Attempts to continue extracting files even with bad block reads. Some data will be missing or corrupted! (default: False)')

    parser_base.add_argument('-i', '--ignore-block-header-errors', action='store_true', dest='ignore_block_header_errors',
                      help='Forces unused and error containing blocks to be included and also displayed with log/verbose. (default: False)')

    parser_base.add_argument('-f', '--u-boot-fix', action='store_true', dest='uboot_fix',
                      help='Assume blocks with image_seq 0 are because of older U-boot implementations and include them. (default: False)')

    # display_blocks

    usage_db = """
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
    parser_db = subparsers.add_parser(
        "display-blocks",
        usage=usage_db,
        description='Search for specified blocks and display information.',
        parents=[parser_base]
    )
    parser_db.set_defaults(func=display_blocks)

    parser_db.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size. (UBIFS Only)')

    parser_db.add_argument('block_search_params',
                      help="""
                      Double quoted Dict of ubi.block.description attributes, which is run through eval().
                      Ex. "{\'peb_num\':[0, 1], \'ec_hdr.ec\': 1, \'is_valid\': True}"
                      """)

    # display_info

    parser_di = subparsers.add_parser(
        "display-info",
        usage='ubireader display-info [options] filepath',
        description='Show information about UBI or UBIFS image.',
        parents=[parser_base]
    )
    parser_di.set_defaults(func=display_info)

    parser_di.add_argument('-u', '--ubifs-info', action='store_true', dest='ubifs_info',
                      help='Get UBIFS information from inside a UBI image. (default: false)')
    
    parser_di.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size. (UBIFS Only)')

    # extract_files

    parser_ef = subparsers.add_parser(
        "extract-files",
        usage='ubireader extract-files [options] filepath',
        description='Extract contents of a UBI or UBIFS image.',
        parents=[parser_base]
    )
    parser_ef.set_defaults(func=extract_files)

    parser_ef.add_argument('-k', '--keep-permissions', action='store_true', dest='permissions',
                      help='Maintain file permissions, requires running as root. (default: False)')

    parser_ef.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size. (UBIFS Only)')

    parser_ef.add_argument('-o', '--output-dir', dest='outpath',
                        help='Specify output directory path.')

    # extract_images

    parser_ei = subparsers.add_parser(
        "extract-images",
        usage='ubireader extract-images [options] filepath',
        description='Extract UBI or UBIFS images from file containing UBI data in it.',
        parents=[parser_base]
    )
    parser_ei.set_defaults(func=extract_images)

    parser_ei.add_argument('-u', '--image-type', dest='image_type',
                        help='Specify image type to extract UBI or UBIFS. (default: UBIFS)')

    parser_ei.add_argument('-o', '--output-dir', dest='outpath',
                        help='Specify output directory path.')

    # list_files

    parser_lf = subparsers.add_parser(
        "list-files",
        usage='ubireader list-files [options] filepath',
        description='List and Extract files of a UBI or UBIFS image.',
        parents=[parser_base]
    )
    parser_lf.set_defaults(func=list_files)

    parser_lf.add_argument('-e', '--leb-size', type=int, dest='block_size',
                        help='Specify LEB size. (UBIFS Only)')

    parser_lf.add_argument('-P', '--path', dest='listpath',
                        help='Path to list.')

    parser_lf.add_argument('-C', '--copy', dest='copyfile',
                        help='File to Copy.')

    parser_lf.add_argument('-D', '--copy-dest', dest='copyfiledest',
                        help='Copy Destination.')

    # utils_info

    parser_ui = subparsers.add_parser(
        "utils-info",
        usage='ubireader utils-info [options] filepath',
        description='Determine settings for recreating UBI image.',
        parents=[parser_base]
    )
    parser_ui.set_defaults(func=utils_info)

    parser_ui.add_argument('-r', '--show-only', action='store_true', dest='show_only',
                      help='Print parameters to screen only. (default: false)')
    
    parser_ui.add_argument('-o', '--output-dir', dest='outpath',
                        help='Specify output directory path.')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = vars(parser.parse_args())
    func = args.pop("func")
    func(**args)


if __name__ == "__main__":
    main()