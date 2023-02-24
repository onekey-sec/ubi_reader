import sys
import inspect
import argparse

import ubireader.ui.scripts
from ubireader.exceptions import UBIReaderParseError

def main():
    parser = argparse.ArgumentParser(description='UBI and UBIFS tools.')
    subparsers = parser.add_subparsers()

    for name, obj in inspect.getmembers(sys.modules[ubireader.ui.scripts.__name__]):
        if inspect.isclass(obj) and name.endswith('Ui'):
            subp = obj()
            subparsers.add_parser(
                subp.cmd,
                usage=subp.usage,
                description=subp.description,
                parents=[subp.parser]
            )

    args = vars(parser.parse_args())
    print(args)
    func = args.pop('func')
    filepath = args.pop('filepath')
    try:
        func(filepath, **args)
    except UBIReaderParseError as e:
        sys.exit("Error: " + str(e))


if __name__ == "__main__":
    main()
