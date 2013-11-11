#!/usr/bin/env python
#############################################################
# ubi_reader
# (c) 2013 Jason Pruitt (jrspruitt@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################
import time

import sys
from ubi import ubi
from ubi import sort

def print_info(ubi, num=None):
    # Roll through all Objects pretty contained information
    if num is None:
        # Print main UBI Object attributes
        ubi.display()
        print '\n'
        # Loop through images found
        for image in ubi.images:
            # Print image Object attributes
            image.display('\t')
            print '\n'
            # Loop through volumes in image.
            for volume in image.volumes:
                # Print volume attribtures and UBI headers
                image.volumes[volume].display('\t\t')

    else:
        try:
            # Print Block Object with PEB # <num>
            # If not in index, show first PEB of UBI data
            ubi.blocks[num].display()
 
        except Exception, e:
            print e
            
            print 'Block out of range, printing first UBI block'
            ubi.blocks[ubi.first_peb_num].display()
    return
    
if __name__ == '__main__':
    try:
        path = sys.argv[1]
        num = int(sys.argv[2])

    except:
        num = None
    
    if path in ['-h', '--help']:
        print '''
Usage:
    $ ubi_info.py path/to/file.ubi [block number]

    if no args, print all found information about UBI image.
    if block num provided, print block description
    block num is the PEB location of the UBI block.
        '''
        sys.exit(1)

    else:
        # You want a specific starting offset of input file
        #ubi = ubi(path, start_offset=0x06000000, block_size=131072)
        
        # You know the block size, saves a second or two
        #ubi = ubi(path, block_size=131072) 

        # Create UBI Object
        ubi = ubi(path)
        print_info(ubi, num)
        sys.exit(1)