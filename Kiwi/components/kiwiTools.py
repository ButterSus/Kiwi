from __future__ import annotations

from inspect import isclass
# Default libraries
# -----------------

from dataclasses import dataclass as _dataclass
from typing import Any, List, Callable
from tokenize import tok_name
from itertools import chain

# Custom libraries
# ----------------

import Kiwi.components.kiwiColors as _colors
import Kiwi.components.kiwiASO as _kiwi
from Kiwi.components.kiwiScope import Attr, ScopeSystem, ScopeType
from Kiwi.kiwiTokenizer import\
    Tokenize as _Tokenize,\
    generate_tokens as _generate_tokens,\
    StringIO as _StringIO,\
    Tokenizer as _Tokenizer


def dumpTokenizer(node: _Tokenizer) -> str:
    items = list()
    iterator = 0
    new = '\n'
    for token in _Tokenize(_generate_tokens(_StringIO(node.text).readline)):
        item = f"{_colors.Red}{iterator}:\t{_colors.Yellow}{token.type}\t{tok_name[token.type]}"
        item = item.ljust(30, ' ') + f"\t{_colors.White}{token.string if token.string != new else ''}"
        items.append(item)
        iterator += 1
    return '\n'.join(items)


def dumpAST(module: _kiwi.Module, minimalistic=False) -> str:
    tab = ' ' * 3
    new = '\n'

    def f(node, lvl=1, color=_kiwi.AST.color) -> str:
        if isinstance(node, Attr):
            node = _kiwi.Token(..., ..., '.'.join(map(str, node)))
        if isinstance(node, list):
            if len(node) == 0:
                return f'{color}{"" if minimalistic else "[]"}'
            prefix = f"\n{tab * lvl}" if len(node) > 1 else ""
            return f'{color}{"" if minimalistic else "["}{"" if minimalistic else prefix}' \
                   f'{(", " + new + tab * lvl).join(map(lambda x:f(x, lvl + 1, color), node))}' \
                   f'{color}{"" if minimalistic else "]"}'
        if isinstance(node, _kiwi.Token):
            ast_color = color if node.color is None else node.color
            return f'{ast_color} {node} {color}'
        if isclass(node):
            return _colors.Yellow + node.__name__
        if node.__class__.__name__ == 'Construct':
            return f'{_colors.Cyan}{node.method}{_colors.White} -> ' \
                   f'{f(node.parent, lvl=lvl, color=color)}\n{tab*lvl}' \
                   f'{color}{f(node.arguments, lvl=lvl, color=color)}{color}'
        if isinstance(node, _kiwi.AST):
            ast_color = color if node.color is None else node.color
            try:
                ans = list(node.__annotations__)
            except AttributeError:
                ans = []
            items = [f'\n{tab * lvl}{ans[i]}='
                     f'{f(node.__getattribute__(ans[i]), lvl + 1, ast_color)}' for i in range(len(ans))]
            return f'{ast_color}{node.__class__.__name__}({", ".join(items)}){color}'
        return _colors.White + str(node) + color

    return f(module) + _colors.ResetAll


def dumpScopeSystem(scope: ScopeSystem):
    def f(node: Any, col=_colors.Cyan + _colors.BackgroundDefault, level=1):
        tab = ' ' * 4
        if isinstance(node, ScopeType):
            items = list()
            for key in node.content.keys():
                prefix = str()
                if key in node.hide:
                    prefix = _colors.Black + _colors.BackgroundWhite + " private " + _colors.BackgroundDefault + " "
                if isinstance(node.content[key], ScopeType):
                    items.append(f"\n{tab * level}{prefix}{_colors.Red}{key}" + f(node.content[key],
                                                                                  level=level + 1,
                                                                                  col=col))
                    continue
                items.append(f"\n{tab * level}"
                             f"{prefix}{_colors.Yellow}{key} {_colors.Blue + _colors.BackgroundDefault}={col} "
                             f"{f(node.content[key], level=level + 1, col=col)}")
            return f'{_colors.Red} is {{{", ".join(items)}{_colors.Red}}}'
        if isinstance(node, _kiwi.AST):
            items = list()
            for key in node.__annotations__:
                items.append(f"\n{tab * level}"
                             f"{_colors.Yellow}{key} {_colors.Blue}={col} "
                             f"{f(node.__getattribute__(key), level=level + 1, col=col)}")
            return f'{_colors.White}AST({", ".join(items)}{_colors.White})'
        if isclass(node):
            return f'{_colors.Magenta + _colors.BackgroundBlack} {node.__name__} ' \
                   f'{_colors.Default + _colors.BackgroundDefault}'
        return "instance of " + _colors.White + "%.32s" % node.__class__.__name__ + \
               ('...' if len(str(node.__class__.__name__)) > 32 else '') + col

    return _colors.Red + 'globals' + f(scope.globalScope) + _colors.ResetAll


@_dataclass
class AST_Task:
    function: Callable
    args: List[Any]


class AST_Visitor:
    @staticmethod
    def getAttributes(node: _kiwi.AST):
        try:
            targets = node.__annotations__
        except AttributeError:
            return [], []
        for annotation in targets:
            attribute = node.__getattribute__(annotation)
            yield annotation, attribute

    def knockCall(self, node: Any) -> Callable[[Any], None]:
        name = node.__class__.__name__
        if name in dir(self):
            return self.__getattribute__(name)

    def unpackTuple(self, value: tuple) -> tuple:
        if len(value) == 0:
            return tuple()
        try:
            return self.unpackTuple(tuple(chain.from_iterable(value)))
        except TypeError:
            return value

    _no_references = 0
    _tasks: List[list] = list()
    _currentIndex: List[int] = list()

    def getLastCommands(self, index: int = 0) -> List[Any]:
        return self._tasks[-(1 + index)][self._currentIndex[-(1 + index)] + 1:]

    def replaceLastCommands(self, commands: List[Any], index: int = 0):
        self._tasks[-(1 + index)] = self._tasks[-(1 + index)][:self._currentIndex[-(1 + index)] + 1]
        self._tasks[-(1 + index)].extend(commands)

    def visit(self, node: Any, no_references=False) -> Any:
        self._no_references += no_references
        if isinstance(node, list):
            result = list()
            self._tasks.append(node)
            self._currentIndex.append(0)
            while self._currentIndex[-1] < len(self._tasks[-1]):
                visited = self.visit(self._tasks[-1][self._currentIndex[-1]])
                self._currentIndex[-1] += 1
                if isinstance(visited, tuple):
                    result.extend(self.unpackTuple(visited))
                    continue
                if visited is None:
                    continue
                result.append(visited)
            self._no_references -= no_references
            self._currentIndex.pop(-1)
            self._tasks.pop(-1)
            return result
        if isinstance(node, _kiwi.Token):
            if function := self.knockCall(node):
                result = function(node)
                self._no_references -= no_references
                return result
            self._no_references -= no_references
            return node
        if isinstance(node, _kiwi.AST):
            if function := self.knockCall(node):
                result = function(node)
                self._no_references -= no_references
                return result
            for annotation, attribute in self.getAttributes(node):
                visited = self.visit(attribute)
                node.__setattr__(annotation, visited)
            self._no_references -= no_references
            return node
        if isinstance(node, AST_Task):
            return node.function(*node.args)

    def visitAST(self, node: _kiwi.AST | _kiwi.Token) -> List[Any]:
        result = list()
        for annotation, attribute in self.getAttributes(node):
            result.append(self.visit(attribute))
        return result
