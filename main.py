import toml

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
    project: ConfigProject
    config: ConfigFile
    options: ConfigOptions

    def __init__(self, updateGrammar: bool = False):
        if updateGrammar:
            import subprocess
            subprocess.run(
                'python -m pegen /home/buttersss/PycharmProjects/pegen/frontend/KiwiParser/grammar.gram -o'
                ' /home/buttersss/PycharmProjects/pegen/frontend/KiwiParser/__init__.py -v'.split(),
                stdout=subprocess.DEVNULL
            )
        self.config = toml.load('kiwiProject.toml')
        self.project = self.config['project']
        self.options_init()
        KiwiAnalyzer(self)

    def options_init(self):
        if (options := self.config['options']) is not None:
            self.options = options


if __name__ == '__main__':
    Builder(updateGrammar=True)
