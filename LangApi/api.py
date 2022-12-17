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
from dataclasses import dataclass, field
from itertools import chain
from inspect import isclass

# Custom libraries
# ----------------

if TYPE_CHECKING:
    import LangApi  # noqa
    import LangCode  # noqa
    from Kiwi.kiwiAnalyzer import Analyzer
    from build import ConfigGeneral

from Kiwi.components.kiwiScope import BasicScope, CodeScope
from Kiwi.kiwiTokenizer import Tokenizer


@dataclass
class Construct:
    """
    This dataclass stores analyzer request to run any method of built-in object or grammar constructions.
    API.visit method can launch it.
    """
    method: str
    """
    The name of the method to run
    e.g:
    "Add"
    (Check LangApi.abstract for name of methods)
    """
    parent: Any
    """
    The object or class of the method to run,
    if it's class, then it should take api parameter to initialize
    """
    arguments: List[Any]
    """
    The arguments of the method to run,
    It can be absolutely anything
    """
    raw_args: bool = field(default=False)
    """
    By default, arguments will be passed to visitor, that will launch Construct before to pass
    it as argument.
    e.g:
    Let's assume we have this structure:
    Construct(  # This construct will be handled last of all
        method = "Add",
        parent = SomeClassOrObject
        arguments = [
            Construct(  # This construct will be handled first of all
                method = "Add",
                parent = SomeClassOrObject
                arguments = [1, 2]
            )
        ]
    ),
    But if raw_args equals to True, then arguments will not be handled by visitor
    """


class API:
    """
    Kiwi Language API provides you all basic methods and properties
    to implement any built-in types, functions or even grammar constructions.
    """
    builtinLibScope: Dict[
        str,
        Dict[str, Type[LangApi.Abstract]
        ]
    ] = {
        'builtins': dict()
    }
    analyzer: Analyzer
    config: ConfigGeneral
    Construct: Construct.__class__ = Construct

    def __init__(self, analyzer: Analyzer, langApi: Any, langCode: Any):
        # Modules reference
        # -----------------

        global LangApi  # noqa
        LangApi = langApi  # noqa
        global LangCode  # noqa
        LangCode = langCode  # noqa

        # Class references
        # ----------------

        self.analyzer = analyzer
        self.config = analyzer.config

        # Built-in objects initialization
        # -------------------------------

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

    def visit(self, instruction: Any) -> Any:
        """
        This method is used to handle analyzer output.
        Also, if the input value is a list with tuple, tuple will be unpacked.
        e.g:
        If the input value is a list of Construct, constructs will be launched.
        """
        if isinstance(instruction, list):
            result = list()
            for item in instruction:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(self._unpackTuple(visited))
                    continue
                result.append(visited)
            return result
        if isinstance(instruction, Construct):
            parent = self.visit(instruction.parent)
            if instruction.raw_args:
                args = instruction.arguments
            else:
                args = self.visit(instruction.arguments)
            assert instruction.method in dir(parent)
            return parent.__getattribute__(instruction.method)(*args)
        if isclass(instruction) and not isinstance(instruction, BasicScope):
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

    def getThisScope(self, index=0) -> BasicScope:
        """
        This method returns the scope at the given index.
        e.g:
        If index is 0, which is used by default, the scope at index 0 will be returned.

        Let's say we have the following code:
        function foo():
            print("Hello, Kiwi!")  # if this method is called here, then function scope will be returned.
        """
        if isinstance(self.scopeFolder[-(1 + index)], list):
            return self.scopeFolder[-(1 + index)][0]
        return self.scopeFolder[-(1 + index)]

    def enterScope(self, scope: BasicScope):
        """
        This method is used to enter a new or existing scope.
        But it doesn't append code of scope to datapack.
        """
        self.scopeFolder.append(scope)

    def leaveScope(self):
        self.scopeFolder.pop(-1)

    def system(self, command: LangApi.CodeType, codeKey='main'):
        self.scopeFolder[-1].code[codeKey].append(command)

    def eval(self, text: str) -> Any:
        """
        This method is used to evaluate a string.
        :return:
        It returns Kiwi-Object, Score for example
        """
        result = self.analyzer.ast.eval(Tokenizer(text).lexer)
        return self.visit(self.analyzer.visit(result))

    def exec(self, text: str) -> Any:
        """
        This method is used to execute a string.
        :return:
        It returns Kiwi-Object, Score for example
        """
        result = self.analyzer.ast.exec(Tokenizer(text).lexer)
        return self.visit(self.analyzer.visit(result))

    @classmethod
    def build(cls, module_name, scope: Dict[str, Type[LangApi.Abstract]]):
        """
        It's used to add built-in objects.
        """
        if module_name not in cls.builtinLibScope.keys():
            cls.builtinLibScope[module_name] = scope
        else:
            cls.builtinLibScope[module_name] |= scope
