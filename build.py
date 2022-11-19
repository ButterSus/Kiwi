"""
This code is unlicensed
By ButterSus

Project builder

About Project:
    KiwiSusCompiler is compiler for Kiwi language.
    Kiwi language is used to describe datapack of Minecraft.

    Pros:
        - Import system
        - Function described in one file
        - Conditions
        - Better expressions
        - Namespaces

Also check our IDE:
    KiwiIDE - is the official IDE for Kiwi language:
        https://github.com/ButterSus/KiwiIDE
"""


import toml

from time import time
from typing import TypedDict, Optional, List
from frontend.KiwiAnalyzer import KiwiAnalyzer


class ConfigOptions(TypedDict):
    include_directories: Optional[List[str]]


class ConfigProject(TypedDict):
    project_name: str
    entry_file: str


class ConfigFile(TypedDict):
    project: ConfigProject
    options: Optional[ConfigOptions]


class Builder:
    """
    It just builds...
    """
    project: ConfigProject
    config: ConfigFile
    options: ConfigOptions

    def __init__(self, debug: bool = False):
        if debug:
            import subprocess
            import pathlib
            subprocess.run(
                f'python -m pegen {pathlib.Path(__file__).parent / "frontend/KiwiParser/grammar.gram"} -o'
                f' {pathlib.Path(__file__).parent / "frontend/KiwiParser/__init__.py"} -v'.split(),
                stdout=subprocess.DEVNULL
            )
        self.config = toml.load('kiwiProject.toml')
        self.project = self.config['project']
        self.options_init()
        KiwiAnalyzer(self, debug=True)

    def options_init(self):
        if (options := self.config['options']) is not None:
            self.options = options


if __name__ == '__main__':
    """
    If this project is on development,
    But you really want to try it out:
        Change value below <debug> to <False>
        "Builder(debug=False)".
        
        Then it will compile without debug features,
        but instead you get about 20x faster compiling speed
    """
    start_time = time()
    Builder(debug=True)
    print(
        f"Compiled without errors in %.6f seconds" % (time() - start_time)
    )
