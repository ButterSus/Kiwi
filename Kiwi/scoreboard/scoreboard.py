from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable

# Custom libraries
# ----------------

import LangApi
import components.kiwiASO as kiwi
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


default_criteria = 'dummy'


# Content of file
# ---------------


class Scoreboard(LangApi.abstract.Variable):
    isNative = True
    """
    Specifies for analyzer not to handle AST parameters in annotation.
    """

    criteria: str
    """
    Criteria from minecraft scoreboards.
    """

    _general: Scoreboard = None
    @classmethod
    @property
    def general(cls) -> Scoreboard:  # noqa
        api = LangApi.api.API.general
        if cls._general is None:
            cls._general = Scoreboard(api).InitsType(api.prefix.default_scoreboard,
                                                                   api.prefix.default_scoreboard)
        return cls._general

    def InitsType(self, attr: Attr, address: Attr,
                  criteria: kiwi.AST | str = default_criteria) -> Scoreboard:
        if isinstance(criteria, kiwi.AST):
            criteria = self.analyzer.native(criteria)
        assert isinstance(criteria, str)

        self.attr = self.api.prefix.SpecStatic(attr)
        self.address = address
        self.criteria = criteria
        self.api.system(
            LangApi.bytecode.ScoreboardObjectiveCreate(
                name=self.attr.toString(),
                criteria=self.criteria
            )
        )
        return self


class ScoreboardClass(LangApi.abstract.Class):
    def Call(self, *args: LangApi.abstract.Abstract):
        pass

    def GetChild(self):
        return Scoreboard(self.api)


associations = {
    'scoreboard': ScoreboardClass
}
