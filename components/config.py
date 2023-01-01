"""
This module contains all options in terminal and configuration file
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Any, TypedDict, List
from pathlib import Path
from argparse import ArgumentParser

# Custom libraries
# ----------------

import toml
import components.kiwiColors as colors

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
    "include_directories": ["src"],
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
    "description": "#Made by using Frontend Compiler",
    "entry_file": "main",
    "mc_version": "1.18.2"
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
        if self.arguments['create_project']:
            self.configGeneral = dict()
            self.configGeneral |= self.arguments
            return
        self.get_options()

    def get_arguments(self):
        self.argparser = ArgumentParser(description='Frontend Datapack Official Compiler')
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

        project_toml = self.pathGeneral / 'kiwi_project.toml'
        if not project_toml.exists():
            print(f'{colors.Red}File kiwi_project.toml not found in project directory\n'
                  f'To fix this, try create project using --create-project attribute{colors.Default}')
            exit(1)

        currentConfigTOML: ConfigTOML \
            = DefaultDict(configTOML, toml.load(str(project_toml)))
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