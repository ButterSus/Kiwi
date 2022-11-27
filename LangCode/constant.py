from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *


class Number(Formalizable, SupportAdd, SupportSub,
             SupportMul, SupportDiv, SupportMod):
    value: int

    def Formalize(self, token: str) -> Number:
        self.value = int(token)
        return self

    def Add(self, other: Number) -> Number:
        self.value += other.value
        return self

    def Sub(self, other: Number) -> Number:
        self.value -= other.value
        return self

    def Mul(self, other: Number) -> Number:
        self.value *= other.value
        return self

    def Div(self, other: Number) -> Number:
        self.value //= other.value
        return self

    def Mod(self, other: Number) -> Number:
        self.value %= other.value
        return self


class String(Formalizable, SupportAdd,
             SupportSub, SupportMul):
    value: str

    def Formalize(self, token: str) -> String:
        self.value = str(token)[1:-1]
        return self

    def Add(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, String):
            self.value += other.value
            return self
        assert False

    def Sub(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, String):
            self.value -= other.value
            return self
        assert False

    def Mul(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, String):
            self.value *= other.value
            return self
        assert False
