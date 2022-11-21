from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, TextIO
from pathlib import Path
from std import *
from shutil import rmtree
import json

# Custom libraries
# ----------------

if TYPE_CHECKING:
    from build import ConfigGeneral


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
        self.interface()

    def folders(self):
        """
        Folders initialization
        """

        self.directories.bin = Path(self.configGeneral['output_directory'])
        rmtree(self.directories.bin)
        self.directories.bin.mkdir(exist_ok=True)

        self.directories.data = Path(self.directories.bin / 'data')
        self.directories.data.mkdir(exist_ok=True)

        self.directories.project = Path(self.directories.data / self.configGeneral['project_name'])
        self.directories.project.mkdir(exist_ok=True)

        self.directories.functions = Path(self.directories.project / 'functions')
        self.directories.functions.mkdir(exist_ok=True)

    def files(self):
        """
        File initialization: pack.mcmeta
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
                    "pack_format": get_pack(self.configGeneral['mc_version']),
                    "description": (self.configGeneral['description'])
                }
            }, indent=4))

    def finish(self):
        self.closeFunction()

    # Interface for compiler
    # ----------------------

    fileStack: List[TextIO] = []

    def interface(self):
        self.newFunction('init')
        self.scoreboard = Scoreboard('globals', self)
        self.scoreboard.Annotation(String('\"dummy\"', self))

    def newFunction(self, name: str):
        self.fileStack.append((self.directories.functions / name).with_suffix('.mcfunction').open('w+'))

    def closeFunction(self):
        self.fileStack[-1].close()
        self.fileStack.pop(-1)

    def cmd(self, text: str):
        self.fileStack[-1].write(text)

    # Default attributes
    # ------------------

    scoreboard: Scoreboard
    criteria: String = String('\"dummy\"')
    prefix_space: str = ''
