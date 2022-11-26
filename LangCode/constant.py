from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *


class Number(Constant, SupportArithmetic):
    value: int

    def Annotation(self, token: str, *args: Argument) -> Number:
        self.value = int(token)
        return self

    def Add(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, Number):
            self.value += other.value
            return self
        assert False

    def Sub(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, Number):
            self.value -= other.value
            return self
        assert False

    def Mul(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, Number):
            self.value *= other.value
            return self
        assert False

    def Div(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, Number):
            self.value /= other.value
            return self
        assert False

    def Mod(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, Number):
            self.value %= other.value
            return self
        assert False


class String(Constant, SupportArithmetic):
    value: str

    def Annotation(self, token: str, *args: Argument) -> String:
        self.value = str(token)
        return self

    def Add(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, String):
            self.value += other.value
            return self
        assert False

    def Sub(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, String):
            self.value -= other.value
            return self
        assert False

    def Mul(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, String):
            self.value *= other.value
            return self
        assert False

    def Div(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, String):
            self.value /= other.value
            return self
        assert False

    def Mod(self, other: Argument) -> Optional[Argument]:
        if isinstance(other, String):
            self.value %= other.value
            return self
        assert False



