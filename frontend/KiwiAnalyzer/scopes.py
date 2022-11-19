"""
This code is unlicensed
By ButterSus

Previous stage:
    AST

About current stage:
    This stage is used to generate Semantic Analyzer Objects
    SAO -> Compiler

Next stage:
    Compiler
"""


from __future__ import annotations


from dataclasses import dataclass
from typing import Any, List, Optional, Set

from frontend.KiwiAnalyzer.objects import KiwiObject
from frontend.std import built_in_dict
import frontend.KiwiAST.colors as colors
from inspect import isclass


ID = str
Key = ID | List[ID]


@dataclass
class Reference:
    scope: ScopeType
    _keys: ID

    def __init__(self, scope: ScopeType, keys: Key):
        self.scope = scope
        self._keys = keys

    def _getter(self) -> Any | ScopeType:
        return self.scope.content.get(self._keys)

    def _setter(self, value: Any):
        self.scope.write(self._keys, value)

    var: Any = property(
        fset=_setter,
        fget=_getter
    )


class ScopeType:
    private_mode = False
    content: dict
    hide: Set[str] = set()
    parent: Optional[ScopeType]

    def __init__(self, content: dict, parent: Optional[ScopeType] = None):
        self.content = content
        self.parent = parent

    def reference(self, keys: Key, *, isAttribute=False) -> Reference:
        if isAttribute:
            assert self.exists(keys)
            assert not self.isHided(keys)
            if len(keys) == 1:
                return Reference(self, keys[0])
            result: ScopeType = self.content[keys[0]]
            assert isinstance(result, ScopeType)
            return result.reference(keys[1:], isAttribute=True)
        keys = [keys] if not isinstance(keys, list) else keys
        if not self.exists(keys):
            assert self.parent
            return self.parent.reference(keys)
        if len(keys) == 1:
            assert self.exists(keys)
            return Reference(self, keys[0])
        return self.reference(keys, isAttribute=True)

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
            return result.write(keys[1:], value, isAttribute=True)
        keys = [keys] if not isinstance(keys, list) else keys
        if len(keys) == 1:
            self.content[keys[0]] = value
            return True
        if not self.exists(keys) and self.parent:
            return self.parent.write(keys, value)
        assert self.write(keys, value, isAttribute=True)

    def get(self, keys: Key, *, isAttribute=False, hideMode=False) -> Any | ScopeType:
        if isAttribute:
            assert self.exists(keys)
            assert not self.isHided(keys)
            if len(keys) == 1:
                return self.content[keys[0]]
            result: ScopeType = self.content[keys[0]]
            return result.get(keys[1:], isAttribute=True)
        keys = [keys] if not isinstance(keys, list) else keys
        if not self.exists(keys):
            assert self.parent
            return self.parent.get(keys)
        if len(keys) == 1:
            return self.content[keys[0]]
        return self.get(keys, isAttribute=True)

    def exists(self, key: Key) -> bool:
        if isinstance(key, list):
            return key[0] in self.content
        return key in self.content

    def isHided(self, key: Key) -> bool:
        return key[0] in self.hide


class ScopeSystem:
    _iterator = 0
    _builtInScope: ScopeType = ScopeType(built_in_dict)
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

    def newNamedSpace(self, name: ID):
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, list) else name
            self.localScope.hide.add(name)
        self.localScope.write(
            name, ScopeType(dict(), self.localScope)
        )
        self.localScope = self.localScope.get(name)

    def newLocalSpace(self):
        if self.localScope.private_mode:
            self.localScope.hide.add(str(self._iterator))
        self.localScope.write(
            str(self._iterator), ScopeType(dict(), self.localScope)
        )
        self.localScope = self.localScope.get(str(self._iterator))
        self._iterator += 1

    def leaveSpace(self):
        assert self.localScope.parent
        self.localScope = self.localScope.parent

    # VARIABLE METHODS
    # ================

    def ref(self, name: Key) -> Reference:
        return self.localScope.reference(name)

    def get(self, name: Key) -> Any | ScopeType:
        return self.localScope.get(name)

    def write(self, name: Key, value: Any):
        self.localScope.write(name, value)
        if self.localScope.private_mode:
            name = name[0] if isinstance(name, list) else name
            self.localScope.hide.add(name)

    # ANOTHER METHODS
    # ===============

    def dump(self, *, indent=4):
        color = colors.Cyan + colors.BackgroundDefault
        return colors.Red + 'globals' + self._dump(self.globalScope, color=color, indent=indent) + colors.ResetAll

    def _dump(self, node: KiwiObject | ScopeType, level=1, color=colors.ResetAll, *, indent=4):
        _tabulation = ' ' * indent
        if isinstance(node, ScopeType):
            items = list()
            for key in node.content.keys():
                prefix = str()
                if key in node.hide:
                    prefix = colors.Black + colors.BackgroundWhite + " private " + colors.BackgroundDefault + " "
                if isinstance(node.content[key], ScopeType):
                    items.append(f"\n{_tabulation * level}{prefix}{colors.Red}{key}" + self._dump(node.content[key], level=level + 1, color=color))
                    continue
                items.append(f"\n{_tabulation * level}"
                             f"{prefix}{colors.Yellow}{key} {colors.Blue + colors.BackgroundDefault}={color} "
                             f"{self._dump(node.content[key], level=level + 1, color=color, indent=indent)}")
            return f'{colors.Red} is {{{", ".join(items)}{colors.Red}}}'
        if isclass(node):
            return f'instance of {colors.Magenta + colors.BackgroundBlack} {node.__name__} {color}'
        if isinstance(node, KiwiObject):
            items = list()
            for key in node.__annotations__:
                items.append(f"\n{_tabulation * level}"
                             f"{colors.Yellow}{key} {colors.Blue}={color} "
                             f"{self._dump(node.__getattribute__(key), level=level + 1, color=color, indent=indent)}")
            return f'{colors.White}Variable({" ,".join(items)}{colors.White})'
        return ''

    def enablePrivate(self):
        self.localScope.private_mode = True

    def disablePrivate(self):
        self.localScope.private_mode = False

