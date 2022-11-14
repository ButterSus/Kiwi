from frontend import KiwiAST

import tokenize
import subprocess

from pegen.parser import Tokenizer


def parse(kiwiFile: str, updateGrammar: bool = False) -> KiwiAST.Module:
    if updateGrammar:
        subprocess.run(
            "python -m pegen frontend/KiwiParser/grammar.gram -o frontend/KiwiParser/__init__.py -v".split(),
            stdout=subprocess.DEVNULL
        )
    from frontend.KiwiParser import KiwiParser
    with open(kiwiFile) as module:
        tokengen = tokenize.generate_tokens(module.readline)
        tokenizer = Tokenizer(tokengen)
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
        return f'{ast_color}<{ast}>{color}'
    length = len(annotations)
    ast_color = color if ast.color is None else ast.color
    items = [f"{_newline}{_tabulation*level}{annotations[i]}={dump(ast.__getattribute__(annotations[i]), level+1, ast_color)}" for i in range(length)]
    name = ast.__class__.__name__
    return f'{ast_color}{name}' \
           f'({", ".join(items)}){color}'
