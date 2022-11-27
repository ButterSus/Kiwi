from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING

# Custom libraries
# ----------------

from LangApi import *
from Kiwi.components.kiwiASO import Attr
from Kiwi.components.kiwiScope import ScopeType
import Kiwi.components.kiwiASO as kiwi


class Undefined(Declareable, InitableType):
    attr: Attr
    address: Attr

    def Declare(self, attr: Attr) -> Undefined:
        assert isinstance(attr, Attr)
        self.address = Attr(attr)
        self.attr = Attr(self.api.analyzer.scope.getAttr() + attr)
        return self

    def InitsType(self, parent: Variable, *args: Abstract):
        self.api.analyzer.scope.write(
            self.address, parent.InitsType(self.attr, self.address, *args))


class Function(ScopeType, Declareable):
    attr: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def Declare(self, name: Attr, body: kiwi.AST):
        assert isinstance(name, Attr)
        self.attr = Attr(self.api.analyzer.scope.getAttr() + name)

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toString(), self, hideMode=True
        )
        body = self.api.analyzer.visit(body)
        self.api.analyzer.scope.leaveSpace()
        return Construct(
            'Start', self, [self.attr]
        ), *body, Construct(
            'Finish', self, []
        )

    def Start(self, attr: Attr):
        self.api.enterScope(attr.toString())
        self.api.enterFunction(attr)

    def Finish(self):
        self.api.closeScope()
        self.api.closeFunction()


class Namespace(Declareable, ScopeType):
    attr: Attr

    def Declare(self, name: Attr, private_body: kiwi.AST,
                public_body: kiwi.AST, default_body: kiwi.AST):
        assert isinstance(name, Attr)
        self.attr = Attr(self.api.analyzer.scope.getAttr() + name)

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toString(), self
        )
        default_body = self.api.analyzer.visit(default_body)
        self.api.analyzer.scope.leaveSpace()
        return Construct(
            'Start', self, [self.attr]
        ), *default_body, Construct(
            'Finish', self, []
        )

    def Start(self, attr: Attr):
        self.api.enterScope(attr.toString())

    def Finish(self):
        self.api.closeScope()
