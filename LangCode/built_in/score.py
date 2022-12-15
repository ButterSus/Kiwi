from __future__ import annotations

# Default libraries
# -----------------

from typing import Type  # noqa: F401
from functools import reduce  # noqa: F401

# Custom libraries
# ----------------

from LangCode import *
from LangCode.constant import *
from Kiwi.components.kiwiASO import String as TokenString


class Scoreboard(Variable):
    criteria: String

    def InitsType(self, attr: Attr, address: Attr, criteria: String = None) -> Scoreboard:
        # Handle <ADDRESS>
        # ----------------

        assert isinstance(address, Attr)
        self.address = address

        # Handle <NAME>
        # -------------

        assert isinstance(attr, Attr)
        self.attr = attr

        # Handle <CRITERIA>
        # -----------------

        if criteria is None:
            criteria = String(self.api).Formalize(TokenString(..., ..., '"dummy"'))
        assert isinstance(criteria, String)
        self.criteria = criteria

        self.api.system(ScoreboardObjectiveCreate(
            name=self.attr.toString(),
            criteria=self.criteria.value
        ))
        return self


class ScoreboardClass(Class):
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass

    def GetChild(self) -> Scoreboard:
        return Scoreboard(self.api)
