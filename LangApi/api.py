from __future__ import annotations

from inspect import isclass
# Default libraries
# -----------------

from typing import Dict, TYPE_CHECKING, Any,\
    List, Type
from dataclasses import dataclass, field
from itertools import chain

# Custom libraries
# ----------------

if TYPE_CHECKING:
    import LangApi as LangApi
    import LangCode.built_in as LangCode
    from Kiwi.kiwiAnalyzer import Analyzer
    from build import ConfigGeneral

from Kiwi.components.kiwiScope import ScopeType, CodeScope
from Kiwi.components.kiwiASO import Attr, DirAttr
from Kiwi.kiwiTokenizer import Tokenizer


@dataclass
class Construct:
    method: str
    parent: Any
    arguments: List[Construct | str | Attr | LangApi.Abstract | LangCode.TokenString]
    raw_args: bool = field(default=False)


class API:
    defaultLibScope: Dict[str, Dict[str, Type[LangApi.Abstract]]] = {
        'builtins': dict()
    }
    analyzer: Analyzer
    config: ConfigGeneral
    _files: List[str] = list()

    class General:
        scoreboard: LangCode.Scoreboard
        constants: Dict[int, LangCode.Score]
    general = General()

    def __init__(self, analyzer: Analyzer):
        self.analyzer = analyzer
        self.config = analyzer.config
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

    def _init(self):
        self.general = self.General()

    def resetExpression(self):
        self._temp_counter = 0

    def _unpackTuple(self, value: tuple) -> tuple:
        try:
            return self._unpackTuple(tuple(chain.from_iterable(value)))
        except TypeError:
            return value

    def visit(self, expr: list | Construct | ScopeType | LangApi.Abstract)\
            -> list | LangApi.Abstract | ScopeType:
        if isinstance(expr, Attr):
            return expr
        if isinstance(expr, list):
            result = list()
            for item in expr:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(self._unpackTuple(visited))
                    continue
                result.append(visited)
            return result
        if isinstance(expr, Construct):
            parent = self.visit(expr.parent)
            if expr.raw_args:
                args = expr.arguments
            else:
                args = self.visit(expr.arguments)
            return parent.__getattribute__(expr.method)(*args)
        if isclass(expr) and not isinstance(expr, ScopeType):
            expr: Any
            return expr(self)
        return expr

    code: List[CodeScope] = list()
    _scopes: List[ScopeType | CodeScope] = list()
    _is_not_local = False

    # Generated prefix
    # ----------------

    _return_counter = 0

    def getReturnEx(self) -> Attr:
        result = self._return_counter
        self._return_counter += 1
        return self.useLocalPrefix(Attr([f'${result}']))

    _temp_counter = 0

    def getTempEx(self) -> Attr:
        result = self._temp_counter
        self._temp_counter += 1
        return Attr([f'%{result}'])

    def getConstEx(self, attr: Attr) -> Attr:  # noqa
        result = attr[:-1] + Attr([f'#{attr[-1]}'])
        return result

    # Prefix methods
    # --------------

    def useDirPrefix(self, attr: Attr) -> Attr:
        result = Attr()
        for scope in self._scopes[1:]:
            result.append(scope.name)
        return DirAttr(Attr([self.config['project_name']]), attr)

    def useLocalPrefix(self, attr: Attr, withFuse: bool = False) -> Attr:
        if self._is_not_local:
            return self.useGlobalPrefix(attr)
        result = Attr()
        for scope in self._scopes[1:]:
            result.append(scope.name)
        result = self.useGlobalPrefix(result + attr)
        if withFuse:
            return self._useFusePrefix(result)
        return result

    def useGlobalPrefix(self, attr: Attr, withFuse: bool = False) -> Attr:
        if withFuse:
            return self._useFusePrefix(attr)
        return attr

    def _useFusePrefix(self, attr: Attr) -> Attr:
        return attr.__class__([self.config['project_name']]) + attr

    # Another methods
    # ---------------

    def getThisScope(self) -> ScopeType | CodeScope | LangCode.Function:
        return self._scopes[-1]

    def enterScope(self, scope: ScopeType):
        if isinstance(scope, CodeScope) and scope not in self.code:
            self.code.append(scope)
        self._scopes.append(scope)

    def leaveScope(self):
        self._scopes.pop(-1)

    def globalScope(self):
        self._is_not_local = True

    def localScope(self):
        self._is_not_local = False

    def system(self, command: LangApi.CodeType):
        if self._is_not_local:
            self._scopes[0].code.append(command)
        else:
            self._scopes[-1].code.append(command)

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
