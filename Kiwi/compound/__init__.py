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
import Kiwi.compound.function
import Kiwi.compound.namespace
import Kiwi.compound.ifelse
import Kiwi.compound.whiledo
import Kiwi.compound.forloop


def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    module.init(_compiler, _LangApi, _Kiwi)
    function.init(_compiler, _LangApi, _Kiwi)
    namespace.init(_compiler, _LangApi, _Kiwi)
    ifelse.init(_compiler, _LangApi, _Kiwi)
    whiledo.init(_compiler, _LangApi, _Kiwi)
    forloop.init(_compiler, _LangApi, _Kiwi)


associations = reduce(
    lambda a, b: a | b,
    [
        module.associations,
        function.associations,
        namespace.associations,
        ifelse.associations,
        whiledo.associations,
        forloop.associations,
    ]
)
