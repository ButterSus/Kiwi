from __future__ import annotations

# Default libraries
# -----------------

import toml
from time import time
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import TypedDict, Any, List
from pathlib import Path

import LangCode
from LangApi import API
# Custom libraries
# ----------------

from Kiwi.kiwiTokenizer import Tokenizer
from Kiwi.kiwiAST import AST
from Kiwi.components.kiwiConstructor import Constructor
from Kiwi.kiwiAnalyzer import Analyzer
from Kiwi.components.kiwiTools import dumpAST, dumpTokenizer, dumpScopeSystem


# Dict with default values
# ------------------------

class DefaultDict(dict):
    defaultDict: dict

    def __init__(self, defaultDict: dict, value: dict):
        self.defaultDict = defaultDict
        super().__init__(value)

    def __getitem__(self, item):
        return self.get(item)

    def get(self, __key: str) -> Any:
        result = super().get(__key)
        if result is None:
            return self.defaultDict.get(__key)
        return result

    def toDict(self) -> dict:
        for key in self.defaultDict.keys():
            self[key] = self.get(key)
        return dict(self)


# Config TOML
# -----------

class ConfigOptions(TypedDict):
    include_directories: List[str]
    entry_function: str
    output_directory: str
    default_scope: str


configOptions: ConfigOptions = {
    "include_directories": [],
    "entry_function": "main",
    "output_directory": "bin",
    "default_scope": "public"
}


class ConfigExtended(TypedDict):
    space_separator: str
    temporary: str


configExtended: ConfigExtended = {
    "space_separator": ".",
    "temporary": "TMP"
}


class ConfigProject(TypedDict):
    project_name: str
    description: str
    entry_file: str
    mc_version: str


configProject: ConfigProject = {
    "project_name": "untitled",
    "description": "#Made by using Kiwi Compiler",
    "entry_file": "main",
    "mc_version": "1.16.5"
}


class ConfigTOML(TypedDict):
    project: ConfigProject
    options: ConfigOptions
    extended: ConfigExtended


configTOML: ConfigTOML = {
    "project": configProject,
    "options": configOptions,
    "extended": configExtended
}


# Terminal arguments
# ------------------

class ConfigTerminal(TypedDict):
    path: str
    debug: bool
    minimalistic: bool
    create_project: bool
    update_grammar: bool


# General config
# --------------

class ConfigGeneral(ConfigProject, ConfigOptions, ConfigTerminal):
    pass


class Terminal:
    """
    The main task of this class is
    - collect build options for frontend and backend without checking correctness
    """

    argparser: ArgumentParser
    arguments: ConfigTerminal
    configGeneral: ConfigGeneral
    pathGeneral: Path

    # Config options
    # --------------

    def __init__(self):
        self.get_arguments()
        self.get_options()

    def get_arguments(self):
        self.argparser = ArgumentParser(description='Kiwi Datapack Official Compiler')
        self.argparser.add_argument('path', type=str, help='Path to your project')
        self.argparser.add_argument('--debug', default=False, action='store_true',
                                    help='Compiles grammar and print details (for devs)')
        self.argparser.add_argument('--create-project', default=False, action='store_true',
                                    help='Creates new project')
        self.argparser.add_argument('--update-grammar', default=False, action='store_true',
                                    help='Updates grammar')
        self.argparser.add_argument('--minimalistic', default=False, action='store_true',
                                    help='Less debug code (for devs)')
        self.arguments = vars(self.argparser.parse_args())
        self.pathGeneral = Path(self.arguments['path'])

    def get_options(self):
        def combineDictionaries(*values: DefaultDict | dict) -> dict:
            result = dict()
            for value in values:
                if isinstance(value, DefaultDict):
                    result |= value.toDict()
                else:
                    result |= value
            return result

        currentConfigTOML: ConfigTOML \
            = DefaultDict(configTOML, toml.load(str(self.pathGeneral / 'kiwi_project.toml')))
        currentConfigProject: ConfigProject \
            = DefaultDict(configProject, currentConfigTOML['project'])
        currentConfigExtended: ConfigExtended \
            = DefaultDict(configExtended, currentConfigTOML['extended'])
        currentConfigOptions: ConfigOptions \
            = DefaultDict(configOptions, currentConfigTOML['options'])
        self.configGeneral = combineDictionaries(
            self.arguments, currentConfigProject,
            currentConfigExtended, currentConfigOptions)
        self.configGeneral['include_directories'].append('./')


@dataclass
class Module:
    """
    Contains all information for compiler
    """

    tokenizer: Tokenizer
    ast: AST
    analyzer: Analyzer
    api: API


