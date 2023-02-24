import os

from ubireader.parsers import ArgHandler, makedir
from ubireader.ubi import ubi
from ubireader.ubi_io import ubi_file
from ubireader import settings


def parse(filepath, *args, **kwargs):
    args = ArgHandler(filepath, *args, **kwargs)

    img_name = os.path.basename(args.filepath)
    if args.output_dir:
        outpath = os.path.abspath(args.output_dir)
    else:
        outpath = settings.output_dir

    # Create file object.
    ufile_obj = ubi_file(args.filepath, args.block_size, args.start_offset, args.end_offset)

    # Create UBI object
    ubi_obj = ubi(ufile_obj)

    # Loop through found images in file.
    for image in ubi_obj.images:
        if args.image_type == 'UBI':
            # Create output path and open file.
            img_outpath = os.path.join(outpath, f'{img_name}-{image.image_seq}.ubi')
            makedir(outpath)
            f = open(img_outpath, 'wb')

            # Loop through UBI image blocks
            for block in image.get_blocks(ubi_obj.blocks):
                if ubi_obj.blocks[block].is_valid:
                    # Write block (PEB) to file
                    f.write(ubi_obj.file.read_block(ubi_obj.blocks[block]))

        elif args.image_type == 'UBIFS':
            # Loop through image volumes
            for volume in image.volumes:
                # Create output path and open file.
                vol_outpath = os.path.join(outpath, f'{img_name}-{image.image_seq}-{volume}.ubifs')
                makedir(outpath)
                f = open(vol_outpath, 'wb')

                # Loop through and write volume block data (LEB) to file.
                for block in image.volumes[volume].reader(ubi_obj):
                    f.write(block)