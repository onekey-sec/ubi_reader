import os
import argparse

from ubireader import settings
from ubireader.utils import guess_filetype, guess_start_offset, guess_peb_size, guess_leb_size
from ubireader.exceptions import UBIReaderParseError
from ubireader.debug import error, log
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC


class UIParser(object):
    def __init__(self):
        self._p = argparse.ArgumentParser(add_help=False)

    def get_parser(self):
        return self._p

    parser = property(fget=get_parser)

    def set_usage(self, usage):
        self._p.usage = usage

    def get_usage(self):
        return self._p.usage

    usage = property(get_usage, set_usage)


    def set_description(self, description):
        self._p.description = description

    def get_description(self):
        return self._p.description

    description = property(get_description, set_description)


    def set_function(self, func):
        self._p.set_defaults(func=func)

    function = property(fset=set_function)


    # CLI options.
    def arg_log(self):
        self._p.add_argument('-l', '--log', action='store_true', dest='log',
                            help='Print extraction information to screen.')

    def arg_verbose_log(self):
        self._p.add_argument('-v', '--verbose-log', action='store_true', dest='verbose',
                            help='Prints nearly everything about anything to screen.')

    def arg_warn_only_block_read_errors(self):
        self._p.add_argument('-w', '--warn-only-block-read-errors', action='store_true', dest='warn_only_block_read_errors',
                            help='Attempts to continue extracting files even with bad block reads. Some data will be missing or corrupted! (default: False)')

    def arg_ignore_block_header_errors(self):
        self._p.add_argument('-i', '--ignore-block-header-errors', action='store_true', dest='ignore_block_header_errors',
                            help='Forces unused and error containing blocks to be included and also displayed with log/verbose. (default: False)')

    def arg_u_boot_fix(self):
        self._p.add_argument('-f', '--u-boot-fix', action='store_true', dest='uboot_fix',
                        help='Assume blocks with image_seq 0 are because of older U-boot implementations and include them. (default: False)')

    def arg_peb_size(self):
        self._p.add_argument('-p', '--peb-size', type=int, dest='block_size',
                            help='Specify PEB size.')

    def arg_leb_size(self):
        self._p.add_argument('-e', '--leb-size', type=int, dest='block_size',
                            help='Specify LEB size.')

    def arg_start_offset(self):
        self._p.add_argument('-s', '--start-offset', type=int, dest='start_offset',
                            help='Specify offset of UBI/UBIFS data in file. (default: 0)')

    def arg_end_offset(self):
        self._p.add_argument('-n', '--end-offset', type=int, dest='end_offset',
                            help='Specify end offset of UBI/UBIFS data in file.')

    def arg_guess_offset(self):
        self._p.add_argument('-g', '--guess-offset', type=int, dest='guess_offset',
                            help='Specify offset to start guessing where UBI data is in file. (default: 0)')

    def arg_image_type(self):
        self._p.add_argument('-u', '--image-type', dest='image_type',
                        help='Specify image type to extract UBI or UBIFS. (default: UBIFS)')

    def arg_keep_permissions(self):
        self._p.add_argument('-k', '--keep-permissions', action='store_true', dest='permissions',
                        help='Maintain file permissions, requires running as root. (default: False)')

    def arg_output_dir(self):
        self._p.add_argument('-o', '--output-dir', dest='output_dir',
                        help='Specify output directory path.')

    def arg_filepath(self):
        self._p.add_argument('filepath', help='UBI/UBIFS image file.')

    def arg_image_type(self):
        self._p.add_argument('-u', '--image-type', dest='image_type',
                        help='Specify image type to extract UBI or UBIFS. (default: UBIFS)')

# Processing variables.
    def get_output_dir(self):
        return self._output_dir

    output_dir = property(get_output_dir)

    def get_block_size(self):
        return self._block_size

    block_size = property(get_block_size)

    def get_start_offset(self):
        return self._start_offset

    start_offset = property(get_start_offset)

    def get_end_offset(self):
        return self._end_offset

    end_offset = property(get_end_offset)

    def get_permissions(self):
        return self._permissions

    permissions = property(get_permissions)

    def get_filepath(self):
        return self._filepath

    filepath = property(get_filepath)

    def get_filetype(self):
        return self._filetype

    filetype = property(get_filetype)

    def get_image_type(self):
        return self._image_type

    image_type = property(get_image_type)

    def parse_args(self, *args, **kwargs):
        settings.logging_on = kwargs['log']
        settings.logging_on_verbose = kwargs['verbose']
        settings.warn_only_block_read_errors = kwargs['warn_only_block_read_errors']
        settings.ignore_block_header_errors = kwargs['ignore_block_header_errors']
        settings.uboot_fix = kwargs['uboot_fix']

        self._filepath = kwargs['filepath']
        if not os.path.exists(self.filepath):
            raise UBIReaderParseError("File path doesn't exist.")

        if kwargs['start_offset']:
            self._start_offset = kwargs['start_offset']
        
        if kwargs['guess_offset']:
            self._start_offset = guess_start_offset(self.filepath, kwargs['guess_offset'])

        else:
            self._start_offset = guess_start_offset(self.filepath)

        self._end_offset = kwargs['end_offset']


        self._filetype = guess_filetype(self.filepath, self.start_offset)
        if self.filetype not in [UBI_EC_HDR_MAGIC, UBIFS_NODE_MAGIC]:
            raise UBIReaderParseError('Could not determine file type.')

        if kwargs['block_size']:
            self._block_size = kwargs['block_size']
        else:
            if self.filetype == UBI_EC_HDR_MAGIC:
                self._block_size = guess_peb_size(self.filepath)

            elif self.filetype == UBIFS_NODE_MAGIC:
                self._block_size = guess_leb_size(self.filepath)

            if not self.block_size:
                raise UBIReaderParseError('PEB size could not be determined.')

        if 'image_type' in kwargs:
            if kwargs['image_type']:
                self._image_type = kwargs['image_type'].upper()
            else:
                self._image_type = 'UBIFS'

            if self._image_type not in ['UBI', 'UBIFS']:
                raise UBIReaderParseError('Image type must be UBI or UBIFS.')

        if 'output_dir' in kwargs:
            if kwargs['output_dir']:
                self._output_dir = kwargs['output_dir']
            else:
                self._output_dir = settings.output_dir

        if 'permissions' in kwargs:
            self._permissions = kwargs['permissions']

def create_output_dir(outpath):
    if not os.path.exists(outpath):
        try:
            os.makedirs(outpath)
            log(create_output_dir, 'Created output path: %s' % outpath)
        except Exception as e:
            error(create_output_dir, 'Fatal', '%s' % e)