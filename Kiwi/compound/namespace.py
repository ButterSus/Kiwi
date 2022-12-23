from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, List, Callable

# Custom libraries
# ----------------

import LangApi
from components.kiwiScope import Attr
import components.kiwiASO as kiwi


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


class Namespace(LangApi.abstract.Block):
    attr: Attr

    def _getHideMode(self):
        return self.api.configGeneral['default_scope'] == 'private'

    def Formalize(self, attr: Attr, blocks: List[kiwi.AnyBlock]):
        self.analyzer.scope.write(
            attr, self
        )
        self.attr = attr

        result = list()
        self.name = attr.toName()
        self.api.enterCodeScope(self)
        for block in blocks:
            match type(block):
                case kiwi.PrivateBlock:
                    self.analyzer.scope.useCustomSpace(self, hideMode=True)
                case kiwi.DefaultBlock:
                    self.analyzer.scope.useCustomSpace(self, hideMode=self._getHideMode())
                case kiwi.PublicBlock:
                    self.analyzer.scope.useCustomSpace(self)
            result.extend(self.analyzer.visit(block.body))
            self.analyzer.scope.leaveSpace()
        self.api.leaveScope()
        return LangApi.api.Construct(
            LangApi.api.ConstructMethod.Reference,
            self,
            [result],
            raw_args=True
        )

    def Reference(self, body: List[LangApi.api.Construct]):
        self.api.system(LangApi.bytecode.FunctionDirectCall(
            self.api.prefix.SpecFileProject(
                Attr([self.api.prefix.FileNamespace(self.name)])
            ).toString()
        ))
        self.api.enterCodeScope(self)
        self.api.visit(body)
        self.api.leaveScope()

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'main':
                return [
                    *self.constructor.attributes.functions,
                    f'{self.api.prefix.FileNamespace(self.name)}.mcfunction'
                ]


associations = dict()
