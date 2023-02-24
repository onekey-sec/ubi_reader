import os

from ubireader import settings
from ubireader.utils import guess_filetype, guess_start_offset, guess_peb_size, guess_leb_size
from ubireader.exceptions import UBIReaderParseError
from ubireader.debug import error, log
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC

class ArgHandler():
    # Processing variables.

    def __init__(self, filepath, *args, **kwargs):
        settings.logging_on = kwargs['log']
        settings.logging_on_verbose = kwargs['verbose']
        settings.warn_only_block_read_errors = kwargs['warn_only_block_read_errors']
        settings.ignore_block_header_errors = kwargs['ignore_block_header_errors']
        settings.uboot_fix = kwargs['uboot_fix']

        self._filepath = filepath
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
                raise UBIReaderParseError('PEB/LEB size could not be determined.')

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

    @property
    def output_dir(self):
        return self._output_dir

    @property
    def block_size(self):
        return self._block_size

    @property
    def start_offset(self):
        return self._start_offset

    @property
    def end_offset(self):
        return self._end_offset

    @property
    def permissions(self):
        return self._permissions

    @property
    def filepath(self):
        return self._filepath

    @property
    def filetype(self):
        return self._filetype

    @property
    def image_type(self):
        return self._image_type

def makedir(outpath, overwrite=True):
    if os.path.exists(outpath):
        if os.listdir(outpath) and not overwrite:
            error(makedir, 'Fatal', 'Output directory is not empty. %s' % outpath)
    else:
        try:
            os.makedirs(outpath, exist_ok=overwrite)
            log(makedir, 'Created output path: %s' % outpath)
        except Exception as e:
            error(makedir, 'Fatal', '%s' % e)