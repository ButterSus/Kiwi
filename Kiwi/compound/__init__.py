"""
This package contains all built-in grammar
compound statements
"""

from __future__ import annotations

# Default libraries
# -----------------

from functools import reduce
from typing import Any

# Custom libraries
# ----------------

import Kiwi.compound.module


def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    module.init(_compiler, _LangApi, _Kiwi)


associations = reduce(
    lambda a, b: a | b,
    [
        module.associations,
    ]
)
