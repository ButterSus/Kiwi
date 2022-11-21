from __future__ import annotations

# Default libraries
# -----------------

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

# Custom libraries
# ----------------

if TYPE_CHECKING:
    from src.kiwiAnalyzer import Argument
    from src.kiwiCompiler import Compiler
    from src.assets.kiwiCommands import Command
    from build import Constructor


class KiwiType:
    pass


class KiwiConst(KiwiType, ABC):
    value: str

    @abstractmethod
    def __init__(self, value: str, *_):
        self.value = value

    @abstractmethod
    def toDisplay(self) -> str:
        pass


class KiwiSpace(KiwiType, ABC):
    name: str
    constructor: Constructor

    @abstractmethod
    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    @abstractmethod
    def Annotation(self, compiler: Compiler, body: List[Command]):
        pass


class KiwiClass(KiwiType, ABC):
    name: str
    constructor: Constructor

    @abstractmethod
    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    @abstractmethod
    def Annotation(self, *args: Argument):
        pass

    @abstractmethod
    def Assignment(self, *args: Argument):
        pass

    @abstractmethod
    def toDisplay(self) -> str:
        pass


StdOps = {
    '=': 'Assignment'
}
