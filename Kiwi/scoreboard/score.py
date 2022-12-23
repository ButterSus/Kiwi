from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable

# Custom libraries
# ----------------

import LangApi
from components.kiwiScope import Attr


if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi


# Initialization of modules
# -------------------------

def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa


# Content of file
# ---------------


class Score(LangApi.abstract.Variable,
            LangApi.abstract.Assignable):
    attr: Attr
    address: Attr
    scoreboard: Kiwi.scoreboard.scoreboard.Scoreboard

    def InitsType(self, attr: Attr, address: Attr,
                  scoreboard: Kiwi.scoreboard.scoreboard.Scoreboard = None) -> Score:
        if scoreboard is None:
            scoreboard = Kiwi.scoreboard.scoreboard.Scoreboard.general
        self.attr = attr
        self.address = address
        self.scoreboard = scoreboard
        return self

    # temp = Kiwi.tokens.undefined.Undefined(self.analyzer, self.api).Formalize(
    #     self.api.prefix.SpecTemp()
    # ).Annotation(
    #     ScoreClass(self.analyzer, self.api).GetChild()
    # )

    def Assign(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(
                LangApi.bytecode.ScoreboardPlayersSet(
                    self.attr.toName(), self.scoreboard.attr.toName(),
                    str(other.value)
                )
            )
            return self
        assert False


class ScoreClass(LangApi.abstract.Class):
    def Call(self, *args: LangApi.abstract.Abstract):
        pass

    def GetChild(self) -> LangApi.abstract.Variable:
        return Score(self.analyzer, self.api)


associations = {
    'score': ScoreClass,
}
