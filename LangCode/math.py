from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *


class Expression(Abstract):
    def Annotation(self, value: Construct, *_) -> list | Construct:
        return self.api.visit(value)
