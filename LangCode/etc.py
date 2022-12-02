from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *
from Kiwi.components.kiwiASO import Attr
from Kiwi.components.kiwiScope import ScopeType, CodeScope
import Kiwi.components.kiwiASO as kiwi


class Undefined(Declareable, InitableType):
    attr: Attr
    address: Attr

    def Declare(self, attr: Attr) -> Undefined:
        assert isinstance(attr, Attr)
        self.address = Attr(attr)
        self.attr = Attr(self.api.useLocalPrefix(attr))
        return self

    def InitsType(self, parent: Variable, *args: Abstract):
        self.api.analyzer.scope.write(
            self.address, parent.InitsType(self.attr, self.address, *args))


class Module(CodeScope):
    attr: Attr
    address: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())


class Function(Declareable, CodeScope):
    attr: Attr
    address: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def Declare(self, attr: Attr, body: kiwi.AST):
        assert isinstance(attr, Attr)
        self.address = Attr(attr)
        self.attr = Attr(self.api.useLocalPrefix(attr))

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toString(), self, hideMode=True
        )
        body = self.api.analyzer.visit(body)
        self.api.analyzer.scope.leaveSpace()

        return Construct(
            'Start', self, []
        ), *body, Construct(
            'Finish', self, []
        )

    def Start(self):
        self.api.enterScope(self)

    def Finish(self):
        self.api.leaveScope()


class Namespace(Declareable, ScopeType):
    attr: Attr

    def Declare(self, attr: Attr, private_body: kiwi.AST,
                public_body: kiwi.AST, default_body: kiwi.AST):
        assert isinstance(attr, Attr)
        self.attr = Attr(self.api.useLocalPrefix(attr))

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toString(), self
        )
        default_body = self.api.analyzer.visit(default_body)
        self.api.analyzer.scope.leaveSpace()
        return Construct(
            'Start', self, []
        ), *default_body, Construct(
            'Finish', self, []
        )

    def Start(self):
        self.api.enterScope(self)

    def Finish(self):
        self.api.leaveScope()
