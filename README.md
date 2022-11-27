# UBI Reader
UBI Reader is a Python module and collection of scripts capable of extracting
the contents of UBI and UBIFS images, along with analyzing these images to
determine the parameter settings to recreate them using the mtd-utils tools.


### Known Issues
These are some known issues, that prevent an exact data dump from occuring.

* This does not replay the journal, so uncommited data will not be retrieved. Data can be in the journal with both clean and unclean shutdowns.

* Depending on how the NAND was dumped, the data bits may not be error corrected.

* Socket files will be ignored, you can change ubireader/settings.py to have it create dummy files in their place.


## Testing Branch
The testing branch includes a tools/ directory, that has scripts to help when trying to extract data from broken images. These also serve as examples of how to use parts of ubi_reader in custom scripts.

An override system is also included, for manually setting certain parameters that may be reported wrong by the UBI/FS data.

This branch will probably remain seperate, as it is meant to be customized to aid in extracting data from problematic images. You can install it with 'python setup.py develop' to make it easier to modify ubi_reader as needed.


## Dependencies:

Since version v0.8.2, Python3 is required, with the following packages:

    $ sudo apt-get install liblzo2-dev
    $ sudo pip install python-lzo


## Installation:

Latest Version

    $ git clone https://github.com/jrspruitt/ubi_reader
    $ cd ubi_reader
    $ sudo python setup.py install

Or

    $ sudo pip install ubi_reader


## Usage:
For basic usage, the scripts need no options and if applicable will save output
to ./ubifs-root/. More advanced usage can set start and end offset, specify
an output directory, or for debugging can print out what it is doing to the
terminal.

Run program with -h or --help for explanation of options.

## Extracting File Contents:
    ubireader_extract_files [options] path/to/file

The script accepts a file with UBI or UBIFS data in it, so should work with a NAND
dump. It will search for the first occurance of UBI or UBIFS data and attempt to
extract the contents. If file includes special files, you will need to run as
root or sudo for it to create these files. With out it, it'll skip them and show a
warning that these files were not created.

## List/Copy Files:
    ubireader_list_files [options] path/to/file

The script accepts a file with UBI or UBIFS data in it, so should work with a NAND
dump. It will search for the first occurance of UBI or UBIFS data and treat it as
a UBIFS. To list files supply the path to list (-P, --path), e.g. "-P /" to list
the filesystems root directory. To copy a file from the filesystem to a local directory
supply the source path (-C, --copy) and the destination path (-D, --copy-dest),
e.g. -C /etc/passwd -D . (extract /etc/passwd from the UBIFS image and copy it to
local directory).

## Extracting Images:
    ubireader_extract_images [options] path/to/file

This script will extract the whole UBI or UBIFS image from a NAND dump, or the UBIFS
image from a UBI image. You can specify what type of image to extract by setting the
(-u, --image-type) option to "UBI" or "UBIFS". Default is "UBIFS".

## MTD-Utils Parameters:
    ubireader_utils_info [options] path/to/file

The script will analyze a UBI image and create a Linux shell script and UBI config
file that can be used for building new UBI images to the same specifications. For
just a printed list of the options and values, use the (-r, --show-only) option.

## Display Information:
    ubireader_display_info [options] path/to/file

Depending on the image type found, this script displays some UBI information along with
the header info from the layout block, including volume table records. If it is a UBIFS
image, the Super Node, and both Master Nodes are displayed. Using the (-u, --ubifs-info)
option, it will get the UBIFS info from inside a UBI file instead.

## Display Block Information:
    ubireader_display_blocks [options] "{'block.attr':?, ...}" path/to/file

Search for and display block information. This can be used for debugging failed image
and file extractions. The blocks are searched for using a double quoted Python Dict of
search paramaters, example. "{'peb_num':[0, 1] + range(100, 102), 'ec_hdr.ec': 1, 'is_valid': True}"
This will find PEBs 0, 1, 100, 101, 102, with an erase count of 1 that is a valid block.
Can use any of the parameters in ubireader.ubi.block.description.

## Options:
Some general option flags are
* -l, --log: This prints to screen actions being taken while running.
* -v, --verbose: This basically prints everything about anything happening.
* -p, --peb-size int: Specify PEB size of the UBI image, instead of having it guess.
* -e, --leb-size int: Specify LEB size of UBIFS image, instead of having it guess.
* -s, --start-offset int: Tell script to look for UBI/UBIFS data at given address.
* -n, --end-offset int: Tell script to ignore data after given address in data.
* -g, --guess-offset: Specify offset to start guessing where UBI data is in file. Useful for NAND dumps with false positives before image.
* -w, --warn-only-block-read-errors: Attempts to continue extracting files even with bad block reads. Some data will be missing or corrupted!
* -i, --ignore-block-header-errors: Forces unused and error containing blocks to be included and also displayed with log/verbose.
* -f, --u-boot-fix: Assume blocks with image_seq 0 are because of older U-boot implementations and include them. *This may cause issues with multiple UBI image files.
* -o, --output-dir path: Specify where files should be written to, instead of ubi_reader/output
