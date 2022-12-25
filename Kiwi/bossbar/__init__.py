"""
This package contains all scoreboard objects
"""

from __future__ import annotations

# Default libraries
# -----------------

from functools import reduce
from typing import Any

# Custom libraries
# ----------------

import Kiwi.bossbar.bossbar



def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    bossbar.init(_compiler, _LangApi, _Kiwi)



associations = reduce(
    lambda a, b: a | b,
    [
        bossbar.associations,

    ]
)
