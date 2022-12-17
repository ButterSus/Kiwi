"""
Copyright (c) 2022 Krivoshapkin Edward

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
    value: str

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
        return f'tellraw {self.selector} {dumps(self.text)}'


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
