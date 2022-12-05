import os

from ubireader.parsers import UIParser, create_output_dir
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs
from ubireader.ubifs.output import extract_files as _extract_files
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi_io import ubi_file, leb_virtual_file

# Set up argparser and cli options.
ui = UIParser()
ui.description = 'Extract contents of a UBI or UBIFS image.'
ui.usage = 'ubireader_extract_files [options] filepath'
ui.arg_keep_permissions()
ui.arg_log()
ui.arg_verbose_log()
ui.arg_peb_size()
ui.arg_start_offset()
ui.arg_end_offset()
ui.arg_guess_offset()
ui.arg_warn_only_block_read_errors()
ui.arg_ignore_block_header_errors()
ui.arg_u_boot_fix()
ui.arg_output_dir()
ui.arg_filepath()

# Process file.
def extract_files(*args, **kwargs):
    ui.parse_args(*args, **kwargs)

    # Create file object.
    ufile_obj = ubi_file(ui.filepath, ui.block_size, ui.start_offset, ui.end_offset)

    if ui.filetype == UBI_EC_HDR_MAGIC:
        # Create UBI object
        ubi_obj = ubi(ufile_obj)

        # Loop through found images in file.
        for image in ubi_obj.images:

            # Create path for specific image
            # In case multiple images in data
            img_outpath = os.path.join(ui.output_dir, '%s' % image.image_seq)

            # Loop through volumes in each image.
            for volume in image.volumes:

                # Get blocks associated with this volume.
                vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)

                # Create volume data output path.
                vol_outpath = os.path.join(img_outpath, volume)
                
                # Create volume output path directory.
                create_output_dir(vol_outpath)

                # Skip volume if empty.
                if not len(vol_blocks):
                    continue

                # Create LEB backed virtual file with volume blocks.
                # Necessary to prevent having to load entire UBI image
                # into memory.
                lebv_file = leb_virtual_file(ubi_obj, vol_blocks)

                # Extract files from UBI image.
                ubifs_obj = ubifs(lebv_file)
                print('Extracting files to: %s' % vol_outpath)
                _extract_files(ubifs_obj, vol_outpath, ui.permissions)


    elif ui.filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)

        # Create directory for files.
        create_output_dir(ui.output_dir)

        # Extract files from UBIFS image.
        print('Extracting files to: %s' % ui.output_dir)
        _extract_files(ubifs_obj, ui.output_dir, ui.permissions)

    else:
        print('Something went wrong to get here.')


# Add process function to parser.
ui.function = extract_files