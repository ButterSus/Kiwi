from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Set, Any

# Custom libraries

...


class Attr(list):
    def toString(self) -> str:
        return str(self[-1])


Key = str | Attr


class ScopeType:
    private_mode = False
    content: dict
    hide: Set[str] = set()
    parent: Optional[ScopeType]

    def __init__(self, content: dict, parent: Optional[ScopeType] = None):
        self.content = content
        self.parent = parent

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
            result: ScopeType = self.content[keys[0]]
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
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, Attr) else name
            self.localScope.hide.add(name)
        self.localScope.write(
            name, ScopeType(dict(), self.localScope)
        )
        self.localScope = self.localScope.get(name, ignoreScope=False)

    def newLocalSpace(self):
        if self.localScope.private_mode:
            self.localScope.hide.add(str(self._iterator))
        self.localScope.write(
            str(self._iterator), ScopeType(dict(), self.localScope)
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