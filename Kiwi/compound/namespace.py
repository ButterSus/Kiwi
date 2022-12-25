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
    namespace_attr: Attr

    def _getHideMode(self):
        return self.api.configGeneral['default_scope'] == 'private'

    def Formalize(self, attr: Attr, blocks: List[kiwi.AnyBlock]):
        self.analyzer.scope.write(
            attr, self
        )
        self.attr = attr
        self.name = attr.toName()
        self.namespace_attr = self.api.prefix.FileNamespace(self.name)

        result = list()
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
        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [result],
            raw_args=True
        )

    def Reference(self, body: List[LangApi.abstract.Construct]):
        self.api.system(LangApi.bytecode.FunctionDirectCall(
            self.api.prefix.FileAttrToDirectory(
                self.api.prefix.FileNamespace(self.name)
            )
        ))  # TODO: SCOPE HANDLING
        self.api.enterCodeScope(self)
        self.analyzer.scope.useCustomSpace(self)
        self.api.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScope()

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'main':
                return [
                    *self.constructor.attributes.functions,
                    *self.namespace_attr[:-1],
                    f'{self.namespace_attr.toName()}.mcfunction'
                ]
        assert False


associations = dict()
