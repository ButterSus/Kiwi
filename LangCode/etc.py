from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *
from Kiwi.components.kiwiASO import Attr
from Kiwi.components.kiwiScope import CodeScope, NoCodeScope
import Kiwi.components.kiwiASO as kiwi


class Undefined(Formalizable, InitableType):
    attr: Attr
    address: Attr

    def Formalize(self, attr: Attr) -> Undefined:
        assert isinstance(attr, Attr)
        self.address = attr
        self.attr = self.api.useLocalPrefix(attr)
        return self

    def InitsType(self, parent: Variable, *args: Abstract):
        self.api.analyzer.scope.write(
            self.address, parent.InitsType(self.attr, self.address, *args))


class Module(CodeScope, Abstract):
    attr: Attr
    address: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict(), name=self.api.config['entry_file'])


class Function(CodeScope, Formalizable, Callable):
    attr: Attr
    address: Attr
    params: List[Abstract]
    returns: Abstract

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def Formalize(self, attr: Attr, body: kiwi.AST, params: List[kiwi.Parameter], returns: kiwi.ReturnParameter):
        assert isinstance(attr, Attr)
        self.address = attr
        self.attr = self.api.useLocalPrefix(attr)

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toName(), self, hideMode=True
        )
        self.api.enterScope(self)
        params = self.api.analyzer.visit(params)
        returns = self.api.analyzer.visit(returns)
        body = self.api.analyzer.visit(body)
        self.api.leaveScope()
        self.api.analyzer.scope.leaveSpace()

        return Construct(
            'Reference',
            self,
            [body, params, returns],
            raw_args=True
        )

    def Reference(self, body: Construct, params: Any, returns: Any):
        self.api.enterScope(self)
        self.params = self.api.visit(params)
        self.returns = self.api.visit(returns)
        self.api.visit(body)
        self.api.leaveScope()
        return self

    def Call(self, *args: Abstract):
        for param, arg in zip(self.params, args):
            self.api.visit(
                Construct(
                    'Assign',
                    param,
                    [arg]
                ))
        self.api.system(FunctionDirectCall(
            self.api.useDirPrefix(self.attr).toString()
        ))
        return self.returns

    def Return(self, value: Abstract):
        self.api.visit(
            Construct(
                'Assign',
                self.returns,
                [value]
            )
        )


class Namespace(NoCodeScope, Formalizable):
    attr: Attr
    address: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def Formalize(self, attr: Attr, blocks: List[kiwi.PrivateBlock | kiwi.PublicBlock | kiwi.DefaultBlock]):
        assert isinstance(attr, Attr)
        self.address = attr
        self.attr = self.api.useLocalPrefix(attr)

        result = list()

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toName(), self
        )
        self.api.enterScope(self)
        for block in blocks:
            if isinstance(block, kiwi.PrivateBlock):
                self.private_mode = True
            elif isinstance(block, kiwi.PublicBlock):
                self.private_mode = False
            else:
                self.private_mode = self.api.config['default_scope'] == 'public'
            result.append(self.api.analyzer.visit(block))
        self.api.leaveScope()
        self.api.analyzer.scope.leaveSpace()

        return Construct(
            'Reference',
            self,
            [*result],
            raw_args=True
        )

    def Reference(self, *blocks: kiwi.PrivateBlock | kiwi.PublicBlock | kiwi.DefaultBlock):
        self.api.enterScope(self)
        for block in blocks:
            self.api.visit(block.body)
        self.api.leaveScope()
        return self
