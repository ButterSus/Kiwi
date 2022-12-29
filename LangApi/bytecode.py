"""
This module contains all minecraft commands,
which are used to be compiled into datapack.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import List, Dict, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from json import dumps

# Custom libraries
# ----------------

...

const_predicate_true = {
    "condition": "minecraft:value_check",
    "value": 1,
    "range": 1
}

const_predicate_false = {
    "condition": "minecraft:value_check",
    "value": 0,
    "range": 1
}


_double_slash = '\\\\'
_unary_slash = '\\'


NBTLiteral = Dict[str, Any] | List[Any]


def convert_var_name(name: str) -> str:
    mode = True
    result = str()
    for symbol in name:
        if mode == symbol.isupper():
            mode = not mode
            result += '-'
            symbol = symbol.lower()
        result += symbol
    return result


class CodeType(ABC):
    @abstractmethod
    def toCode(self) -> str:
        ...


@dataclass
class ScoreboardObjectiveCreate(CodeType):
    name: str
    criteria: str
    display_name: str = field(default=None)

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        if self.display_name is not None:
            return f'scoreboard objectives add {name} {self.criteria} {self.display_name}'
        return f'scoreboard objectives add {name} {self.criteria}'


@dataclass
class ScoreboardObjectiveSetDisplay(CodeType):
    type: str
    scoreboard: str

    def toCode(self) -> str:
        scoreboard = convert_var_name(self.scoreboard)
        return f'scoreboard objectives setdisplay {self.type} {scoreboard}'


@dataclass
class ScoreboardObjectiveRemove(CodeType):
    scoreboard: str

    def toCode(self) -> str:
        scoreboard = convert_var_name(self.scoreboard)
        return f'scoreboard objectives remove {scoreboard}'


@dataclass
class ScoreboardPlayersSet(CodeType):
    name: str
    scoreboard: str
    value: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        return f'scoreboard players set {name} {scoreboard} {self.value}'


@dataclass
class ScoreboardPlayersAdd(CodeType):
    name: str
    scoreboard: str
    value: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        return f'scoreboard players add {name} {scoreboard} {self.value}'


@dataclass
class ScoreboardPlayersRemove(CodeType):
    name: str
    scoreboard: str
    value: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        return f'scoreboard players remove {name} {scoreboard} {self.value}'


@dataclass
class ScoreboardPlayersOpAss(CodeType):
    name: str
    scoreboard: str
    other_name: str
    other_scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        other_name = convert_var_name(self.other_name)
        other_scoreboard = convert_var_name(self.other_scoreboard)
        return f'scoreboard players operation {name} {scoreboard} = ' \
               f'{other_name} {other_scoreboard}'


@dataclass
class ScoreboardPlayersOpIAdd(CodeType):
    name: str
    scoreboard: str
    other_name: str
    other_scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        other_name = convert_var_name(self.other_name)
        other_scoreboard = convert_var_name(self.other_scoreboard)
        return f'scoreboard players operation {name} {scoreboard} += ' \
               f'{other_name} {other_scoreboard}'


@dataclass
class ScoreboardPlayersOpISub(CodeType):
    name: str
    scoreboard: str
    other_name: str
    other_scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        other_name = convert_var_name(self.other_name)
        other_scoreboard = convert_var_name(self.other_scoreboard)
        return f'scoreboard players operation {name} {scoreboard} -= ' \
               f'{other_name} {other_scoreboard}'


@dataclass
class ScoreboardPlayersOpIMul(CodeType):
    name: str
    scoreboard: str
    other_name: str
    other_scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        other_name = convert_var_name(self.other_name)
        other_scoreboard = convert_var_name(self.other_scoreboard)
        return f'scoreboard players operation {name} {scoreboard} *= ' \
               f'{other_name} {other_scoreboard}'


@dataclass
class ScoreboardPlayersOpIDiv(CodeType):
    name: str
    scoreboard: str
    other_name: str
    other_scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        other_name = convert_var_name(self.other_name)
        other_scoreboard = convert_var_name(self.other_scoreboard)
        return f'scoreboard players operation {name} {scoreboard} /= ' \
               f'{other_name} {other_scoreboard}'


@dataclass
class ScoreboardPlayersOpIMod(CodeType):
    name: str
    scoreboard: str
    other_name: str
    other_scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        other_name = convert_var_name(self.other_name)
        other_scoreboard = convert_var_name(self.other_scoreboard)
        return f'scoreboard players operation {name} {scoreboard} %= ' \
               f'{other_name} {other_scoreboard}'


@dataclass
class ScoreboardPlayersReset(CodeType):
    name: str
    scoreboard: str

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        return f'scoreboard players reset {name} {scoreboard}'



@dataclass
class BossbarAdd(CodeType):
    identifier: str
    text: NBTLiteral

    def toCode(self) -> str:
        identifier = convert_var_name(self.identifier)
        return f'bossbar add {identifier} {dumps(self.text, ensure_ascii=False).replace(_double_slash, _unary_slash)}'

@dataclass
class FunctionDirectCall(CodeType):
    name: str

    def toCode(self) -> str:
        return f'function {convert_var_name(self.name)}'


@dataclass
class Execute(CodeType):
    steps: List[CodeType]

    def toCode(self) -> str:
        return f'execute {" ".join(map(lambda x: x.toCode(), self.steps))}'


@dataclass
class StepIfPredicate(CodeType):
    predicate: str

    def toCode(self) -> str:
        return f'if predicate {convert_var_name(self.predicate)}'


@dataclass
class StepIfScoreMatch(CodeType):
    name: str
    scoreboard: str
    value: str | int

    def toCode(self) -> str:
        name = convert_var_name(self.name)
        scoreboard = convert_var_name(self.scoreboard)
        return f'if score {name} {scoreboard} matches {self.value}'


@dataclass
class StepRun(CodeType):
    step: CodeType

    def toCode(self) -> str:
        return f'run {self.step.toCode()}'


@dataclass
class Tellraw(CodeType):
    selector: str
    text: str | List[NBTLiteral]

    def toCode(self) -> str:
        return f'tellraw {self.selector} {dumps(self.text).replace(_double_slash, _unary_slash)}'


@dataclass
class RawCommand(CodeType):
    text: str

    def toCode(self) -> str:
        return self.text


@dataclass
class RawJSON(CodeType):
    json: NBTLiteral

    def toCode(self) -> str:
        return dumps(self.json, indent=4)
