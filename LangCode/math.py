from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *


class Expression(Formalizable):
    def Formalize(self, value: Construct = None) -> Optional[Abstract]:
        if value is None:
            return
        result = self.api.visit(value)
        self.api.resetExpression()
        return result


class NotFullExpression(Formalizable):
    def Formalize(self, value: Construct = None) -> Optional[Abstract]:
        if value is None:
            return
        result = self.api.visit(value)
        return result