class ModuleWirer:
    """
    The main task of this class is
    - build one big empire of modules
    """

    directory: str
    configGeneral: ConfigGeneral
    include_directories: List[Path]
    module: Module

    def __init__(self, directory: str, configGeneral: ConfigGeneral):
        self.directory = directory
        self.configGeneral = configGeneral
        self.include_directories = list(map(Path, self.configGeneral['include_directories']))
        self.module = self.openModule(self.getPath(directory))
        self.module.api.visit(self.module.ast.module.body)

    def getPath(self, file_name: str) -> Path:
        """
        Returns full path of file
        """
        for path in map(lambda x: x / file_name, self.include_directories):
            if not path.suffix:
                path = path.with_suffix('.kiwi')
            if path.exists():
                return path
        assert False

    def openModule(self, directory: Path) -> Module:
        with directory.open() as file:
            # AST generation
            # --------------

            tokenizer = Tokenizer(file.read())
            ast = AST(tokenizer.lexer)

            # Libraries importing
            # -------------------

            # libScope = dict()
            # for alias in ast.module.imports:
            #     # If used <from ... import ...>
            #     # -----------------------------
            #
            #     if isinstance(alias.as_name, list):
            #         result = self.openModule(
            #             self.getPath(alias.directory)
            #         ).analyzer.scope
            #
            #         for fromAlias in alias.as_name:
            #             fromAlias: kiwi.Alias
            #             found_content = result.globalScope.get(fromAlias.directory, ignoreScope=False)
            #             libScope[fromAlias.as_name] = found_content
            #             if isinstance(found_content, ScopeType):
            #                 libScope[f'.{fromAlias.as_name}'] = result.globalScope.get(fromAlias.directory)
            #         continue
            #
            #     # If not used
            #     # -----------
            #
            #     libScope[alias.as_name] = self.openModule(
            #         self.getPath(alias.directory)
            #     ).analyzer.scope.globalScope
            #
            #     libScope[f'.{alias.as_name}'] = Namespace(
            #         f'.{alias.as_name}',
            #         self.constructor
            #     )

            # Compiling process
            # -----------------

            if self.configGeneral['debug']:
                print(dumpAST(ast.module, minimalistic=self.configGeneral['minimalistic']))

            analyzer = Analyzer(ast, dict(), self.configGeneral)
            return Module(tokenizer, analyzer.ast, analyzer, analyzer.api)


class Builder:
    """
    The main task of this class is
    - connect all parts of compiler together
    """

    # Parts of compiler
    # -----------------

    terminal: Terminal
    constructor: Constructor
    tokenizer: Tokenizer
    ast: AST
    analyzer: Analyzer
    api: API
    moduleWirer: ModuleWirer

    # General parameters
    # ------------------

    configGeneral: ConfigGeneral

    def __init__(self):
        self.terminal = Terminal()
        self.configGeneral = self.terminal.configGeneral

        if self.configGeneral['update_grammar']:
            from subprocess import run, DEVNULL
            run(
                f'python -m pegen {Path(__file__).parent / "Kiwi/components/kiwi.gram"} -o'
                f' {Path(__file__).parent / "Kiwi/kiwiAST.py"} -v'.split(),
                stdout=DEVNULL
            )

        # Entry file initialization
        # -------------------------

        self.moduleWirer = ModuleWirer(self.configGeneral['entry_file'], self.configGeneral)

        # Only for debugging (POST)
        # -------------------------

        self.tokenizer = self.moduleWirer.module.tokenizer
        self.ast = self.moduleWirer.module.ast
        self.analyzer = self.moduleWirer.module.analyzer
        self.api = self.moduleWirer.module.api

        if self.configGeneral['debug']:
            print(dumpTokenizer(self.tokenizer))
            print(dumpAST(self.ast.module, minimalistic=self.configGeneral['minimalistic']))
            print(dumpScopeSystem(self.analyzer.scope))

        self.constructor = Constructor(self.configGeneral)
        LangCode.built_codeFinish(self.api)
        self.build()

        if self.configGeneral['debug']:
            self.configGeneral['output_directory'] = 'bin'
            self.constructor = Constructor(self.configGeneral)
            self.build()

    def build(self):
        for codeScope in self.api.code:
            (self.constructor.directories.
             functions / LangCode.convert_var_name(codeScope.name)).with_suffix('.mcfunction').open('a') \
                .write('\n'.join(map(lambda x: x.toCode(), codeScope.code)))


if __name__ == '__main__':
    time_start = time()
    Builder()
    print('Compiled successfully in %6f seconds' % (time() - time_start))
