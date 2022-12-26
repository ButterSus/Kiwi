"""
This package contains all built-in constant
tokens
"""

from __future__ import annotations

# Default libraries
# -----------------

from functools import reduce
from typing import Any

# Custom libraries
# ----------------

import Kiwi.tokens.number
import Kiwi.tokens.string
import Kiwi.tokens.expression
import Kiwi.tokens.undefined
import Kiwi.tokens.boolean
import Kiwi.tokens.range


def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    number.init(_compiler, _LangApi, _Kiwi)
    string.init(_compiler, _LangApi, _Kiwi)
    expression.init(_compiler, _LangApi, _Kiwi)
    undefined.init(_compiler, _LangApi, _Kiwi)
    boolean.init(_compiler, _LangApi, _Kiwi)
    range.init(_compiler, _LangApi, _Kiwi)


associations = reduce(
    lambda a, b: a | b,
    [
        number.associations,
        string.associations,
        expression.associations,
        undefined.associations,
        boolean.associations,
        range.associations,
    ]
)
