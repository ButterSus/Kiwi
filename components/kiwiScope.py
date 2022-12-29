"""
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
    from LangApi.api import API
    from LangApi.bytecode import CodeType
    from LangApi.abstract import Abstract


class Attr(list):
    """
    Some basic representation of an attribute.
    It's just a list of strings, except it has
    additional methods, and we can check type using
    if isinstance.
    """

    def append(self, __object: Any):
        """
        Append an object to the attribute if it's not None.
        """
        if __object is None:
            return
        super().append(__object)

    def __add__(self, other) -> Attr:
        """
        I have overloaded the __add__ method,
        because natively it does change the class of Attr.
        """
        return self.__class__(super().__add__(other))

    def __getitem__(self, item):
        """
        I have overloaded the __getitem__ method,
        because natively it does change the class of Attr.
        """
        if isinstance(item, slice):
            return self.__class__(super().__getitem__(item))
        return super().__getitem__(item)

    def toName(self) -> str:
        """
        Just return you the last string of list
        """
        return str(self[-1])

    def toString(self) -> str:
        """
        Return the all strings joined together using dot as separator.
        """
        return '.'.join(self)

    def toPath(self) -> Path:
        """
        Used to convert the attribute to a Path object.
        """
        return reduce(lambda x, y: x / y,
                      [Path(), *self])

    def withSuffix(self, prefix: str):
        """
        It's used to add a suffix to the last string.
        But, you can't add a prefix twice (it can charge and explode!).
        """
        newAttr = self.__class__(self)
        newAttr[-1] += prefix
        return newAttr


class DirAttr(Attr):
    """
    Some alternative way to represent an attributes.
    Sometimes, you want to represent an attribute as a directory.
    For example, when you call function in minecraft:
    function some_project:dir1/dir2/file.mcfunction
    """
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
        """
        Unlike the Attr.toString, this method also adds directory prefix.
        """
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
    name: Optional[str] = None

    def _defaultDirectName(self) -> Optional[str]:
        return self.name

    directName = property(
        fget=_defaultDirectName
    )

    def __init__(self, content: dict, parent: Optional[BasicScope] = None, name: str = None):
        self.content = content
        self.parent = parent
        self.name = name

    def write(self, keys: Key, value: Any, *, isAttribute=False) -> bool | Any:
        if isAttribute:
            if self.isHided(keys):
                return False
            if len(keys) == 1:
                self.content[keys[0]] = value
                return True
            if not self.exists(keys):
                return False
            result: Abstract = self.content[keys[0]]
            if isinstance(result, BasicScope):
                return result.write(Attr(keys[1:]), value, isAttribute=True)
            assert 'setAttribute' in dir(result)
            return result.setAttribute(Attr(keys[1:]), value)
        keys = Attr([keys]) if not isinstance(keys, Attr) else keys
        if len(keys) == 1:
            self.content[keys[0]] = value
            return True
        if not self.exists(keys) and self.parent:
            return self.parent.write(keys, value)
        result = self.write(keys, value, isAttribute=True)
        if not isinstance(result, bool):
            return result
        assert result

    def get(self, keys: Key, *, isAttribute=False) -> Any | BasicScope:
        if isAttribute:
            assert self.exists(keys)
            assert not self.isHided(keys)
            if len(keys) == 1:
                result = self.content[keys[0]]
                return result
            result: Abstract = self.content[keys[0]]
            if isinstance(result, BasicScope):
                return result.get(Attr(keys[1:]))
            assert 'getAttribute' in dir(result)
            return result.getAttribute(Attr(keys[1:]))
        keys = Attr([keys]) if not isinstance(keys, Attr) else keys
        if not self.exists(keys):
            assert self.parent
            return self.parent.get(keys)
        if len(keys) == 1:
            result = self.content[keys[0]]
            return result
        return self.get(keys, isAttribute=True)

    def isAttribute(self, keys: Key) -> bool:
        keys = Attr([keys]) if not isinstance(keys, Attr) else keys
        if len(keys) == 1:
            return False
        assert self.exists(keys)
        assert not self.isHided(keys)
        if isinstance(result := self.content[keys[0]], BasicScope):
            return result.isAttribute(Attr(keys[1:]))
        return True


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
        self.code = dict()

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

    def useNamedSpace(self, name: str, hideModule=False):
        """
        It's used to create space, that can be accessed
        by attributes.
        """
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, Attr) else name
            self.localScope.hide.add(name)
        self.localScope.write(
            name, BasicScope(dict(), self.localScope, name)
        )
        self.localScope = self.localScope.get(name)
        self.localScope.private_mode = hideModule

    def useCustomSpace(self, space: BasicScope, hideMode=False):
        """
        It's usually used for one-body based statements.
        """
        if self.localScope.private_mode:
            self.localScope.hide.add(space.name)
        space.parent = self.localScope
        self.localScope.write(
            space.name, space
        )
        self.localScope = self.localScope.get(space.name)
        self.localScope.private_mode = hideMode

    def useLocalSpace(self, value: int = None, hideMode=False) -> int:
        """
        It's usually used for multi-body statements.
        """
        if value is None:
            value = self._iterator
            self._iterator += 1
        if self.localScope.private_mode:
            self.localScope.hide.add(str(value))
        if not self.localScope.exists(str(value)):
            self.localScope.write(
                str(value), BasicScope(dict(), self.localScope, str(value))
            )
        self.localScope = self.localScope.get(str(value))
        self.localScope.private_mode = hideMode
        return self._iterator - 1 if value is None else value

    def leaveSpace(self):
        """
        This method is called when leaving a space
        """
        assert self.localScope.parent
        self.localScope = self.localScope.parent

    # VARIABLE METHODS
    # ================

    def get(self, name: Key) -> Any | BasicScope:
        """
        This method is used to get a variable
        in current local scopes from variable name.
        """
        return self.localScope.get(name)

    def write(self, name: Key, value: Any):
        """
        This method is used to bind some variable name
        in current local scope to some variable.
        """
        self.localScope.write(name, value)
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, list) else name
            self.localScope.hide.add(name)
