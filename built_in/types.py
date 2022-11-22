from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from built_in.tools import *
from src.assets.kiwiReference import Reference

if TYPE_CHECKING:
    from src.kiwiAnalyzer import Argument, NonRef
    from src.kiwiCompiler import Compiler
    from src.assets.kiwiCommands import Command
    from build import Constructor


def toNonReference(value: Argument) -> NonRef:
    if isinstance(value, Reference):
        value = value.var
    return value


# DATA TYPES
# ==========


class Number(KiwiConst):
    value: int

    def __init__(self, value: str, *_):
        self.value = int(value)

    def Add(self, _other: Argument) -> NonRef:
        other = toNonReference(_other)
        if isinstance(other, Number):
            self.value += other.value
            return self
        return other.Add(self)

    def toDisplay(self) -> str:
        return f'{{"text": "{self.value}"}}'

    def toName(self) -> str:
        return str(self.value)


class String(KiwiConst):
    value: str

    def __init__(self, value: str, *_):
        """
        Should accept it with quotes
        """
        self.value = value

    def Add(self, _other: Argument) -> NonRef:
        other = toNonReference(_other)
        if isinstance(other, String):
            self.value += other.value
            return self
        return other.Add(self)

    def toDisplay(self) -> str:
        return f'{{"text": "{self.toName()}"}}'

    def toName(self) -> str:
        return self.value[1:-1]


class Score(KiwiClass):
    name: str
    scoreboard: Scoreboard
    prefix_space: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, scoreboard: Scoreboard = None):
        self.prefix_space = self.constructor.prefix_space
        if scoreboard is None:
            scoreboard = self.constructor.glScoreboard
        self.scoreboard = scoreboard

    def Assignment(self, value: Argument):
        value = toNonReference(value)
        self.constructor.cmd(f'scoreboard players set '
                             f'{self.toName()} {self.scoreboard.toName()} {value.toName()}')

    def Add(self, _other: Argument) -> NonRef:
        other = toNonReference(_other)
        if isinstance(other, Number):
            self.constructor.cmd(f'scoreboard players add '
                                 f'{self.toName()} {self.scoreboard.toName()} {other.toName()}')
            return self
        assert False

    def toDisplay(self) -> str:
        return f'{{"score":{{"name": "{self.toName()}", "objective": "{self.scoreboard.toName()}"}}}}'

    def toName(self) -> str:
        return f'{self.prefix_space}{self.name}'


class Scoreboard(KiwiClass):
    name: str
    criteria: str
    prefix_space: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, criteria: String = None):
        self.prefix_space = self.constructor.prefix_space
        if criteria is None:
            criteria = self.constructor.criteria
        self.criteria = criteria.toName()
        self.constructor.cmd(f'scoreboard objectives add '
                             f'{self.toName()} {self.criteria}')

    def Add(self, other: Argument) -> Argument:
        assert False

    def Assignment(self, value: Argument):
        """
        You can't assign scoreboard, because it's like a type
        """
        assert False

    def toDisplay(self) -> str:
        return f''

    def toName(self) -> str:
        return f'{self.prefix_space}{self.name}'


class Function(KiwiCallable):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, compiler: Compiler, body: List[Command]):
        self.constructor.newFunction(self.name)
        compiler.visit(body)
        self.constructor.closeFunction()

    def Call(self, compiler: Compiler, *args: Argument):
        self.constructor.cmd(
            f'function {self.constructor.configGeneral["project_name"]}:{self.name}'
        )


class Namespace(KiwiType):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, compiler: Compiler, body_private: List[Command],
                   body_public: List[Command], body_default: List[Command]):
        self.constructor.newNamespace(self.name)
        compiler.visit(body_default)
        self.constructor.closeNamespace()
