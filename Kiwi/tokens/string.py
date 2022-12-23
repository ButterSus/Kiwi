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


class StringFormat(LangApi.abstract.Format,
                   LangApi.abstract.SupportAdd,
                   LangApi.abstract.SupportMul,
                   LangApi.abstract.Printable):
    value: str

    def Formalize(self, token: str) -> StringFormat:
        self.value = token
        return self

    def Add(self, other: StringFormat) -> StringFormat:
        assert isinstance(other, StringFormat)
        self.value += other.value
        return self

    def Mul(self, other: Kiwi.tokens.number.IntegerFormat) -> StringFormat:
        assert isinstance(other, Kiwi.tokens.number.IntegerFormat)
        self.value *= other.value
        return self

    def PrintSource(self) -> LangApi.bytecode.NBTLiteral:
        return {
            "text": self.value
        }


associations = dict()
