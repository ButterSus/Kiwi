from __future__ import annotations

# Default libraries
# -----------------

from string import Formatter

# Custom libraries
# ----------------

from Kiwi.components.kiwiASO import String as TokenString
from LangApi import *


class AbsoluteNone(Formalizable):
    def Formalize(self) -> Optional[Abstract]:
        return self


class Number(Formalizable, SupportAdd, SupportSub, SupportPlus,
             SupportMul, SupportDiv, SupportMod, SupportMinus,
             SupportEquals, SupportNotEquals, SupportLessThan, SupportGreaterThan,
             SupportLessThanEquals, SupportGreaterThanEquals,
             TransPredicate,
             Printable):
    value: int

    def Plus(self) -> Optional[Abstract]:
        return self

    def Minus(self) -> Optional[Abstract]:
        self.value = -self.value
        return self

    def Formalize(self, token: str) -> Number:
        self.value = int(token)
        return self

    def Add(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value += other.value
            return self
        assert False

    def Sub(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value -= other.value
            return self
        assert False

    def Mul(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value *= other.value
            return self
        assert False

    def Div(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value /= other.value
            return self
        assert False

    def Mod(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value %= other.value
            return self
        if isinstance(other, ...):
            ...
        assert False

    def _boolToPredicate(self, value: bool) -> NBTLiteral:
        if value:
            return const_predicate_true
        return const_predicate_false

    def Equals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._boolToPredicate(
                self.value == other.value
            )
        assert False

    def NotEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._boolToPredicate(
                self.value != other.value
            )
        assert False

    def LessThanEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._boolToPredicate(
                self.value <= other.value
            )
        assert False

    def GreaterThanEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._boolToPredicate(
                self.value >= other.value
            )
        assert False

    def LessThan(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._boolToPredicate(
                self.value < other.value
            )
        assert False

    def GreaterThan(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._boolToPredicate(
                self.value > other.value
            )
        assert False

    def PrintSource(self) -> NBTLiteral:
        return {
            "text": str(int(self.value))
        }

    def transPredicate(self) -> NBTLiteral:
        return self.NotEquals(Number(self.api).Formalize("0"))


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
            value = String(self.api).Formalize(TokenString(..., ..., ""), noHandle=True)
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
                TokenString(..., ..., self.value), noHandle=True
            )
            temp.Add(other)
            return temp
        assert False

    def Mul(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Number):
            self.value *= other.value
            return self
        assert False

    def PrintSource(self) -> NBTLiteral:
        return {
            "text": self.value
        }


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
            value = FString(self.api).Formalize(TokenString(..., ..., ""), noHandle=True)
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

    def PrintSource(self) -> List[NBTLiteral]:
        information = self._formatter.parse(self.value)
        result = list()
        for string, expression, _, _ in information:
            if string is not None:
                result.append(String(self.api).Formalize(
                    TokenString(..., ..., string), noHandle=True
                ))
            if expression is not None:
                result.append(self.api.eval(expression))
        return list(map(lambda x: x.PrintSource(), result))


class FStringClass(Class):
    def GetChild(self) -> Abstract:
        return FString(self.api)

    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass
