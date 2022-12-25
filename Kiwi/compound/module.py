from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, List, Callable

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


class Module(LangApi.abstract.Block):
    def Formalize(self, body: List[Any]):
        self.api.enterCodeScope(self)
        result = self.analyzer.visit(body)
        self.api.leaveScope()
        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [result],
            raw_args=True
        )

    def Reference(self, body: List[LangApi.abstract.Construct]):
        self.api.enterCodeScope(self)
        self.api.visit(body)
        self.api.leaveScope()

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'main':
                return [
                    *self.constructor.attributes.functions,
                    '--main--.mcfunction'
                ]
        assert False


associations = dict()
