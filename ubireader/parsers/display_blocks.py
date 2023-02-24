from ubireader.parsers import ArgHandler
from ubireader.exceptions import UBIReaderParseError
from ubireader.ubi import ubi_base
from ubireader.ubi_io import ubi_file

def parse(*args, **kwargs):
    args = ArgHandler(*args, **kwargs)

    if 'block_search_params' in kwargs:
        if kwargs['block_search_params']:
            try:
                search_params = eval(kwargs['block_search_params'])

                if not isinstance(search_params, dict):
                    raise UBIReaderParseError('Search Param Error: Params must be a Dict of block PEB object items:value pairs.')

            except NameError as e:
                raise UBIReaderParseError('Search Param Error: Dict key block attrs must be single quoted.')

            except Exception as e:
                raise UBIReaderParseError('Search Param Error: %s' % e)

        else:
            raise UBIReaderParseError('No search parameters given, -b arg is required.')


    ufile_obj = ubi_file(args.filepath, args.block_size, args.start_offset, args.end_offset)
    ubi_obj = ubi_base(ufile_obj)
    blocks = []

    for block in ubi_obj.blocks:
        match = True

        for key in search_params:
            b = ubi_obj.blocks[block]

            for attr in key.split('.'):
                if hasattr(b, attr):
                    b = getattr(b, attr)

            if isinstance(search_params[key], list):
                if isinstance(b, list):
                    for value in b:
                        if value in search_params[key]:
                            break
                    else:
                        match = False
                elif b not in search_params[key]:
                    match = False

            elif b != search_params[key]:
                match = False
                break

        if match:                
            blocks.append(ubi_obj.blocks[block])

    print('\nBlock matches: %s' % len(blocks))

    for block in blocks:
        print(block.display())