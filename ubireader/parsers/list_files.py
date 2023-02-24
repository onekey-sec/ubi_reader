from ubireader.parsers import ArgHandler
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs
from ubireader.ubifs.list import list_files, copy_file
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi_io import ubi_file, leb_virtual_file

def parse(filepath, *args, **kwargs):
    args = ArgHandler(filepath, *args, **kwargs)

    copyfile = False
    if 'copyfile' in kwargs:
        copyfile = kwargs['copyfile']

    copyfiledest = None
    if 'copyfiledest' in kwargs:
        copyfiledest = kwargs['copyfiledest']

    listpath = None
    if 'listpath' in kwargs:
        listpath = kwargs['listpath']

    # Create file object.
    ufile_obj = ubi_file(args.path, args.block_size, args.start_offset, args.end_offset)

    if args.filetype == UBI_EC_HDR_MAGIC:
        # Create UBI object
        ubi_obj = ubi(ufile_obj)

        # Loop through found images in file.
        for image in ubi_obj.images:

            # Loop through volumes in each image.
            for volume in image.volumes:

                # Get blocks associated with this volume.
                vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)

                # Skip volume if empty.
                if not len(vol_blocks):
                    continue

                # Create LEB backed virtual file with volume blocks.
                # Necessary to prevent having to load entire UBI image
                # into memory.
                lebv_file = leb_virtual_file(ubi_obj, vol_blocks)

                # Create UBIFS object.
                ubifs_obj = ubifs(lebv_file)

                if listpath:
                    list_files(ubifs_obj, listpath)
                if copyfile and copyfiledest:
                    copy_file(ubifs_obj, copyfile, copyfiledest)

    elif args.filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)

        if listpath:
            list_files(ubifs_obj, listpath)

        if copyfile and copyfiledest:
            copy_file(ubifs_obj, copyfile, copyfiledest)

    else:
        print('Something went wrong to get here.')