from frontend import KiwiAST

from typing import Iterator
from io import StringIO
import tokenize

from pegen.parser import Tokenizer


def kiwiTokenizer(stream: Iterator[tokenize.TokenInfo], debugMode: bool):
    for tok in stream:
        if tok.type == 4 or tok.type == 62:
            result = next(stream)
            while result.type == 62:
                if debugMode:
                    print(tok)
                yield tok
                if debugMode:
                    print(result)
                yield result
                if debugMode:
                    print(tok)
                yield tok
                result = next(stream)
            if result.type == 6:
                while result.type == 6:
                    if debugMode:
                        print(tok)
                    yield tok
                    if debugMode:
                        print(result)
                    yield result
                    if debugMode:
                        print(tok)
                    yield tok
                    result = next(stream)
            else:
                if debugMode:
                    print(tok)
                yield tok
                if debugMode:
                    print(result)
                yield result
                continue
            if debugMode:
                print(result)
            yield result
            continue
        if debugMode:
            print(tok)
        yield tok


def parse(kiwiProgram: str, *, debugMode=False) -> KiwiAST.Module:
    from frontend.KiwiParser import KiwiParser
    tokengen = tokenize.generate_tokens(StringIO(kiwiProgram).readline)
    tokenizer = Tokenizer(kiwiTokenizer(tokengen, debugMode=debugMode))
    parser = KiwiParser(tokenizer)
    return parser.start()


_newline = '\n'


def dump(ast: KiwiAST.AST | list, level=1, color=KiwiAST.AST.color, *, indent=4):
    _tabulation = ' ' * indent
    if isinstance(ast, list):
        ast_color = color
        return f'[{(", " + _newline + _tabulation*level).join(map(lambda x: dump(x, level+1, ast_color), ast))}]'
    if not isinstance(ast, KiwiAST.AST) and not isinstance(ast, KiwiAST.Token):
        return str(ast)
    try:
        annotations = list(ast.__annotations__)
    except AttributeError:
        annotations = list()
    if isinstance(ast, KiwiAST.Token):
        ast: ast | KiwiAST.Theme_Undefined
        ast_color = color if ast.color is None else ast.color
        return f'{ast_color} {ast} {color}'
    length = len(annotations)
    ast_color = color if ast.color is None else ast.color
    items = [f"{_newline}{_tabulation*level}{annotations[i]}={dump(ast.__getattribute__(annotations[i]), level+1, ast_color)}" for i in range(length)]
    name = ast.__class__.__name__
    return f'{ast_color}{name}' \
           f'({", ".join(items)}){color}'
