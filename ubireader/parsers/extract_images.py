import argparse
import os

from ubireader import settings
from ubireader.exceptions import UBIReaderParseError
from ubireader.parsers import parser_base
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubi_io import ubi_file
from ubireader.debug import error, log
from ubireader.utils import guess_filetype, guess_start_offset, guess_peb_size


def create_output_dir(outpath):
    if not os.path.exists(outpath):
        try:
            os.makedirs(outpath)
            log(create_output_dir, 'Created output path: %s' % outpath)
        except Exception as e:
            error(create_output_dir, 'Fatal', '%s' % e)


def extract_images(
        filepath,
        log=False,
        verbose=False,
        block_size=None,
        image_type=None,
        start_offset=None,
        end_offset=None,
        guess_offset=None,
        warn_only_block_read_errors=False,
        ignore_block_header_errors=False,
        uboot_fix=False,
        outpath=None
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
    if filetype != UBI_EC_HDR_MAGIC:
        raise UBIReaderParseError('File does not look like UBI data.')

    img_name = os.path.basename(path)
    if outpath:
        outpath = os.path.abspath(os.path.join(outpath, img_name))
    else:
        outpath = os.path.join(settings.output_dir, img_name)

    if block_size:
        block_size = block_size
    else:
        block_size = guess_peb_size(path)

        if not block_size:
            raise UBIReaderParseError('Block size could not be determined.')

    if image_type:
        image_type = image_type.upper()
    else:
        image_type = 'UBIFS'

    # Create file object.
    ufile_obj = ubi_file(path, block_size, start_offset, end_offset)

    # Create UBI object
    ubi_obj = ubi(ufile_obj)

    # Loop through found images in file.
    for image in ubi_obj.images:
        if image_type == 'UBI':
            # Create output path and open file.
            img_outpath = os.path.join(outpath, 'img-%s.ubi' % image.image_seq)
            create_output_dir(outpath)
            f = open(img_outpath, 'wb')

            # Loop through UBI image blocks
            for block in image.get_blocks(ubi_obj.blocks):
                if ubi_obj.blocks[block].is_valid:
                    # Write block (PEB) to file
                    f.write(ubi_obj.file.read_block(ubi_obj.blocks[block]))

        elif image_type == 'UBIFS':
            # Loop through image volumes
            for volume in image.volumes:
                # Create output path and open file.
                vol_outpath = os.path.join(outpath, 'img-%s_vol-%s.ubifs' % (image.image_seq, volume))
                create_output_dir(outpath)
                f = open(vol_outpath, 'wb')

                # Loop through and write volume block data (LEB) to file.
                for block in image.volumes[volume].reader(ubi_obj):
                    f.write(block)


description = 'Extract UBI or UBIFS images from file containing UBI data in it.'
usage = 'ubireader_extract_images [options] filepath'
parser = argparse.ArgumentParser(
    usage=usage,
    description=description,
    parents=[parser_base],
    add_help=False
)
parser.set_defaults(func=extract_images)

parser.add_argument('-u', '--image-type', dest='image_type',
                    help='Specify image type to extract UBI or UBIFS. (default: UBIFS)')

parser.add_argument('-o', '--output-dir', dest='outpath',
                    help='Specify output directory path.')
