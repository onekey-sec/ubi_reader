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
import sys
import traceback
from typing import Literal, NoReturn, Protocol, overload
from ubireader import settings

class _Obj(Protocol):
    __name__: str

def log(obj: _Obj, message: str) -> None:
    if settings.logging_on or settings.logging_on_verbose:
        print('{} {}'.format(obj.__name__, message))

def verbose_log(obj: _Obj, message: str) -> None:
    if settings.logging_on_verbose:
        log(obj, message)

class _Displayable(Protocol):
    def display(self, tab: str) -> str: ...

def verbose_display(displayable_obj: _Displayable) -> None:
    if settings.logging_on_verbose:
        print(displayable_obj.display('\t'))

@overload
def error(obj: _Obj, level: Literal['fatal', 'Fatal'], message: str) -> NoReturn: ...
@overload
def error(obj: _Obj, level: str, message: str) -> None: ...

def error(obj: _Obj, level: str, message: str) -> None:
    if settings.error_action == 'exit':
        print('{} {}: {}'.format(obj.__name__, level, message))
        if settings.fatal_traceback:
            traceback.print_exc()
        sys.exit(1)

    else:
        if level.lower() == 'warn':
            print('{} {}: {}'.format(obj.__name__, level, message))
        elif level.lower() == 'fatal':
            print('{} {}: {}'.format(obj.__name__, level, message))
            if settings.fatal_traceback:
                traceback.print_exc()
            sys.exit(1)
        else:
            print('{} {}: {}'.format(obj.__name__, level, message))

