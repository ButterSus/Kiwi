from __future__ import annotations

from inspect import isclass
# Default libraries
# -----------------

from typing import Dict, TYPE_CHECKING, Any,\
    List, Type
from dataclasses import dataclass
from pathlib import Path
from itertools import chain

# Custom libraries
# ----------------

if TYPE_CHECKING:
    import LangApi.abstract as LangApi
    import LangCode.built_in as LangCode
    from Kiwi.kiwiAnalyzer import Analyzer
    from build import ConfigGeneral

from Kiwi.components.kiwiScope import ScopeType, CodeScope
from Kiwi.components.kiwiASO import Attr
from Kiwi.kiwiTokenizer import Tokenizer


@dataclass
class Construct:
    method: str
    parent: Any
    arguments: List[Construct | LangApi.Assignable | str | Attr]


class API:
    defaultLibScope: Dict[str, Dict[str, Type[LangApi.Abstract]]] = {
        'builtins': dict()
    }
    analyzer: Analyzer
    config: ConfigGeneral
    _path: Path
    _files: List[str] = list()

    class General:
        scoreboard: LangCode.Scoreboard
    general = General()
    code: LangCode

    def __init__(self, code: LangCode, analyzer: Analyzer):
        API.code = code
        self.code.built_annotationsInit(self.__class__)
        self.analyzer = analyzer
        self.config = analyzer.constructor.configGeneral
        self._init()
        for name, value in self.defaultLibScope['builtins'].items():
            self.analyzer.scope.write(
                name, value)
        del (self.defaultLibScope['builtins'])
        for module_name, module_scope in self.defaultLibScope.items():
            self.analyzer.scope.newNamedSpace(module_name)
            for name, value in module_scope.items():
                self.analyzer.scope.write(
                    name, value)
            self.analyzer.scope.leaveSpace()
        self.code.built_codeInit(self)

    def _init(self):
        self.general = self.General()

    def finish(self):
        self.code.built_codeFinish(self)

    def resetExpression(self):
        self._counter = 0

    def _unpackTuple(self, value: tuple) -> tuple:
        try:
            return self._unpackTuple(tuple(chain.from_iterable(value)))
        except TypeError:
            return value

    def visit(self, expr: list | Construct | ScopeType) -> list | LangApi.Abstract | ScopeType:
        if isinstance(expr, Attr):
            return expr
        if isinstance(expr, list):
            result = list()
            for item in expr:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(self._unpackTuple(visited))
                    continue
                if visited is None:
                    continue
                result.append(visited)
            return result
        if isinstance(expr, Construct):
            parent = self.visit(expr.parent)
            args = self.visit(expr.arguments)
            return parent.__getattribute__(expr.method)(*args)
        if isclass(expr) and not isinstance(expr, ScopeType):
            expr: Any
            return expr(self)
        return expr

    _counter = 0
    _scopes: List[ScopeType | CodeScope] = list()

    def getTemp(self) -> Attr:
        pass

    def useLocalPrefix(self, attr: list | Attr) -> Attr:
        return Attr(attr)

    def useGlobalPrefix(self, attr: list | Attr) -> Attr:
        return Attr(['sus'] + attr)

    def enterScope(self, scope: ScopeType):
        self._scopes.append(scope)

    def leaveScope(self):
        self._scopes.pop(-1)

    def system(self, text: str):
        self._scopes[-1].code.append(text)

    def eval(self, text: str) -> list | LangApi.Abstract | ScopeType:
        result = self.analyzer.ast.eval(Tokenizer(text).lexer)
        return self.visit(self.analyzer.visit(result))

    def exec(self, text: str) -> list | LangApi.Abstract | ScopeType:
        result = self.analyzer.ast.exec(Tokenizer(text).lexer)
        return self.visit(self.analyzer.visit(result))

    @classmethod
    def build(cls, module_name, scope: Dict[str, Type[LangApi.Abstract]]):
        if module_name not in cls.defaultLibScope.keys():
            cls.defaultLibScope[module_name] = scope
        else:
            cls.defaultLibScope[module_name] |= scope
