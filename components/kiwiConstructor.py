"""
This module provides all objects to work with files.
It's used to generate datapack folders and files.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, TextIO, List, Any
from pathlib import Path
from shutil import rmtree
import json

# Custom libraries
# ----------------

if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi


def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa
    _Kiwi.init(_compiler, _LangApi, _Kiwi)


# General directories
# -------------------

class Directories:
    """
    This class is used to store main directories.
    """
    bin: Path
    data: Path
    project: Path
    functions: Path
    predicates: Path


class Attributes:
    """
    This class is used to store main attributes for API.
    """
    project: List[str]
    functions: List[str]
    predicates: List[str]


class Constructor:
    """
    This class is used to create a datapack file structure.
    It's final step of compiling a datapack.
    """

    config: compiler.ConfigGeneral
    attributes: Attributes
    directories: Directories
    builder: compiler.Builder

    def __init__(self, builder: compiler.Builder):
        self.builder = builder
        self.config = builder.configGeneral
        self.attributes = Attributes()
        self.directories = Directories()
        self.folders()
        self.files()

    def folders(self):
        """
        Folders initialization.
        """

        self.directories.bin = Path(self.config['output_directory'])
        rmtree(self.directories.bin, ignore_errors=True)
        self.directories.bin.mkdir(exist_ok=True)

        self.directories.data = Path(self.directories.bin / 'data')
        self.directories.data.mkdir(exist_ok=True)

        self.directories.project = Path(self.directories.data /
                                        LangApi.bytecode.convert_var_name(self.config['project_name']))
        self.directories.project.mkdir(exist_ok=True)

        self.directories.functions = Path(self.directories.project / 'functions')
        self.directories.functions.mkdir(exist_ok=True)

        self.directories.predicates = Path(self.directories.project / 'predicates')
        self.directories.predicates.mkdir(exist_ok=True)

        self.attributes.project = list(map(str, self.directories.project.relative_to(
            self.directories.data
        ).parts))
        self.attributes.functions = list(map(str, self.directories.functions.relative_to(
            self.directories.data
        ).parts))
        self.attributes.predicates = list(map(str, self.directories.predicates.relative_to(
            self.directories.data
        ).parts))

    def files(self):
        """
        Files initialization.
        But at the moment, there is only one file.
        """

        def get_pack(version: str) -> int:
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

        with (self.directories.bin / 'pack.mcmeta').open('w+') as file:
            file.write(json.dumps({
                "pack": {
                    "pack_format": get_pack(self.config['mc_version']),
                    "description": (self.config['description'])
                }
            }, indent=4))

    def create_file(self, path: Path, to_go: List[str]) -> TextIO:
        """
        This method takes <path> and <to_go>,
        concatenates <path> and <to_go> into a single directory,
        then returns you opened TextIO object.
        """
        if len(to_go) == 1:
            return (path / to_go[0]).open('a')
        result = path / to_go[0]
        result.mkdir(parents=True, exist_ok=True)
        return self.create_file(result, to_go[1:])

    def build(self):
        """
        Finally, this method is called.
        And the whole datapack is built into one
        powerful structure.
        """
        for codeScope in self.builder.api.code:
            for key, code in codeScope.code.items():
                self.create_file(self.directories.data, codeScope.toPath(key)).write(
                    '\n'.join(map(lambda x: x.toCode(), code))
                )
