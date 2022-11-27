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


class Undefined(Declareable, ChangeableType):
    attr: Attr

    def Declare(self, name: Attr) -> Undefined:
        assert isinstance(name, Attr)
        self.attr = Attr(self.api.analyzer.scope.getAttr() + name)
        return self

    def ChangeType(self, parent: Variable, *args: Abstract):
        self.api.analyzer.scope.write(
            self.attr, parent.ChangeType(self.attr, *args))


class Function(Declareable, ScopeType):
    attr: Attr

    def Declare(self, name: Attr, body: kiwi.AST):
        assert isinstance(name, Attr)
        self.attr = Attr(self.api.analyzer.scope.getAttr() + name)

        self.api.enterFunction(self.attr.toString())
        self.api.analyzer.scope.useCustomSpace(
            self.attr.toString(), self, hideMode=True
        )
        body = self.api.analyzer.visit(body)
        self.api.analyzer.scope.leaveSpace()
        return *body, Construct(
            'Finish',
            self,
            []
        )

    def Finish(self):
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
        return tuple(default_body)
