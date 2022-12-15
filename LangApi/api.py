from __future__ import annotations

from inspect import isclass
# Default libraries
# -----------------

from typing import Dict, TYPE_CHECKING, Any, \
    List, Type, Set
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
    # Modules
    # =======

    Construct = Construct
    LangCode: LangCode

    # Content
    # =======

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

    def __init__(self, analyzer: Analyzer, langCode: LangCode):
        self.LangCode = langCode
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

    _tasks: List[list] = list()
    _currentIndex: List[int] = list()

    def getLastCommands(self, index: int = 0) -> List[list | Construct | Type[ScopeType] | LangApi.Abstract]:
        return self._tasks[-(1 + index)][self._currentIndex[-(1 + index)] + 1:]

    def replaceLastCommands(self, commands: List[list | Construct | Type[ScopeType] | LangApi.Abstract],
                            index: int = 0):
        self._tasks[-(1 + index)] = self._tasks[-(1 + index)][:self._currentIndex[-(1 + index)] + 1]
        self._tasks[-(1 + index)].extend(commands)

    def visit(self, expr: list | Construct | Type[ScopeType] | LangApi.Abstract) \
            -> list | LangApi.Abstract | Type[ScopeType] | Any:
        if isinstance(expr, Attr):
            return expr
        if isinstance(expr, list):
            result = list()
            self._tasks.append(expr)
            self._currentIndex.append(0)
            while self._currentIndex[-1] < len(self._tasks[-1]):
                visited = self.visit(self._tasks[-1][self._currentIndex[-1]])
                self._currentIndex[-1] += 1
                if isinstance(visited, tuple):
                    result.extend(self._unpackTuple(visited))
                    continue
                result.append(visited)
            self._currentIndex.pop(-1)
            self._tasks.pop(-1)
            return result
        if isinstance(expr, Construct):
            parent = self.visit(expr.parent)
            if expr.raw_args:
                args = expr.arguments
            else:
                args = self.visit(expr.arguments)
            assert expr.method in dir(parent)
            return parent.__getattribute__(expr.method)(*args)
        if isclass(expr) and not isinstance(expr, ScopeType):
            expr: Any
            return expr(self)
        return expr

    code: Set[Type[LangApi.ScopeWithCode] | tuple[Type[LangApi.ScopeWithCode], int]] = set()
    _scopes: List[Type[LangApi.ScopeWithoutCode] |
                  Type[LangApi.ScopeWithCode] | list[Type[LangApi.ScopeWithCode], int]] = list()
    _is_not_local = False

    # Generated prefix
    # ----------------

    _return_counter = 0

    def getReturnEx(self) -> Attr:
        result = self._return_counter
        self._return_counter += 1
        return self.useLocalPrefix(Attr([f'$return--{result}']))

    _temp_counter = 0

    def getTempEx(self) -> Attr:
        result = self._temp_counter
        self._temp_counter += 1
        return self.useLocalPrefix(Attr([f'$temp--{result}']))

    _if_counter = 0

    def getIfEx(self) -> Attr:
        result = self._if_counter
        self._if_counter += 1
        return self.useLocalPrefix(Attr([f'--if--{result}']))

    _while_counter = 0

    def getWhileEx(self) -> Attr:
        result = self._while_counter
        self._while_counter += 1
        return self.useLocalPrefix(Attr([f'--while--{result}']))

    _while_scope_counter = 0

    def getWhileScopeEx(self) -> Attr:
        result = self._while_scope_counter
        self._while_scope_counter += 1
        return self.useLocalPrefix(Attr([f'$while--{result}']))

    _check_counter = 0

    def getCheckEx(self) -> Attr:
        result = self._check_counter
        self._check_counter += 1
        return self.useLocalPrefix(Attr([f'$check--{result}']))

    _else_counter = 0

    def getElseEx(self) -> Attr:
        result = self._else_counter
        self._else_counter += 1
        return self.useLocalPrefix(Attr([f'--else--{result}']))

    _predicate_counter = 0

    def getPredicateEx(self) -> Attr:
        result = self._predicate_counter
        self._predicate_counter += 1
        return self.useLocalPrefix(Attr([f'{result}']))

    def getConstEx(self, attr: Attr) -> Attr:  # noqa
        result = attr[:-1] + Attr([f'#{attr[-1]}'])
        return result

    # Prefix methods
    # --------------

    def useDirPrefix(self, attr: Attr, withFuse: bool = False) -> Attr:
        if withFuse:
            return DirAttr(Attr([self.config['project_name']]), attr)
        return attr

    def useLocalPrefix(self, attr: Attr, withFuse: bool = False) -> Attr:
        if self._is_not_local:
            return self.useGlobalPrefix(attr)
        result = Attr()
        for scope in self._scopes[1:]:
            if isinstance(scope, list):
                scope = scope[0]
            if scope is None:
                continue
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

    def getThisScope(self, index=0) -> Type[LangApi.ScopeWithoutCode | LangApi.ScopeWithCode]:
        if isinstance(self._scopes[-(1 + index)], list):
            return self._scopes[-(1 + index)][0]
        return self._scopes[-(1 + index)]

    def enterScope(self, scope: LangApi.ScopeWithoutCode | LangApi.ScopeWithCode, attribute: int = None):
        if isinstance(scope, CodeScope) and scope not in self.code:
            scope: Type[LangApi.ScopeWithCode]
            if attribute is not None:
                self.code.add((scope, attribute))
                self._scopes.append([scope, attribute])
                return
            else:
                self.code.add(scope)
        scope: Type[LangApi.ScopeWithoutCode]
        self._scopes.append(scope)

    def leaveScope(self):
        self._scopes.pop(-1)

    def globalScope(self):
        self._is_not_local = True

    def localScope(self):
        self._is_not_local = False

    def system(self, command: LangApi.CodeType):
        index = -1
        if self._is_not_local:
            index = 0
        scope = self._scopes[index]
        if isinstance(scope, list):
            scope[0].code[scope[1]].append(command)
        else:
            scope.code.append(command)

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
