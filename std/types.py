from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from std.tools import *

if TYPE_CHECKING:
    from src.kiwiAnalyzer import Argument
    from src.kiwiCompiler import Compiler
    from src.assets.kiwiCommands import Command
    from build import Constructor


# DATA TYPES
# ==========


class Number(KiwiConst):
    value: int

    def __init__(self, value: str, *_):
        self.value = int(value)

    def toDisplay(self) -> str:
        return f'{{"text": "{self.value}"}}'


class String(KiwiConst):
    value: str

    def __init__(self, value: str, *_):
        """
        Should accept it with quotes
        """
        self.value = value

    def toDisplay(self) -> str:
        return f'{{"text": "{self.value}"}}'

    def toName(self) -> str:
        return self.value[1:-1]


class Score(KiwiClass):
    name: str
    scoreboard: Scoreboard
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, scoreboard: Scoreboard = None):
        if scoreboard is None:
            scoreboard = self.constructor.scoreboard
        self.scoreboard = scoreboard

    def Assignment(self, value: Argument):
        self.constructor.cmd(f'scoreboard players set '
                             f'{self.name} {self.scoreboard.name} {value.value}')

    def toDisplay(self) -> str:
        pass


class Scoreboard(KiwiClass):
    name: str
    criteria: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, criteria: String = None):
        if criteria is None:
            criteria = self.constructor.criteria
        self.criteria = criteria.toName()
        self.constructor.cmd(f'scoreboard objectives add '
                             f'{self.name} {self.criteria}')

    def Assignment(self, value: Argument):
        """
        You can't assign scoreboard, because it's like a type
        """
        assert False

    def toDisplay(self) -> str:
        pass


class Namespace(KiwiSpace):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, compiler: Compiler, body: List[Command]):
        pass


class Function(KiwiSpace):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, compiler: Compiler, body: List[Command]):
        self.constructor.newFunction(self.name)
        compiler.visit(body)
        self.constructor.closeFunction()

