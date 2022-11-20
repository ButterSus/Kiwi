from __future__ import annotations

# Default libraries
# -----------------

import toml
import json
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import TypedDict, Any, List
from pathlib import Path

# Custom libraries
# ----------------

from src.kiwiTokenizer import Tokenizer
from src.kiwiAST import AST
from src.kiwiAnalyzer import Analyzer
from src.assets.kiwiTools import dumpAST, dumpTokenizer, dumpScopeSystem


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


configTOML: ConfigTOML = {
    "project": configProject,
    "options": configOptions
}


# Terminal arguments
# ------------------

class ConfigTerminal(TypedDict):
    path: str
    debug: bool
    create_project: bool


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
        currentConfigOptions: ConfigOptions \
            = DefaultDict(configOptions, currentConfigTOML['options'])
        self.configGeneral = combineDictionaries(
            self.arguments, currentConfigProject, currentConfigOptions)
        self.configGeneral['include_directories'].append('./')


# General directories
# -------------------

class Directories:
    bin: Path
    data: Path
    project: Path
    functions: Path


class Constructor:
    """
    The main task of this class is
    - construct base for compiler
    """

    configGeneral: ConfigGeneral
    directories: Directories

    def __init__(self, configGeneral: ConfigGeneral):
        self.configGeneral = configGeneral
        self.directories = Directories()
        self.folders()
        self.files()

    def folders(self):
        self.directories.bin = Path(self.configGeneral['output_directory'])
        self.directories.bin.mkdir(exist_ok=True)

        self.directories.data = Path(self.directories.bin / 'data')
        self.directories.data.mkdir(exist_ok=True)

        self.directories.project = Path(self.directories.data / self.configGeneral['project_name'])
        self.directories.project.mkdir(exist_ok=True)

        self.directories.functions = Path(self.directories.project / 'functions')
        self.directories.functions.mkdir(exist_ok=True)

    def files(self):
        with (self.directories.bin / 'pack.mcmeta').open('w+') as file:
            file.write(json.dumps({
                "pack": {
                    "pack_format": self.get_pack(self.configGeneral['mc_version']),
                    "description": (self.configGeneral['description'])
                }
            }, indent=4))

    def get_pack(self, version: str) -> int:
        version = list(map(int, version.split('.')))
        version = [version[i] if i < len(version) else 0 for i in range(3)]
        match version:
            case [1, 13, x] if 2 >= x >= 0:
                return 4
            case [1, 14, x] if 4 >= x >= 0:
                return 4
            case [1, 15, x] if 2 >= x >= 0:
                return 5
            case [1, 16, x] if 1 >= x >= 0:
                return 5
            case [1, 16, x] if 5 >= x >= 2:
                return 6
            case [1, 17, x] if 1 >= x >= 0:
                return 7
            case [1, 18, x] if 1 >= x >= 0:
                return 8
            case [1, 18, 2]:
                return 9
            case [1, 19, x] if 2 >= x >= 0:
                return 10
        return -1


@dataclass
class Module:
    tokenizer: Tokenizer
    ast: AST
    analyzer: Analyzer


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

    def getPath(self, directory: str) -> Path:
        for directory in map(lambda x: x / directory, self.include_directories):
            if directory.exists():
                return directory
            if not directory.suffix:
                directory = directory.with_suffix('.kiwi')
                if directory.exists():
                    return directory
        assert False

    def openModule(self, directory: Path) -> Module:
        with directory.open() as file:
            tokenizer = Tokenizer(file.read())
            ast = AST(tokenizer.lexer)
            libScope = dict()
            for alias in ast.module.imports:
                libScope[alias.as_name] = self.openModule(
                    self.getPath(alias.directory)
                ).analyzer.scope.globalScope
            analyzer = Analyzer(ast, libScope)
            return Module(tokenizer, ast, analyzer)


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
    moduleWirer: ModuleWirer

    # General parameters
    # ------------------

    configGeneral: ConfigGeneral

    def __init__(self):
        self.terminal = Terminal()
        self.configGeneral = self.terminal.configGeneral
        self.constructor = Constructor(self.configGeneral)

        # Entry file initialization
        # -------------------------

        self.moduleWirer = ModuleWirer(self.configGeneral['entry_file'], self.configGeneral)
        self.tokenizer = self.moduleWirer.module.tokenizer
        self.ast = self.moduleWirer.module.ast
        self.analyzer = self.moduleWirer.module.analyzer

        print(dumpScopeSystem(self.analyzer.scope))


if __name__ == '__main__':
    Builder()
