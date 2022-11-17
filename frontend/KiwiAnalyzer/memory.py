from __future__ import annotations

import frontend.KiwiAST as kiwi
import frontend.std as std
from frontend.KiwiAnalyzer.objects import KiwiObject
from inspect import isclass
from typing import Optional, Any


_iterator: int = 0
NameReference = kiwi.Attribute | kiwi.Name


class ViewReference:
    _view: View
    _key: str

    def __init__(self, view: View, key: str):
        self._view = view
        self._key = key

    def _set(self, value: Any):
        self._view[self._key] = value

    def _get(self) -> Any:
        return self._view[self._key]

    ref = property(
        fset=_set,
        fget=_get
    )


class View(dict):
    parent: Optional[View]
    name: str

    def __init__(self, parent: Optional[View], name: str = None, *args):
        global _iterator
        self.parent = parent
        if name is None:
            name = str(_iterator)
            _iterator += 1
        if parent is not None:
            parent[name] = self
        self.name = name
        super().__init__(*args)

    def createReference(self, key: str) -> ViewReference:
        return ViewReference(self, key)

    def exists(self, key: str) -> bool:
        return key in self.keys()


class KiwiAnnotations:
    _built_in = {
        "score": std.Score,
        "scoreboard": std.Scoreboard
    }
    _globalView = View(None, 'global', _built_in)
    _localView = _globalView

    def newScope(self, name: str):
        name = str(name)
        self._localView = View(self._localView, name)

    def localScope(self):
        self._localView = View(self._localView)

    def leave(self):
        self._localView = self._localView.parent

    def add(self, annotation: str, type: kiwi.type) -> Optional:
        annotation = str(annotation)
        self._localView[annotation] = type
        return ViewReference(self._localView, annotation)

    def write(self, annotation: str, type: kiwi.type) -> Optional[ViewReference]:
        annotation = str(annotation)
        if (result := self.getRef(annotation)) is None:
            return None
        result.ref = type
        return result

    def get(self, annotation: str) -> Any:
        annotation = str(annotation)
        if (result := self.getRef(annotation)) is None:
            print('error')
            return None
        return result.ref

    def getRef(self, annotation: str):
        annotation = str(annotation)
        return self._getRef(annotation, self._localView)

    def _getRef(self, annotation: str, view: View) -> Optional[ViewReference]:
        annotation = str(annotation)
        try:
            if view.exists(annotation):
                return ViewReference(view, annotation)
            return self._getRef(annotation, view.parent)
        except AttributeError:
            return None

    def exists(self, name: str) -> bool:
        name = str(name)
        return self.getRef(name) is not None

    def current_position(self) -> str:
        result: str = str()
        view = self._localView
        try:
            while True:
                result = view.name + '->' + result
                view = view.parent
        except AttributeError:
            return result

    def dump(self):
        return self._dump(self._globalView)

    def _dump(self, node, level=0) -> str:
        indent = ' ' * 4
        if isinstance(node, dict):
            result: str = ''
            for key, value in node.items():
                if key in self._built_in.keys():
                    continue
                value = self._dump(value, level=level+1)
                result += f'{kiwi.colors.Yellow}{key} ' \
                          f'{kiwi.colors.Blue}= ' \
                          f'{kiwi.colors.Red}{value}\n'
            return result
        if isclass(node):
            return f'instance <{node.__name__}>'
        if isinstance(node, KiwiObject):
            variables: dict = node.__annotations__
            for key in variables.keys():
                variables[key] = node.__getattribute__(key)
            return f'{kiwi.colors.Cyan}<{node.__class__.__name__}>:\n{indent * level}{self._dump(variables, level=level)}'
