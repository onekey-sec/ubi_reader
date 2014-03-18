#!/usr/bin/env python
#############################################################
# ubi_reader/ubifs/display
# (c) 2014 Jason Pruitt (jrspruitt@gmail.com)
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

def common_hdr(chdr, tab=''):
    print '%s%s' % (tab, chdr)
    tab += '\t'
    for key, value in chdr:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)


def sb_node(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        elif key == 'uuid':
            print '%s%s: %r' % (tab, key, value)
        else:
            print '%s%s: %s' % (tab, key, value)


def mst_node(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)


def dent_node(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)


def data_node(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key in ['display', 'data']:
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)


def idx_node(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)


def ino_node(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)


def branch(node, tab=''):
    print '%s%s' % (tab, node)
    tab += '\t'
    for key, value in node:
        if key == 'display':
            continue
        elif key == 'errors':
            print '%s%s: %s' % (tab, key, ','.join(value))
        else:
            print '%s%s: %s' % (tab, key, value)

