"""
Copyright (c) 2022 Krivoshapkin Edward

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This module contains all the objects to handle scopes,
access to variables and functions and attribute classes.

Recommendations:
Do not import * from this module directly.
Instead, import Attr, ... from this module.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Set, Any, List, TYPE_CHECKING, Dict
from pathlib import Path
from functools import reduce
from abc import ABC, abstractmethod

# Custom libraries

if TYPE_CHECKING:
    from LangApi import CodeType, API, Construct
    from LangCode import Function


class Attr(list):
    def append(self, __object: Any):
        if __object is None:
            return
        super().append(__object)

    def __add__(self, other) -> Attr:
        return self.__class__(super().__add__(other))

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(super().__getitem__(item))
        return super().__getitem__(item)

    def toName(self) -> str:
        return str(self[-1])

    def toString(self) -> str:
        return '.'.join(self)

    def toPath(self) -> Path:
        return reduce(lambda x, y: x / y,
                      [Path(), *self])

    def withPrefix(self, prefix: str):
        newAttr = self.__class__(self)
        newAttr[-1] += prefix
        return newAttr


class DirAttr(Attr):
    directory: Attr

    def __init__(self, directory: Attr, *args):
        self.directory = directory
        super().__init__(*args)

    def __add__(self, other) -> Attr:
        return self.__class__(self.directory, super().__add__(other))

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self.directory, super().__getitem__(item))
        return super().__getitem__(item)

    def toName(self) -> str:
        return str(self[-1])

    def toString(self) -> str:
        return f"{self.directory.toString()}:{'/'.join(self)}"


Key = str | Attr


class BasicScope:
    """
    This class represents a basic scope.
    e.g:
    Namespace can not have code, so this class is used to represent it.
    Usually, there is no need to use it.
    """
    private_mode = False
    content: dict
    hide: Set[str] = set()
    parent: Optional[BasicScope]
    name: str = None

    def __init__(self, content: dict, parent: Optional[BasicScope] = None, name: str = None):
        self.content = content
        self.parent = parent
        self.name = name

    def write(self, keys: Key, value: Any, *, isAttribute=False) -> True:
        if isAttribute:
            if self.isHided(keys):
                return False
            if len(keys) == 1:
                self.content[keys[0]] = value
                return True
            if not self.exists(keys):
                return False
            result: BasicScope = self.content[keys[0]]
            if not isinstance(result, BasicScope):
                return False
            return result.write(Attr(keys[1:]), value, isAttribute=True)
        keys = Attr([keys]) if not isinstance(keys, Attr) else keys
        if len(keys) == 1:
            self.content[keys[0]] = value
            return True
        if not self.exists(keys) and self.parent:
            return self.parent.write(keys, value)
        assert self.write(keys, value, isAttribute=True)

    def get(self, keys: Key, *, isAttribute=False, ignoreScope=True) -> Any | BasicScope:
        if isAttribute:
            assert self.exists(keys)
            assert not self.isHided(keys)
            if len(keys) == 1:
                result = self.content[keys[0]]
                return result
            result = self.content[keys[0]]
            if isinstance(result, BasicScope):
                return result.get(Attr(keys[1:]), ignoreScope=ignoreScope)
            return result.get(Attr(keys[1:]), isAttribute=True)
        keys = Attr([keys]) if not isinstance(keys, Attr) else keys
        if not self.exists(keys):
            assert self.parent
            return self.parent.get(keys)
        if len(keys) == 1:
            result = self.content[keys[0]]
            return result
        return self.get(keys, isAttribute=True)

    def exists(self, key: Key) -> bool:
        if isinstance(key, Attr):
            return key[0] in self.content
        return key in self.content

    def isHided(self, key: Key) -> bool:
        return key[0] in self.hide


class CodeScope(BasicScope, ABC):
    """
    This class represents a scope, that can contain code. (multiple times)
    e.g:
    IfElse statement can contain code, also it can be a scope.
    But,
    Namespace statement can not contain code.
    """
    code: Dict[str, List[CodeType]]
    api: API

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = {
            'main': list()
        }

    def Return(self, value: Construct) -> Construct:
        """
        This method is default implementation of
        return statement.
        It calls assign method of function return parameter.
        """
        i = 0
        while not isinstance(function:=self.api.getThisScope(i), self.api.LangCode.Function):  # noqa
            i += 1
        function: Function
        return self.api.Construct(
                'Assign',
                function.returns,
                [value]
            )

    @abstractmethod
    def toPath(self, key: str) -> List[str]:
        """
        This method is used to set path of file
        relatively to data folder, including file name (last element with file format).
        e.g:
        return ['predicates', '0.json']
        """
        ...


class ScopeSystem:
    _iterator = 0
    _builtInScope: BasicScope = BasicScope(dict())
    globalScope: BasicScope
    localScope: BasicScope

    def __init__(self, libScope: Optional[dict] = None):
        """
        libScope should contain libraries.
        """
        if libScope is None:
            libScope = dict()
        self.globalScope = BasicScope(dict(), self._builtInScope)
        self.globalScope.content |= libScope
        self.localScope = self.globalScope

    # SCOPE METHODS
    # =============

    def newNamedSpace(self, name: str):
        """
        Not recommended feature.
        It's used to debug something.
        """
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, Attr) else name
            self.localScope.hide.add(name)
        self.localScope.write(
            name, BasicScope(dict(), self.localScope, name)
        )
        self.localScope = self.localScope.get(name, ignoreScope=False)

    def useCustomSpace(self, name: str, space: BasicScope, hideMode=False):
        """
        This method is used to enter some scope.
        Also, you can set hideMode to True, if you want to make scope local.
        """
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, Attr) else name
            self.localScope.hide.add(name)
        space.parent = self.localScope
        self.localScope.write(
            name, space
        )
        self.localScope = self.localScope.get(name, ignoreScope=False)
        self.localScope.name = name
        self.localScope.private_mode = hideMode

    def newLocalSpace(self):
        """
        Not recommended feature.
        It's used to debug something.
        """
        if self.localScope.private_mode:
            self.localScope.hide.add(str(self._iterator))
        self.localScope.write(
            str(self._iterator), BasicScope(dict(), self.localScope, str(self._iterator))
        )
        self.localScope = self.localScope.get(str(self._iterator), ignoreScope=False)
        self._iterator += 1

    def leaveSpace(self):
        """
        This method is called when leaving a space
        """
        assert self.localScope.parent
        self.localScope = self.localScope.parent

    # VARIABLE METHODS
    # ================

    def get(self, name: Key) -> Any | BasicScope:
        return self.localScope.get(name)

    def write(self, name: Key, value: Any):
        """
        This method is used to bind some variable name
        in current local scope to some variable.
        Notes:

        """
        self.localScope.write(name, value)
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, list) else name
            self.localScope.hide.add(name)

    # ANOTHER METHODS
    # ===============

    def enablePrivate(self):
        """
        This method is used to enable private mode.
        e.g:
        Namespace statement contains private and public variables,
        so if you want to make them private, you need to call this method.
        """
        self.localScope.private_mode = True

    def disablePrivate(self):
        """
        This method is used to disable private mode.
        e.g:
        Namespace statement contains private and public variables,
        so if you want to make them public, you need to call this method.
        """
        self.localScope.private_mode = False
