#!/usr/bin/env python
#############################################################
# ubi_reader/ubifs
# (C) Collin Mulliner based on Jason Pruitt's output.py

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

from __future__ import annotations
import os
from pathlib import PurePath
import time
from typing import TYPE_CHECKING
from ubireader.ubifs.decrypt import decrypt_symlink_target
from ubireader.ubifs.defines import *
from ubireader.ubifs import walk
from ubireader.ubifs.misc import process_reg_file
from ubireader.debug import error

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ubireader.ubifs import ubifs as Ubifs, nodes
    from ubireader.ubifs.walk import Inode

def list_files(ubifs: Ubifs, list_path: PurePath | str, *, recursive: bool = False) -> None:
    list_path = PurePath(list_path)
    pnames = [part for part in list_path.parts if part != '/']
    try:
        inodes: dict[int, Inode] = {}
        bad_blocks: list[int] = []

        walk.index(ubifs, ubifs.master_node.root_lnum, ubifs.master_node.root_offs, inodes, bad_blocks)

        if len(inodes) < 2:
            raise Exception('No inodes found')

        inum = find_dir(inodes, 1, pnames, 0)

        if inum == None:
            return

        if not 'dent' in inodes[inum]:
            return

        for dent in inodes[inum]['dent']:
            if recursive:
                print_dent_recursive(ubifs, inodes, dent, longts=False, dent_path=list_path / dent.name)
            else:
                print_dent(ubifs, inodes, dent, longts=False, dent_path=None)
        
        if len(bad_blocks):
            error(list_files, 'Warn', 'Data may be missing or corrupted, bad blocks, LEB [%s]' % ','.join(map(str, bad_blocks)))

    except Exception as e:
        error(list_files, 'Error', '%s' % e)


def copy_file(ubifs: Ubifs, filepath: str, destpath: str) -> bool:
    pathnames = filepath.split("/")
    pnames: list[str] = []
    for i in pathnames:
        if len(i) > 0:
            pnames.append(i)

    filename = pnames[len(pnames)-1]
    del pnames[-1]

    inodes: dict[int, Inode] = {}
    bad_blocks: list[int] = []

    walk.index(ubifs, ubifs.master_node.root_lnum, ubifs.master_node.root_offs, inodes, bad_blocks)

    if len(inodes) < 2:
        return False

    inum = find_dir(inodes, 1, pnames, 0)

    if inum == None:
        return False

    if not 'dent' in inodes[inum]:
        return False

    for dent in inodes[inum]['dent']:
        if dent.name == filename:
            filedata = process_reg_file(ubifs, inodes[dent.inum], filepath, inodes)
            if os.path.isdir(destpath):
                destpath = os.path.join(destpath, filename)
            with open(destpath, 'wb') as f:
                f.write(filedata)
            return True
    return False


def find_dir(inodes: Mapping[int, Inode], inum: int, names: list[str], idx: int) -> int | None:
    if len(names) == 0:
        return 1
    for dent in inodes[inum]['dent']:
        if dent.name == names[idx]:
            if len(names) == idx+1:
                return dent.inum
            else:
                return find_dir(inodes, dent.inum, names, idx+1)
    return None


def print_dent_recursive(
    ubifs: Ubifs,
    inodes: Mapping[int, Inode],
    dent_node: nodes.dent_node,
    long: bool,
    longts: bool,
    *,
    dent_path: PurePath,
) -> None:
    inode = inodes[dent_node.inum]

    print_dent(ubifs, inodes, dent_node, long=long, longts=longts, dent_path=dent_path)

    if dent_node.type != UBIFS_ITYPE_DIR:
        return

    for dnode in inode.get('dent', []):
        print_dent_recursive(ubifs, inodes, dnode, long=long, longts=longts, dent_path=dent_path / dnode.name)


def print_dent(
    ubifs: Ubifs,
    inodes: Mapping[int, Inode],
    dent_node: nodes.dent_node,
    long: bool = True,
    longts: bool = False,
    *,
    # Path of the directory entry
    dent_path: PurePath | None = None,
) -> None:
    inode = inodes[dent_node.inum]
    # Display the full path if path is set, otherwise just the name.
    display_path = str(dent_path) if dent_path is not None else dent_node.name

    if long:
        fl = file_leng(ubifs, inode)

        lnk = ""
        if dent_node.type == UBIFS_ITYPE_LNK:
            lnk = " -> " + decrypt_symlink_target(ubifs, inodes, dent_node)

        if longts:
            mtime = inode['ino'].mtime_sec
        else:
            mtime = time.strftime("%b %d %H:%M", time.gmtime(inode['ino'].mtime_sec))

        print('%6o %2d %s %s %7d %s %s%s' % (inode['ino'].mode, inode['ino'].nlink, inode['ino'].uid, inode['ino'].gid, fl, mtime, display_path, lnk))
    else:
        print(display_path)


def file_leng(ubifs: Ubifs, inode: Inode) -> int:
    fl = 0
    if 'data' in inode:
        compr_type = 0
        sorted_data = sorted(inode['data'], key=lambda x: x.key['khash'])
        last_khash = sorted_data[0].key['khash']-1

        for data in sorted_data:
            if data.key['khash'] - last_khash != 1:
                while 1 != (data.key['khash'] - last_khash):
                    last_khash += 1
                    fl = fl + UBIFS_BLOCK_SIZE
            fl = fl + data.size
        return fl
    return 0
