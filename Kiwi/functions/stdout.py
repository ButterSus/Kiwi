from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable
from functools import reduce

# Custom libraries
# ----------------

import LangApi


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


class Print(LangApi.abstract.Callable):
    def Call(self, *args: LangApi.abstract.Abstract):
        result = list()
        for arg in args:
            assert isinstance(arg, LangApi.abstract.Printable)
            result.append(arg.PrintSource())
        self.api.system(LangApi.bytecode.Tellraw(
            '@a',
            reduce(lambda r, v: r + [' ', v], result[1:], result[:1])
        ))


associations = {
    'print': Print
}
