import argparse


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