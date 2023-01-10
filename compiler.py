"""
This module is the entry point of Kiwi Compiler.
It calls all other modules.
"""

from __future__ import annotations

# Default libraries
# -----------------

from time import time
from typing import List
from pathlib import Path

# Custom libraries
# ----------------

import components.kiwiConstructor as KiwiConstructor
from components.kiwiTools import (
    dumpAST, dumpTokenizer, dumpScopeSystem, getSomeModule
)
from components.config import Terminal, ConfigGeneral
import components.kiwiColors as colors

from frontend.kiwiTokenizer import Tokenizer
from frontend.kiwiParser import AST
import frontend.kiwiAnalyzer as kiwiAnalyzer
import toml
import LangApi
import Kiwi


# Initialization of modules
# -------------------------

def init():
    KiwiConstructor.init(getSomeModule(__name__), LangApi, Kiwi)
    kiwiAnalyzer.init(getSomeModule(__name__), LangApi, Kiwi)
    LangApi.api.init(getSomeModule(__name__), LangApi, Kiwi)


class Builder:
    """
    The main task of this class is
    - connect all parts of compiler together
    """

    # Parts of compiler
    # -----------------

    terminal: Terminal
    constructor: KiwiConstructor.Constructor

    tokenizer: Tokenizer
    ast: AST
    analyzer: kiwiAnalyzer.Analyzer
    api: LangApi.api.API

    # General parameters
    # ------------------

    configGeneral: ConfigGeneral
    include_directories: List[Path]

    def getPath(self, file_name: str) -> Path:
        """
        This method returns the absolute path of the given file,
        Also, it tries to find the file in the include_directories.
        """
        for path in map(lambda x: x / file_name, self.include_directories):
            path = Path(self.configGeneral['path']) / path
            if not path.suffix:
                path = path.with_suffix('.kiwi')
            if path.exists():
                return path
        assert False

    def openModule(self, directory: Path) -> tuple[Tokenizer, AST, kiwiAnalyzer.Analyzer, LangApi.api.API]:
        """
        This method opens the module and returns the module components.
        """
        with directory.open() as file:
            text = file.read()
            tokenizer = Tokenizer(text)
            try:
                ast = AST(tokenizer.lexer)
            except SyntaxError as e:
                print(f'{colors.Red}Kiwi Error System:')
                print(f'  File "{directory.absolute()}", line {e.lineno}')
                print(f'    {e.text}    {"^".rjust(e.offset)}\nSyntaxError: {e.msg}{colors.Default}')
                exit(1)
            assert ast.module is not None
            api = LangApi.api.API(self.constructor, self, tokenizer, ast)
            if self.configGeneral['debug']:
                print(dumpAST(ast.module))
            analyzer = kiwiAnalyzer.Analyzer(self.constructor, self, tokenizer, ast, api, text)
            analyzer.visit(ast.module)
            if self.configGeneral['debug']:
                print(dumpAST(ast.module, minimalistic = self.configGeneral['minimalistic']))
            api.visit(ast.module)
            return tokenizer, analyzer.ast, analyzer, api

    def __init__(self):
        self.terminal = Terminal()
        self.configGeneral = self.terminal.configGeneral

        if self.configGeneral['create_project']:
            path = Path(self.configGeneral['path'])
            path.mkdir(exist_ok=True)
            (path / 'src').mkdir(exist_ok=True)
            with (path / 'kiwi_project.toml').open('w+') as file:
                toml.dump({
                    'project': {
                        'project_name': 'untitled',
                        'description': '#Made by using Kiwi Compiler',
                        'entry_file': 'main',
                        'mc_version': '1.16.5'
                    },
                    'options': {
                        'include_directories': ['src'],
                        'entry_function': 'main',
                        'output_directory': 'bin',
                        'default_scope': 'public',
                        'space_separator': '.'
                    }
                }, file)
            with (path / 'src' / 'main.kiwi').open('w+') as file:
                file.write(
                    f'function main() <- load():\n{" "*4}pass  # Your code goes here'
                )
            print(f'Your project has been created in a few milliseconds, have fun! :D')
            exit(0)

        if self.configGeneral['update_grammar']:
            from subprocess import run, DEVNULL
            result = run(
                f'python -m pegen {Path(__file__).parent / "components/kiwi.gram"} -o'
                f' {Path(__file__).parent / "frontend/kiwiParser.py"} -v'.split(),
                stdout=DEVNULL
            )
            if result.returncode != 0:
                exit(1)

        # Entry file initialization
        # -------------------------

        self.constructor = KiwiConstructor.Constructor(self)
        self.include_directories = list(map(Path, self.configGeneral['include_directories']))
        self.tokenizer, self.ast, self.analyzer, self.api = self.openModule(
            self.getPath(
                self.configGeneral['entry_file']
            )
        )

        # Only for debugging
        # ------------------

        if self.configGeneral['debug']:
            print(dumpTokenizer(self.tokenizer))
            print(dumpScopeSystem(self.analyzer.scope))

        # Building project
        # ----------------

        self.constructor.build()

        if self.configGeneral['debug']:
            self.configGeneral['output_directory'] = 'bin'
            self.constructor = KiwiConstructor.Constructor(self)
            self.constructor.build()


if __name__ == '__main__':
    time_start = time()
    init()
    Builder()
    print('Compiled successfully in %6f seconds' % (time() - time_start))
