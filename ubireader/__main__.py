import argparse
import sys

from ubireader.exceptions import UBIReaderParseError
from ubireader.parsers import display_blocks, display_info, extract_files, extract_images, list_files, utils_info


def main():
    parser = argparse.ArgumentParser(description='Extract files from UBI and UBIFS images.')
    subparsers = parser.add_subparsers()
    subparsers.add_parser(
        "display-blocks",
        usage=display_blocks.usage,
        description=display_blocks.description,
        parents=[display_blocks.parser]
    )
    subparsers.add_parser(
        "display-info",
        usage=display_info.usage,
        description=display_info.description,
        parents=[display_info.parser]
    )
    subparsers.add_parser(
        "extract-files",
        usage=extract_files.usage,
        description=extract_files.description,
        parents=[extract_files.parser]
    )
    subparsers.add_parser(
        "extract-images",
        usage=extract_images.usage,
        description=extract_images.description,
        parents=[extract_images.parser]
    )
    subparsers.add_parser(
        "list-files",
        usage=list_files.usage,
        description=list_files.description,
        parents=[list_files.parser]
    )
    subparsers.add_parser(
        "utils-info",
        usage=utils_info.usage,
        description=utils_info.description,
        parents=[utils_info.parser]
    )

    args = vars(parser.parse_args())
    func = args.pop("func")
    try:
        func(**args)
    except UBIReaderParseError as e:
        sys.exit("Error: " + str(e))


if __name__ == "__main__":
    main()
