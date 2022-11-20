"""
This code is unlicensed
By ButterSus

Built-in types, structures, function, etc.
"""


from __future__ import annotations

from typing import Type
from abc import ABC, abstractmethod


class KiwiType(ABC):
    @abstractmethod
    def Add(self, other: KiwiObj) -> KiwiObj:
        ...

    @abstractmethod
    def Sub(self, other: KiwiObj) -> KiwiObj:
        ...


KiwiObj = Type[KiwiType]


# DATA TYPES
# ==========


class Score(KiwiType):
    name: str
    scoreboard: Scoreboard

    def __init__(self, name: str, scoreboard: Scoreboard):
        self.name = name
        self.scoreboard = scoreboard

    def Add(self, other: KiwiObj) -> KiwiObj:
        pass

    def Sub(self, other: KiwiObj) -> KiwiObj:
        pass


class Scoreboard(KiwiType):
    name: str
    criteria: str

    def __init__(self, name: str, criteria: str):
        self.name = name
        self.criteria = criteria

    def Add(self, other: KiwiObj) -> KiwiObj:
        pass

    def Sub(self, other: KiwiObj) -> KiwiObj:
        pass


built_in_dict = {
    "score": Score,
    "scoreboard": Scoreboard
}
