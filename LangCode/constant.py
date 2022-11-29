from __future__ import annotations

# Default libraries
# -----------------

from string import Formatter

# Custom libraries
# ----------------

from Kiwi.components.kiwiASO import String as TokenString
from LangApi import *


class Number(Formalizable, SupportAdd, SupportSub,
             SupportMul, SupportDiv, SupportMod,
             Printable):
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

    def PrintSource(self) -> str:
        return f'{{"text":"{self.value}"}}'


class String(Formalizable, Printable,
             SupportAdd, SupportMul,
             Variable):
    value: str

    def InitsType(self, attr: Attr, address: Attr, value: String = None) -> Optional[Abstract]:
        # Handle <ADDRESS>
        # ----------------

        assert isinstance(address, Attr)
        self.address = address

        # Handle <NAME>
        # -------------

        assert isinstance(attr, Attr)
        self.attr = attr

        # Handle <VALUE>
        # --------------

        if value is None:
            value = String(self.api).Formalize(TokenString(""), noHandle=True)
        assert isinstance(value, String)
        self.value = value.value

        return self

    def Formalize(self, token: TokenString, noHandle=False) -> String:
        if noHandle:
            self.value = token.value
            return self
        self.value = token.getString()
        return self

    def Add(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, String):
            temp = FString(self.api).Formalize(
                TokenString(self.value), noHandle=True
            )
            temp.Add(other)
            return temp
        assert False

    def Mul(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value *= other.value
            return self
        assert False

    def PrintSource(self) -> str:
        return f'{{"text":"{self.value}"}}'


class StringClass(Class):
    def GetChild(self) -> Abstract:
        return String(self.api)

    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass


class FString(String):
    _formatter = Formatter()

    def InitsType(self, attr: Attr, address: Attr, value: FString = None) -> Optional[Abstract]:
        # Handle <ADDRESS>
        # ----------------

        assert isinstance(address, Attr)
        self.address = address

        # Handle <NAME>
        # -------------

        assert isinstance(attr, Attr)
        self.attr = attr

        # Handle <VALUE>
        # --------------

        if value is None:
            value = FString(self.api).Formalize(TokenString(""), noHandle=True)
        if isinstance(value, String):
            value.__class__ = FString
        assert isinstance(value, FString)
        self.value = value.value

        return self

    def Add(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, String):
            self.value += other.value
            return self
        assert False

    def Mul(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value *= other.value
            return self
        assert False

    def PrintSource(self) -> str:
        information = self._formatter.parse(self.value)
        result = list()
        for string, expression, _, _ in information:
            if string is not None:
                result.append(String(self.api).Formalize(
                    TokenString(string), noHandle=True
                ))
            if expression is not None:
                result.append(self.api.eval(expression))
        return ','.join(map(lambda x: x.PrintSource(), result))


class FStringClass(Class):
    def GetChild(self) -> Abstract:
        return FString(self.api)

    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass
