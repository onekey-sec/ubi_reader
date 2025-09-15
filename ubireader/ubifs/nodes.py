#!/usr/bin/env python
#############################################################
# ubi_reader/ubifs
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

from __future__ import annotations
from typing import TYPE_CHECKING, Any
from ubireader.ubifs.misc import parse_key
from ubireader.ubifs.defines import *
from ubireader.ubifs import display

if TYPE_CHECKING:
    from collections.abc import Iterator
    from ubireader.ubifs.misc import ParsedKey

class common_hdr(object):
    """Get common header at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.

    See ubifs/defines.py for object attributes.
    """
    errors: list[str]

    magic: int
    crc: int
    sqnum: int
    len: int
    node_type: int
    group_type: int
    padding: bytes

    def __init__(self, buf: bytes) -> None:

        fields = dict(list(zip(UBIFS_COMMON_HDR_FIELDS, struct.unpack(UBIFS_COMMON_HDR_FORMAT, buf))))
        for key in fields:
            setattr(self, key, fields[key])

        setattr(self, 'errors', [])
        
    def __repr__(self) -> str:
        return 'UBIFS Common Header'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.common_hdr(self, tab)


class ino_node(object):
    """Get inode node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.

    See ubifs/defines.py for object attributes.
    """
    data: bytes
    errors: list[str]

    key: ParsedKey
    creat_sqnum: int
    size: int
    atime_sec: int
    ctime_sec: int
    mtime_sec: int
    atime_nsec: int
    ctime_nsec: int
    mtime_nsec: int
    nlink: int
    uid: int
    gid: int
    mode: int
    flags: int
    data_len: int
    xattr_cnt: int
    xattr_size: int
    padding1: bytes
    xattr_names: int
    compr_type: int
    padding2: bytes

    def __init__(self, buf: bytes) -> None:

        fields = dict(list(zip(UBIFS_INO_NODE_FIELDS, struct.unpack(UBIFS_INO_NODE_FORMAT, buf[0:UBIFS_INO_NODE_SZ]))))
        for key in fields:
            if key == 'key':
                setattr(self, key, parse_key(fields[key]))
            else:
                setattr(self, key, fields[key])

        setattr(self, 'data', buf[UBIFS_INO_NODE_SZ:])
        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Ino Node'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.ino_node(self, tab)

class xent_node(object):
    """Get xattr entry node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.

    See ubifs/defines.py for object attributes.
    """
    name: str
    error: list[str]

    key: ParsedKey
    inum: int
    padding1: int
    type: int
    nlen: int
    cookie: int

    def __init__(self, buf: bytes) -> None:
        fields = dict(zip(UBIFS_XENT_NODE_FIELDS, struct.unpack(UBIFS_XENT_NODE_FORMAT, buf[0:UBIFS_XENT_NODE_SZ])))
        for key in fields:
            if key == 'key':
                setattr(self, key, parse_key(fields[key]))
            else:
                setattr(self, key, fields[key])
        setattr(self, 'name', buf[-self.nlen-1:-1].decode())
        setattr(self, 'errors', [])

    def __repr__(self):
        return 'UBIFS XATTR Entry Node'

    def __iter__(self):
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.dent_node(self, tab)

class dent_node(object):
    """Get dir entry node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.

    See ubifs/defines.py for object attributes.
    """
    raw_name: bytes
    name: str
    errors: list[str]

    key: ParsedKey
    inum: int
    padding1: int
    type: int
    nlen: int
    cookie: int

    def __init__(self, buf: bytes) -> None:
        fields = dict(list(zip(UBIFS_DENT_NODE_FIELDS, struct.unpack(UBIFS_DENT_NODE_FORMAT, buf[0:UBIFS_DENT_NODE_SZ]))))
        for key in fields:
            if key == 'key':
                setattr(self, key, parse_key(fields[key]))
            else:
                setattr(self, key, fields[key])
        setattr(self, 'raw_name', buf[-self.nlen-1:-1])
        setattr(self, 'name', "")
        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Directory Entry Node'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.dent_node(self, tab)


class data_node(object):
    """Get data node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.
    Int:offset  -- Offset in LEB of data node.

    See ubifs/defines.py for object attributes.
    """
    offset: int
    compr_len: int
    errors: list[str]

    key: ParsedKey
    size: int
    compr_type: int
    plaintext_size: int

    def __init__(self, buf: bytes, file_offset: int) -> None:

        fields = dict(list(zip(UBIFS_DATA_NODE_FIELDS, struct.unpack(UBIFS_DATA_NODE_FORMAT, buf[0:UBIFS_DATA_NODE_SZ]))))
        for key in fields:
            if key == 'key':
                setattr(self, key, parse_key(fields[key]))
            else:
                setattr(self, key, fields[key])

        setattr(self, 'offset', file_offset)
        setattr(self, 'compr_len', (len(buf) - UBIFS_DATA_NODE_SZ))
        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Data Node'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.data_node(self, tab)


class idx_node(object):
    """Get index node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.

    See ubifs/defines.py for object attributes.
    """
    branches: list[branch]
    errors: list[int]

    child_cnt: int
    level: int

    def __init__(self, buf: bytes) -> None:
        fields = dict(list(zip(UBIFS_IDX_NODE_FIELDS, struct.unpack(UBIFS_IDX_NODE_FORMAT, buf[0:UBIFS_IDX_NODE_SZ]))))
        for key in fields:
            setattr(self, key, fields[key])

        idxs = UBIFS_IDX_NODE_SZ
        # Dynamic detection of `brs` (branch size), whether a hash is present after
        # the key in authenticated UBIFS. Not checking the len of the hash.
        brs = (len(buf) - UBIFS_IDX_NODE_SZ) // self.child_cnt
        setattr(self, 'branches', [branch(buf[idxs+(brs*i):idxs+(brs*i)+brs]) for i in range(0, self.child_cnt)])
        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Index Node'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.idx_node(self, tab)


class branch(object):
    """ Create branch from given idx_node data buf.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.
    """
    hash: bytes
    errors: list[str]

    lnum: int
    offs: int
    len: int
    key: ParsedKey

    def __init__(self, buf: bytes) -> None:
        fields = dict(list(zip(UBIFS_BRANCH_FIELDS, struct.unpack(UBIFS_BRANCH_FORMAT, buf[0:UBIFS_BRANCH_SZ]))))
        for key in fields:
            if key == 'key':
                setattr(self, key, parse_key(fields[key]))
            else:
                setattr(self, key, fields[key])

        if len(buf) > UBIFS_BRANCH_SZ:
            setattr(self, 'hash', buf[UBIFS_BRANCH_SZ:])

        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Branch'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.branch(self, tab)
    

class sb_node(object):
    """Get superblock node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.
    Int:offset  -- Offset in LEB of data node.

    See ubifs/defines.py for object attributes.
    """
    errors: list[str]

    padding: bytes
    key_hash: int
    key_fmt: int
    flags: int
    min_io_size: int
    leb_size: int
    leb_cnt: int
    max_leb_cnt: int
    max_bud_bytes: int
    log_lebs: int
    lpt_lebs: int
    orph_lebs: int
    jhead_cnt: int
    fanout: int
    lsave_cnt: int
    fmt_version: int
    default_compr: int
    padding1: bytes
    rp_uid: int
    rp_gid: int
    rp_size: int
    time_gran: int
    uuid: bytes
    ro_compat_version: int
    hmac: bytes
    hmac_wkm: bytes
    hash_algo: int
    hash_mst: bytes
    padding2: bytes

    def __init__(self, buf: bytes, file_offset: int = -1) -> None:
        self.file_offset = file_offset
        fields = dict(list(zip(UBIFS_SB_NODE_FIELDS, struct.unpack(UBIFS_SB_NODE_FORMAT, buf))))
        for key in fields:
            setattr(self, key, fields[key])

        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Super Block Node'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.sb_node(self, tab)


class mst_node(object):
    """Get master node at given LEB number + offset.

    Arguments:
    Bin:buf     -- Raw data to extract header information from.
    Int:offset  -- Offset in LEB of data node.

    See ubifs/defines.py for object attributes.
    """
    errors: list[str]

    highest_inum: int
    cmt_no: int
    flags: int
    log_lnum: int
    root_lnum: int
    root_offs: int
    root_len: int
    gc_lnum: int
    ihead_lnum: int
    ihead_offs: int
    index_size: int
    total_free: int
    total_dirty: int
    total_used: int
    total_dead: int
    total_dark: int
    lpt_lnum: int
    lpt_offs: int
    nhead_lnum: int
    nhead_offs: int
    ltab_lnum: int
    ltab_offs: int
    lsave_lnum: int
    lsave_offs: int
    lscan_lnum: int
    empty_lebs: int
    idx_lebs: int
    leb_cnt: int
    hash_root_idx: int
    hash_lpt: bytes
    hmac: bytes
    padding: bytes

    def __init__(self, buf: bytes, file_offset: int = -1) -> None:
        self.file_offset = file_offset
        fields = dict(list(zip(UBIFS_MST_NODE_FIELDS, struct.unpack(UBIFS_MST_NODE_FORMAT, buf))))
        for key in fields:
            setattr(self, key, fields[key])

        setattr(self, 'errors', [])

    def __repr__(self) -> str:
        return 'UBIFS Master Block Node'

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        for key in dir(self):
            if not key.startswith('_'):
                yield key, getattr(self, key)

    def display(self, tab: str = '') -> str:
        return display.mst_node(self, tab)
