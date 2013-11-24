# UBI Reader


UBI Reader is a program capable of reading UBI and UBIFS images.
It will provide various information about images, volumes, physical erase
blocks, along with UBIFS superblock and master nodes. It is capable of walking
the UBIFS index node, gathering associated directory entry, data and inode nodes,
ordered by inode number. Also possible is extracting the directory tree with in
with all associated files.

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
All scripts save output into the ubi_reader/output/ directory, depending on information
available to the script, names can vary from input file name to volume names or what order
the image was found.

Run program with -h or --help for explanation of options.

### UBI Images:

__ubi_extract.py__

    $ ubi_extract.py [options] /path/to/image.ubi

Extract a UBI image from file. This is useful with a NAND dump or other such binary data.
Will extract any images found, as long as they have different image_seq numbers.
It is possible to specify keyword args start_offset and end\_offset in the ubi\_file() call.


__ubi_extract_ubifs.py__

    $ ubi_extract_ubifs.py [options] /path/to/image.ubi

Extract UBIFS image from file. Like ubi_extract.py, but provides the additional step of
stripping out UBI information and saving the UBIFS image.


__ubi\_extract\_files.py__

    $ ubi_extract_files.py [options] /path/to/image.ubi

Extract contents of a UBI image, saving to output. If this is not run as root, depending
on files and types of files being extracted and their permissions, not all actions may
be taken, and you'll see a lot of warnings. To preserve all permissions and for things
such as device files run as root. Internally this creates a virtual UBIFS image to read
from. As such, it is faster to extract the UBIFS image, and use ubifs\_extract\_files.py
but this will save a step, and doesn't take up file system space.

__ubi_info.py__

    $ ubi_info.py [options] /path/to/image.ubi

With no Physical Erase Block number provided, this will print all found information about
the UBI images and volumes found in the file. If PEB Number is provided, it will print
out the header contents of that PEB. If PEB Number not found, will print the first block.


__create\_build\_script.py__

    $ create_build_script.py [options] /path/to/image.ubi

Analyze provided image and creates the .ini configuration file and a shell script that accepts
a path(s) to a folder(s) to build a similiar configured UBI image. If Image contains multiple
volumes, script will accept multiple paths. Compare to .ini file for which path corrisponds
to which input.

__ubi\_utils\_info.py__

    $ ubi_utils_info.py [options] /path/to/image.ubi

Analyze provided image, and print to console the names, option flags and values of any relevant
information for use with programs such as mkfs.ubi, ubinize, ubimkvol, ubiformat, etc. Make
sure to check with the relevant application, as some option flags are duplicates.


### UBIFS Images:
__ubifs\_extract\_files.py__

    $ ubifs_extract_files.py [options] /path/to/image.ubifs

Same as ubi\_extract\_files.py but works on UBIFS images.

__ubifs\_info.py__

    $ ubifs_info.py [options] /path/to/image.ubifs

Prints the Superblock node and Master node.

### Known Issues

* Will not create a SOCK file type, instead just saves an empty text file with its name.

* For NAND dumps and the like, this will not fix anything ECC would take care of, so some bad data
may be extracted.

* This does not replay the journal, so uncommited data will not be retrieved.

* Assumes things are in good condition and where it thinks they should be...

### TODO

* Organize, document, the usual.

