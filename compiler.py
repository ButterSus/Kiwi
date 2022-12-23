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
from components.kiwiTools import dumpAST, dumpTokenizer, dumpScopeSystem, getSomeModule
from components.config import Terminal, ConfigGeneral

from frontend.kiwiTokenizer import Tokenizer
from frontend.kiwiParser import AST
import frontend.kiwiAnalyzer as kiwiAnalyzer
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
            ast = AST(tokenizer.lexer)
            api = LangApi.api.API(self.constructor, self, tokenizer, ast)
            if self.configGeneral['debug']:
                print(dumpAST(ast.module))
            analyzer = kiwiAnalyzer.Analyzer(self.constructor, self, tokenizer, ast, api, text)
            analyzer.visit(ast.module)
            api.visit(ast.module)
            return tokenizer, analyzer.ast, analyzer, api

    def __init__(self):
        self.terminal = Terminal()
        self.configGeneral = self.terminal.configGeneral

        if self.configGeneral['update_grammar']:
            from subprocess import run, DEVNULL
            run(
                f'python -m pegen {Path(__file__).parent / "components/kiwi.gram"} -o'
                f' {Path(__file__).parent / "frontend/kiwiParser.py"} -v'.split(),
                stdout=DEVNULL
            )

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
            print(dumpAST(self.ast.module, minimalistic = self.configGeneral['minimalistic']))
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
