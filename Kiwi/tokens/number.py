from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable

# Custom libraries
# ----------------

import LangApi


if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi


# Initialization of modules
# -------------------------

def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa


# Content of file
# ---------------


class IntegerFormat(LangApi.abstract.Format,
                    LangApi.abstract.SupportArithmetic,
                    LangApi.abstract.SupportComparison,
                    LangApi.abstract.TransPredicate,
                    LangApi.abstract.Printable):
    # General methods
    # ---------------

    value: int

    def Formalize(self, token: str | int):
        self.value = int(token)
        return self

    # Math methods
    # ------------

    def Plus(self):
        return self

    def Minus(self):
        self.value = -self.value
        return self

    def Add(self, other: LangApi.abstract.Abstract):
        if isinstance(other, IntegerFormat):
            self.value += other.value
            return self
        assert False

    def Sub(self, other: LangApi.abstract.Abstract):
        if isinstance(other, IntegerFormat):
            self.value -= other.value
            return self
        assert False

    def Mul(self, other: LangApi.abstract.Abstract):
        if isinstance(other, IntegerFormat):
            self.value *= other.value
            return self
        assert False

    def Div(self, other: LangApi.abstract.Abstract):
        if isinstance(other, IntegerFormat):
            self.value /= other.value
            return self
        assert False

    def Mod(self, other: LangApi.abstract.Abstract):
        if isinstance(other, IntegerFormat):
            self.value %= other.value
            return self
        assert False

    # Comparison methods
    # ------------------

    @staticmethod
    def _boolToPredicate(value: bool) -> LangApi.bytecode.NBTLiteral:
        if value:
            return LangApi.bytecode.const_predicate_true
        return LangApi.bytecode.const_predicate_false

    def Equals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, IntegerFormat):
            return self._boolToPredicate(
                self.value == other.value
            )
        assert False

    def NotEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, IntegerFormat):
            return self._boolToPredicate(
                self.value != other.value
            )
        assert False

    def LessThanEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, IntegerFormat):
            return self._boolToPredicate(
                self.value <= other.value
            )
        assert False

    def GreaterThanEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, IntegerFormat):
            return self._boolToPredicate(
                self.value >= other.value
            )
        assert False

    def LessThan(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, IntegerFormat):
            return self._boolToPredicate(
                self.value < other.value
            )
        assert False

    def GreaterThan(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, IntegerFormat):
            return self._boolToPredicate(
                self.value > other.value
            )
        assert False

    # Another methods
    # ---------------

    def PrintSource(self) -> LangApi.bytecode.NBTLiteral:
        return {
            "text": str(self.value)
        }

    def transPredicate(self) -> LangApi.bytecode.NBTLiteral:
        return self.NotEquals(IntegerFormat(self.api).Formalize(0))



associations = dict()
