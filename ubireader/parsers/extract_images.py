import os

from ubireader.parsers import UIParser, create_output_dir
from ubireader.ubi import ubi
from ubireader.ubi_io import ubi_file
from ubireader import settings

# Set up argparser and cli options.
ui = UIParser()
ui.description = 'Extract UBI or UBIFS images from file containing UBI data in it.'
ui.usage = 'ubireader_extract_images [options] filepath'
ui.arg_log()
ui.arg_verbose_log()
ui.arg_peb_size()
ui.arg_image_type()
ui.arg_start_offset()
ui.arg_end_offset()
ui.arg_guess_offset()
ui.arg_warn_only_block_read_errors()
ui.arg_ignore_block_header_errors()
ui.arg_u_boot_fix()
ui.arg_output_dir()
ui.arg_filepath()

def extract_images(*args, **kwargs):
    ui.parse_args(*args, **kwargs)

    img_name = os.path.basename(ui.filepath)
    if ui.output_dir:
        outpath = os.path.abspath(os.path.join(ui.output_dir, img_name))
    else:
        outpath = os.path.join(settings.output_dir, img_name)

    # Create file object.
    ufile_obj = ubi_file(ui.filepath, ui.block_size, ui.start_offset, ui.end_offset)

    # Create UBI object
    ubi_obj = ubi(ufile_obj)

    # Loop through found images in file.
    for image in ubi_obj.images:
        if ui.image_type == 'UBI':
            # Create output path and open file.
            img_outpath = os.path.join(outpath, 'img-%s.ubi' % image.image_seq)
            create_output_dir(outpath)
            f = open(img_outpath, 'wb')

            # Loop through UBI image blocks
            for block in image.get_blocks(ubi_obj.blocks):
                if ubi_obj.blocks[block].is_valid:
                    # Write block (PEB) to file
                    f.write(ubi_obj.file.read_block(ubi_obj.blocks[block]))

        elif ui.image_type == 'UBIFS':
            # Loop through image volumes
            for volume in image.volumes:
                # Create output path and open file.
                vol_outpath = os.path.join(outpath, 'img-%s_vol-%s.ubifs' % (image.image_seq, volume))
                create_output_dir(outpath)
                f = open(vol_outpath, 'wb')

                # Loop through and write volume block data (LEB) to file.
                for block in image.volumes[volume].reader(ubi_obj):
                    f.write(block)


# Add process function to parser.
ui.function = extract_images