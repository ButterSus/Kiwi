"""
Kiwi package
v 0.0.5

It's used to collect all Kiwi back-end into one structured package
"""

from __future__ import annotations

# Default libraries
# -----------------

from functools import reduce
from typing import Any

# Custom libraries
# ----------------

import Kiwi.tokens
import Kiwi.compound
import Kiwi.functions
import Kiwi.scoreboard
import Kiwi.bossbar


def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    tokens.init(_compiler, _LangApi, _Kiwi)
    compound.init(_compiler, _LangApi, _Kiwi)
    functions.init(_compiler, _LangApi, _Kiwi)
    scoreboard.init(_compiler, _LangApi, _Kiwi)
    bossbar.init(_compiler, _LangApi, _Kiwi)


associations = reduce(
    lambda a, b: a | b,
    [
        tokens.associations,
        compound.associations,
        functions.associations,
        scoreboard.associations,
        bossbar.associations,
    ]
)
