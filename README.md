# UBI Reader


UBI Reader is a Python module and collection of scripts capable of extracting
the contents of UBI and UBIFS images, along with analyzing these images to
determine the parameter settings to recreate them using the mtd-utils tools.

## Install:

Python is required.

python-lzo is the only non-standard module, possibly included in your disto repo, if not.

    $ sudo apt-get install liblzo2-dev

    If its available in your repos.
    $ sudo apt-get install python-lzo

    Else
    $ git clone https://github.com/jd-boyd/python-lzo.git
    $ cd python-lzo
    $ python setup.py install


## Usage:
For basic usage, the scripts need no options and if applicable will save output
to ubi_reader/output/. More advanced usage can set start and end offset, specify
an output directory, or for debugging can print out what it is doing to the
terminal.

Run program with -h or --help for explanation of options.

## Extracting File Contents:
    ./extract_files.py [options] path/to/file

The script accepts a file with UBI or UBIFS data in it, so should work with a NAND
dump. It will search for the first occurance of UBI or UBIFS data and attempt to
extract the contents. If file includes special files, you will may need to run as
fakeroot and set the (-k, --keep-permissions) option, for it to create these files.
With out it, it'll skip them and show a warning that these files were not created.

## Extracting Images:
    ./extract_images.py [options] path/to/file

This script will extract the whole UBI or UBIFS image from a NAND dump, or the UBIFS
image from a UBI image. You can specify what type of image to extract by setting the
(-u, --image-type) option to "UBI" or "UBIFS". Default is "UBIFS".

## MTD-Utils Parameters:
    ./ubi_utils_info.py [options] path/to/file

The script will analyze a UBI image and create a Linux shell script and UBI config
file that can be used for building new UBI images to the same specifications. For
just a printed list of the options and values, use the (-r, --show-only) option.

## Display Information:
    ./display_info.py [options] path/to/file

Depending on the image type found, this script displays some UBI information along with
the header info from the layout block, including volume table records. If it is a UBIFS
image, the Super Node, and both Master Nodes are displayed. Using the (-u, --ubifs-info)
option, it will get the UBIFS info from inside a UBI file instead.

## Options:
Some general option flags are
* -l, --log: This prints to screen actions being taken while running.
* -v, --verbose: This basically prints everything about anything happening.
* -p, --peb-size int: Specify PEB size of the UBI image, instead of having it guess.
* -e, --leb-size int: Specify LEB size of UBIFS image, instead of having it guess.
* -s, --start-offset int: Tell script to start looking for UBI/UBIFS data at given address.
* -n, --end-offset int: Tell script to ignore data after given address in data.
* -o, --output-dir path: Specify where files should be written to, instead of ubi_reader/output


### Known Issues

* Socket files will be ignored, you can change modules/settings.py to have it created dummy files in their place.

* For NAND dumps and the like, this will not fix anything ECC would take care of, so some bad data
may be extracted.

* This does not replay the journal, so uncommited data will not be retrieved.

* Assumes things are in good condition and where it thinks they should be...

### TODO

* Organize, document, the usual.

* Arbitrary block analyzer script.

