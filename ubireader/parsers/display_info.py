from ubireader.parsers import ArgHandler
from ubireader.ubi import ubi
from ubireader.ubi.defines import UBI_EC_HDR_MAGIC
from ubireader.ubifs import ubifs
from ubireader.ubifs.defines import UBIFS_NODE_MAGIC
from ubireader.ubi_io import ubi_file, leb_virtual_file


def parse(filepath, *args, **kwargs):
    args = ArgHandler(filepath, *args, **kwargs)
    # Create file object.
    ufile_obj = ubi_file(args.filepath, args.block_size, args.start_offset, args.end_offset)

    if args.filetype == UBI_EC_HDR_MAGIC:
        # Create UBI object
        ubi_obj = ubi(ufile_obj)

        # Display UBI info if not UBIFS request.
        if args.image_type == 'UBI':
            print(ubi_obj.display())

        # Loop through found images in file.
        for image in ubi_obj.images:
            # Display image information if not UBIFS request.
            if args.image_type == 'UBI':
                print('%s' % image.display('\t'))

            # Loop through volumes in each image.
            for volume in image.volumes:
                # Show UBI or UBIFS info.
                if args.image_type == 'UBI':
                    # Display volume information.
                    print(image.volumes[volume].display('\t\t'))

                else:
                    # Get blocks associated with this volume.
                    vol_blocks = image.volumes[volume].get_blocks(ubi_obj.blocks)
    
                    # Skip volume if empty.
                    if not len(vol_blocks):
                        continue
    
                    # Create LEB backed virtual file with volume blocks.
                    # Necessary to prevent having to load entire UBI image
                    # into memory.
                    lebv_file = leb_virtual_file(ubi_obj, vol_blocks)
    
                    # Create UBIFS object and print info.
                    ubifs_obj = ubifs(lebv_file)
                    print(ubifs_obj.display())
                    print(ubifs_obj.superblock_node.display('\t'))
                    print(ubifs_obj.master_node.display('\t'))
                    try:
                        print(ubifs_obj.master_node2.display('\t'))
                    except:
                        print('Master Node Error only one valid node.')

    elif args.filetype == UBIFS_NODE_MAGIC:
        # Create UBIFS object
        ubifs_obj = ubifs(ufile_obj)
        print(ubifs_obj.display())
        print(ubifs_obj.superblock_node.display('\t'))
        print(ubifs_obj.master_node.display('\t'))
        try:
            print(ubifs_obj.master_node2.display('\t'))
        except:
            print('Master Node Error only one valid node.')

    else:
        print('Something went wrong to get here.')