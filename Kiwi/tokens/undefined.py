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


class Undefined(LangApi.abstract.Formalizable):
    attr: Attr
    address: Attr

    def Formalize(self, attr: Attr) -> Undefined:
        assert isinstance(attr, Attr)
        self.address = attr
        self.attr = self.api.prefix.ModLocal(attr)
        return self

    def Annotation(self, parent: LangApi.abstract.Variable, *args: LangApi.abstract.Abstract):
        result = parent.InitsType(self.attr, self.address, *args)
        self.analyzer.scope.write(self.address, result)
        return result

    def AnnAssign(self, parent: LangApi.abstract.Const, value: LangApi.abstract.Abstract):
        result = parent.InitsTypeAssign(self.attr, self.address, value)
        self.analyzer.scope.write(self.address, result)
        return result


associations = dict()
