from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Set, Any, List, TYPE_CHECKING
from pathlib import Path
from functools import reduce
from abc import ABC, abstractmethod

import LangApi

# Custom libraries

if TYPE_CHECKING:
    from LangApi.bytecode import CodeType


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


class ScopeType:
    private_mode = False
    content: dict
    hide: Set[str] = set()
    parent: Optional[ScopeType]
    name: str = None

    def __init__(self, content: dict, parent: Optional[ScopeType] = None, name: str = None):
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
            result: ScopeType = self.content[keys[0]]
            if not isinstance(result, ScopeType):
                return False
            return result.write(Attr(keys[1:]), value, isAttribute=True)
        keys = Attr([keys]) if not isinstance(keys, Attr) else keys
        if len(keys) == 1:
            self.content[keys[0]] = value
            return True
        if not self.exists(keys) and self.parent:
            return self.parent.write(keys, value)
        assert self.write(keys, value, isAttribute=True)

    def get(self, keys: Key, *, isAttribute=False, ignoreScope=True) -> Any | ScopeType:
        if isAttribute:
            assert self.exists(keys)
            assert not self.isHided(keys)
            if len(keys) == 1:
                result = self.content[keys[0]]
                return result
            result = self.content[keys[0]]
            if isinstance(result, ScopeType):
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


class CodeScope(ScopeType, ABC):
    code: List[CodeType | List[CodeType]]
    api: LangApi.API

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = list()

    def _set_files(self, number: int):
        self.code = [list() for _ in range(number)]

    @abstractmethod
    def toPath(self, attribute: int = None) -> List[str]:
        ...


class NoCodeScope(ScopeType):
    code: List[CodeType]
    api: LangApi.API

    def __init__(self, *args, **kwargs):
        self.code = list()
        super().__init__(*args, **kwargs)


class ScopeSystem:
    _iterator = 0
    _builtInScope: ScopeType = ScopeType(dict())
    globalScope: ScopeType
    localScope: ScopeType

    def __init__(self, libScope: Optional[dict] = None):
        if libScope is None:
            libScope = dict()
        self.globalScope = ScopeType(dict(), self._builtInScope)
        self.globalScope.content |= libScope
        self.localScope = self.globalScope

    # SCOPE METHODS
    # =============

    def newNamedSpace(self, name: str):
        """
        Not recommended feature
        """
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, Attr) else name
            self.localScope.hide.add(name)
        self.localScope.write(
            name, ScopeType(dict(), self.localScope, name)
        )
        self.localScope = self.localScope.get(name, ignoreScope=False)

    def useCustomSpace(self, name: str, space: ScopeType, hideMode=False):
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
        Not recommended feature
        """
        if self.localScope.private_mode:
            self.localScope.hide.add(str(self._iterator))
        self.localScope.write(
            str(self._iterator), ScopeType(dict(), self.localScope, str(self._iterator))
        )
        self.localScope = self.localScope.get(str(self._iterator), ignoreScope=False)
        self._iterator += 1

    def leaveSpace(self):
        assert self.localScope.parent
        self.localScope = self.localScope.parent

    # VARIABLE METHODS
    # ================

    def get(self, name: Key) -> Any | ScopeType:
        return self.localScope.get(name)

    def write(self, name: Key, value: Any = None):
        self.localScope.write(name, value)
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, list) else name
            self.localScope.hide.add(name)

    # ANOTHER METHODS
    # ===============

    def enablePrivate(self):
        self.localScope.private_mode = True

    def disablePrivate(self):
        self.localScope.private_mode = False
