from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *


class Expression(Formalizable):
    def Formalize(self, value: Construct) -> Abstract:
        return self.api.visit(value)
