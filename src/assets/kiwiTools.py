from __future__ import annotations

# Default libraries
# -----------------

from typing import Any, List, Callable
from inspect import isclass
from tokenize import tok_name

# Custom libraries
# ----------------

import src.assets.kiwiColors as colors
import src.assets.kiwiASO as kiwi
from src.kiwiTokenizer import Tokenize, generate_tokens, StringIO, Tokenizer


def dumpTokenizer(node: Tokenizer) -> str:
    items = list()
    iterator = 0
    new = '\n'
    for token in Tokenize(generate_tokens(StringIO(node.text).readline)):
        item = f"{colors.Red}{iterator}:\t{colors.Yellow}{token.type}\t{tok_name[token.type]}"
        item = item.ljust(30, ' ') + f"\t{colors.White}{token.string if token.string != new else ''}"
        items.append(item)
        iterator += 1
    return '\n'.join(items)


def dumpAST(node: kiwi.Module) -> str:
    tab = ' ' * 4
    new = '\n'

    def f(node, lvl=1, color=kiwi.AST.color) -> str:
        if isinstance(node, list):
            if len(node) == 0:
                return '[]'
            return f'[\n{tab * lvl}{(", " + new + tab * lvl).join(map(lambda x:f(x, lvl + 1, color), node))}]'
        if isclass(node):
            return f'{colors.Cyan}<instance of {colors.Magenta+colors.BackgroundBlack} ' \
                   f'{node.__name__} {colors.BackgroundDefault + colors.Cyan}>{color}'
        if isinstance(node, kiwi.Token):
            ast_color = color if node.color is None else node.color
            return f'{ast_color} {node} {color}'
        if isinstance(node, kiwi.AST):
            ast_color = color if node.color is None else node.color
            try:
                ans = list(node.__annotations__)
            except AttributeError:
                ans = []
            items = [f'\n{tab * lvl}{ans[i]}='
                     f'{f(node.__getattribute__(ans[i]), lvl + 1, ast_color)}' for i in range(len(ans))]
            return f'{ast_color}{node.__class__.__name__}({", ".join(items)}){color}'
        return str(node)

    return f(node) + colors.ResetAll


class Visitor:
    def getAttributes(self, node: kiwi.AST):
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

    def visit(self, node: Any) -> Any:
        if isinstance(node, list):
            result = list()
            for item in node:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(visited)
                    continue
                if visited is None:
                    continue
                result.append(visited)
            return result
        if isinstance(node, kiwi.Token):
            if function := self.knockCall(node):
                return function(node)
            return node
        if isinstance(node, kiwi.AST):
            if function := self.knockCall(node):
                return function(node)
            for annotation, attribute in self.getAttributes(node):
                visited = self.visit(attribute)
                node.__setattr__(annotation, visited)
            return node

    def visitAST(self, node: kiwi.AST) -> List[Any]:
        result = list()
        for annotation, attribute in self.getAttributes(node):
            result.append(self.visit(attribute))
        return result
