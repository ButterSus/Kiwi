"""
This module provides you all methods and classes,
to handle any task.
You can implement any construction, data type or
built-in function.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import (
    Dict, TYPE_CHECKING, Any,List, Type, Set
)
from itertools import chain
from inspect import isclass

# Custom libraries
# ----------------

from components.kiwiScope import BasicScope, CodeScope, Attr as _Attr
from components.kiwiASO import AST as _AST
from components.kiwiTools import AST_Visitor as _AST_Visitor

if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi


# Initialization of modules
# -------------------------

def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa


class API:
    """
    frontend Language API provides you all basic methods and properties
    to implement any built-in types, functions or even grammar constructions.
    """
    builtinLibScope: Dict[
            str,
            Dict[str, Type[LangApi.abstract.Abstract]
        ]] = {
        'builtins': dict()
    }
    prefix: LangApi.prefix.Prefix
    general: API

    # Parts of compiler
    # -----------------

    constructor: compiler.KiwiConstructor.Constructor
    builder: compiler.Builder
    tokenizer: compiler.Tokenizer
    ast: compiler.AST
    analyzer: compiler.kiwiAnalyzer.Analyzer

    # General parameters
    # ------------------

    configGeneral: compiler.ConfigGeneral

    def __init__(
            self,
            constructor: compiler.KiwiConstructor.Constructor,
            builder: compiler.Builder,
            tokenizer: compiler.Tokenizer,
            ast: compiler.AST
    ):
        # Parts of compiler
        # -----------------

        self.constructor = constructor
        self.builder = builder
        self.tokenizer = tokenizer
        self.ast = ast

        # General parameters
        # ------------------

        self.configGeneral = builder.configGeneral

        # Initialization
        # --------------

        API.general = self
        self.prefix = LangApi.prefix.Prefix(self)
        for name, value in self.builtinLibScope['builtins'].items():
            self.analyzer.scope.write(
                name, value
            )
        del (self.builtinLibScope['builtins'])

    def _unpackTuple(self, value: tuple) -> tuple:
        try:
            return self._unpackTuple(tuple(chain.from_iterable(value)))
        except TypeError:
            return value

    def visit(self, instruction: Any, canInit=False) -> Any:
        """
        This method is used to handle analyzer output.
        Also, if the input value is a list with tuple, tuples will be unpacked.
        e.g:
        If the input value is a list of Construct, constructs will be launched.
        """
        if isinstance(instruction, _Attr):
            return instruction
        if isinstance(instruction, list):
            result = list()
            for item in instruction:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(self._unpackTuple(visited))
                    continue
                result.append(visited)
            return result
        if isinstance(instruction, _AST):
            for annotation, attribute in _AST_Visitor.getAttributes(instruction):
                visited = self.visit(attribute)
                instruction.__setattr__(annotation, visited)
            return instruction
        if isinstance(instruction, LangApi.abstract.Construct):
            parent = self.visit(instruction.parent, canInit=True)
            assert isinstance(parent, LangApi.abstract.Abstract)
            if instruction.raw_args:
                args = instruction.arguments
            else:
                args = self.visit(instruction.arguments)
            return parent.loader(instruction.method)(*args)
        if isclass(instruction) and not isinstance(instruction, BasicScope) and canInit:
            instruction: Any
            return instruction(self)
        return instruction

    code: Set[CodeScope] = set()
    """
    A set of all code scopes, that will be put into datapack.
    """

    scopeFolder: List[BasicScope | CodeScope] = list()
    """
    A list of scopes, it's usually used to build prefixes in variable or file names.
    """

    # Another methods
    # ---------------

    _isGlobal: int = 0

    def enableGlobal(self):
        self._isGlobal += True

    def disableGlobal(self):
        self._isGlobal -= True

    def getThisScope(self, index=0) -> BasicScope:
        """
        This method returns the scope at the given index.
        e.g:
        If index is 0, which is used by default, the scope at index 0 will be returned.

        Let's say we have the following code:
        function foo():
            print("Hello, frontend!")  # if this method is called here, then function scope will be returned.
        """
        return self.scopeFolder[-(1 + index)]

    def enterScope(self, scope: BasicScope):
        """
        This method is used to enter a new or existing scope.
        But it doesn't append code of scope to datapack.
        """
        self.scopeFolder.append(scope)

    _codeKeys: List[str] = list()

    def enterCodeScope(self, scope: CodeScope, codeKey: str = None):
        """
        This method is used to enter a new or existing scope.
        """
        if self._codeBuffers:
            assert False
        self.code.add(scope)
        self.enterScope(scope)
        if codeKey is not None:
            self._codeKeys.append(codeKey)

    def leaveScope(self):
        """
        This method is used to leave the current scope.
        """
        if self._codeBuffers:
            assert False
        self.scopeFolder.pop(-1)

    def leaveScopeWithKey(self):
        """
        This method is used to leave the current scope and code key.
        """
        if self._codeBuffers:
            assert False
        self.leaveScope()
        self._codeKeys.pop(-1)

    _codeBuffers: List[Dict[str, List[LangApi.bytecode.CodeType]]] = list()

    def bufferPush(self):
        """
        This method allows you additionally save all commands into buffer.
        It's used to copy generated commands.
        Be careful! It doesn't save global commands.
        You can shoot out your leg! (As I did twice)
        """
        self._codeBuffers.append(dict())

    def bufferPop(self) -> Dict[str, List[LangApi.bytecode.CodeType]]:
        """
        This method allows you to pop saved commands from buffer.
        It's used to get generated commands.
        Be careful! It doesn't save global commands.
        You can shoot out your leg! (As I did twice)
        """
        return self._codeBuffers.pop(-1)

    def bufferPaste(self, buffer: Dict[str, List[LangApi.bytecode.CodeType]]):
        """
        This method is used to paste buffer code into current scope
        Be careful! It uses relative scope path!
        You can shoot out your leg! (As I did twice)
        """
        for codeKey, code in buffer.items():
            for command in code:
                self.system(command, codeKey=codeKey)

    def system(self, command: LangApi.bytecode.CodeType, codeKey: str = None, isGlobal=False):
        """
        This method is used to add command to code of the current scope.
        It's one of the most important methods.
        """

        # Getting index
        # -------------

        if self._codeKeys and not (isGlobal + self._isGlobal) and codeKey is None:
            codeKey = self._codeKeys[-1]
        else:
            codeKey = 'main'
        index = 0 if isGlobal + self._isGlobal else -1

        # Buffer saving
        # -------------

        if self._codeBuffers and not (isGlobal + self._isGlobal):
            if codeKey not in self._codeBuffers[-1]:
                self._codeBuffers[-1][codeKey] = list()
            self._codeBuffers[-1][codeKey].append(command)
        # Command saving
        # --------------

        if codeKey not in self.scopeFolder[index].code.keys():
            self.scopeFolder[index].code[codeKey] = list()
        self.scopeFolder[index].code[codeKey].append(command)

    def eval(self, text: str) -> Any:
        """
        This method is used to evaluate a string.
        :return:
        It returns frontend-Object, Score for example
        """
        result = self.analyzer.ast.eval(compiler.Tokenizer(text).lexer)
        return self.visit(self.analyzer.visit(result))

    def exec(self, text: str) -> Any:
        """
        This method is used to execute a string.
        :return:
        It returns frontend-Object, Score for example
        """
        result = self.analyzer.ast.exec(compiler.Tokenizer(text).lexer)
        return self.visit(self.analyzer.visit(result))

    @classmethod
    def build(cls, scope: Dict[str, Type[LangApi.abstract.Abstract]]):
        """
        It's used to add built-in objects.
        Usually it's called before API initialization.
        """
        cls.builtinLibScope['builtins'] |= scope
