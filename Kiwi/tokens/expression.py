from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable

# Custom libraries
# ----------------

import LangApi


if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi
    import components.kiwiASO as kiwi


# Initialization of modules
# -------------------------

def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa


# Content of file
# ---------------


class Expression(LangApi.abstract.Formalizable):
    def Formalize(self, value: kiwi.expression) -> LangApi.abstract.Construct:
        return self.analyzer.visit(value)


associations = dict()
