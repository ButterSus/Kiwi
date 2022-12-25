from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, List, Callable, Type

# Custom libraries
# ----------------

import LangApi
import components.kiwiASO as kiwi
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


class Function(LangApi.abstract.Block,
               LangApi.abstract.Returnable,
               LangApi.abstract.Callable):
    attr: Attr
    file_attr: Attr
    params: List[LangApi.abstract.Assignable]
    returns: LangApi.abstract.Assignable | LangApi.abstract.Abstract

    def Formalize(self, attr: Attr,
                  body: List[kiwi.statement],
                  params: List[kiwi.Parameter],
                  returns: kiwi.ReturnParameter):
        self.analyzer.scope.write(
            attr, self
        )
        self.attr = attr
        self.name = attr.toName()
        self.file_attr = self.api.prefix.FileFunction(self.name)

        self.api.enterCodeScope(self)
        self.analyzer.scope.useCustomSpace(
            self, hideMode=True
        )
        self.params = self.analyzer.visit(params)
        if isinstance(returns, kiwi.ReturnParameter):
            return_parent: Type[LangApi.abstract.Variable] = self.analyzer.visit(returns)
            if return_parent.isNative:
                args = returns.args
            else:
                args = self.analyzer.visit(returns.args)
            return_attr = self.api.prefix.VarReturn()
            self.returns = return_parent(self.api).InitsType(
                return_attr, return_attr, *args
            )
        if isinstance(returns, kiwi.ReturnRefParameter):
            self.returns = self.analyzer.visit(returns)
        body = self.analyzer.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScope()

        return LangApi.api.Construct(
            LangApi.api.ConstructMethod.Reference,
            self,
            [body],
            raw_args=True
        )

    def Reference(self, body: List[LangApi.api.Construct]):
        self.api.enterCodeScope(self)
        self.analyzer.scope.useCustomSpace(self, hideMode=True)
        self.api.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScope()

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'main':
                return [
                    *self.constructor.attributes.functions,
                    *self.file_attr[:-1],
                    f'{self.file_attr.toName()}.mcfunction'
                ]
        assert False

    def Return(self, value: LangApi.abstract.Abstract):
        self.returns.Assign(value)

    def Call(self, *args: LangApi.abstract.Abstract) -> LangApi.abstract.Abstract:
        assert len(args) == len(self.params)
        for param, arg in zip(self.params, args):
            param.Assign(arg)
        self.api.system(
            LangApi.bytecode.FunctionDirectCall(
                self.api.prefix.FileAttrToDirectory(
                    self.api.prefix.FileFunction(self.name)
                )
            )
        )
        try:
            return self.returns
        except AttributeError:
            return ...  # TODO: NONE SYSTEM


associations = dict()
