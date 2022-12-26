from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable, Dict, Type

# Custom libraries
# ----------------

import LangApi
from LangApi.abstract import Abstract
from components.kiwiScope import Attr


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

    class _IntegerFormat(Kiwi.tokens.number.IntegerFormat):
        def Add(self, other: LangApi.abstract.Abstract) -> LangApi.abstract.Abstract:
            if isinstance(other, Score):
                temp_name = self.api.prefix.SpecTemp()
                temp = Score(self.api).InitsType(
                    temp_name, temp_name
                ).Assign(self).IAdd(other)
                return temp
            return super().Add(other)

        def Sub(self, other: LangApi.abstract.Abstract) -> LangApi.abstract.Abstract:
            if isinstance(other, Score):
                temp_name = self.api.prefix.SpecTemp()
                temp = Score(self.api).InitsType(
                    temp_name, temp_name
                ).Assign(self).ISub(other)
                return temp
            return super().Sub(other)

        def Mul(self, other: LangApi.abstract.Abstract) -> LangApi.abstract.Abstract:
            if isinstance(other, Score):
                temp_name = self.api.prefix.SpecTemp()
                temp = Score(self.api).InitsType(
                    temp_name, temp_name
                ).Assign(self).IMul(other)
                return temp
            return super().Mul(other)

        def Div(self, other: LangApi.abstract.Abstract) -> LangApi.abstract.Abstract:
            if isinstance(other, Score):
                temp_name = self.api.prefix.SpecTemp()
                temp = Score(self.api).InitsType(
                    temp_name, temp_name
                ).Assign(self).IDiv(other)
                return temp
            return super().Div(other)

        def Equals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
            if isinstance(other, Score):
                return other.Equals(self)
            return super().Equals(other)

        def NotEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
            if isinstance(other, Score):
                return other.NotEquals(self)
            return super().NotEquals(other)

        def GreaterThanEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
            if isinstance(other, Score):
                return other.LessThanEquals(self)
            return super().GreaterThanEquals(other)

        def LessThanEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
            if isinstance(other, Score):
                return other.GreaterThanEquals(self)
            return super().LessThanEquals(other)

        def GreaterThan(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
            if isinstance(other, Score):
                return other.LessThan(self)
            return super().GreaterThan(other)

        def LessThan(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
            if isinstance(other, Score):
                return other.GreaterThan(self)
            return super().LessThan(other)

    Kiwi.tokens.number.IntegerFormat = _IntegerFormat


# Content of file
# ---------------


class Score(LangApi.abstract.Variable,
            LangApi.abstract.Assignable,
            LangApi.abstract.SupportArithmetic,
            LangApi.abstract.SupportAugArithmetic,
            LangApi.abstract.SupportComparison,
            LangApi.abstract.TransPredicate,
            LangApi.abstract.Printable):
    # General methods
    # ---------------

    attr: Attr
    address: Attr
    scoreboard: Kiwi.scoreboard.scoreboard.Scoreboard

    def InitsType(self, attr: Attr, address: Attr,
                  scoreboard: Kiwi.scoreboard.scoreboard.Scoreboard = None) -> Score:
        if scoreboard is None:
            scoreboard = Kiwi.scoreboard.scoreboard.Scoreboard.general
        assert isinstance(scoreboard, Kiwi.scoreboard.scoreboard.Scoreboard)
        self.attr = attr
        self.address = address
        self.scoreboard = scoreboard
        return self

    def Assign(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(
                LangApi.bytecode.ScoreboardPlayersSet(
                    self.attr.toString(), self.scoreboard.attr.toString(),
                    str(other.value)
                )
            )
            return self
        if isinstance(other, Score):
            self.api.system(
                LangApi.bytecode.ScoreboardPlayersOpAss(
                    self.attr.toString(), self.scoreboard.attr.toString(),
                    other.attr.toString(), other.scoreboard.attr.toString()
                )
            )
            return self
        assert False

    # Math methods
    # ------------

    _constants: Dict[int, Score] = dict()

    def getConst(self, value: int) -> Score:
        if value in self._constants.keys():
            return self._constants[value]
        self.api.enableGlobal()
        const_name = self.api.prefix.SpecConst(value)
        result = Score(self.api).InitsType(
            const_name, const_name
        ).Assign(
            Kiwi.tokens.number.IntegerFormat(self.api).Formalize(value)
        )
        self.api.disableGlobal()
        self._constants[value] = result
        return result

    def Plus(self) -> Score:
        return self

    def Minus(self) -> Score:
        self.api.system(LangApi.bytecode.ScoreboardPlayersOpIMul(
            self.attr.toString(), self.scoreboard.attr.toString(),
            self.getConst(-1).attr.toString(), self.getConst(-1).scoreboard.attr.toString()
        ))
        return self

    def Add(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat | Score):
            temp_name = self.api.prefix.SpecTemp()
            temp = Score(self.api).InitsType(
                temp_name, temp_name
            ).Assign(self).IAdd(other)
            return temp
        assert False

    def IAdd(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(LangApi.bytecode.ScoreboardPlayersAdd(
                self.attr.toString(), self.scoreboard.attr.toString(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIAdd(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Sub(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat | Score):
            temp_name = self.api.prefix.SpecTemp()
            temp = Score(self.api).InitsType(
                temp_name, temp_name
            ).Assign(self).ISub(other)
            return temp
        assert False

    def ISub(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(LangApi.bytecode.ScoreboardPlayersRemove(
                self.attr.toString(), self.scoreboard.attr.toString(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpISub(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Mul(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat | Score):
            temp_name = self.api.prefix.SpecTemp()
            temp = Score(self.api).InitsType(
                temp_name, temp_name
            ).Assign(self).IMul(other)
            return temp
        assert False

    def IMul(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIMul(
                self.attr.toString(), self.scoreboard.attr.toString(),
                self.getConst(other.value).attr.toString(),
                self.getConst(other.value).scoreboard.attr.toString()
            ))
            return self
        if isinstance(other, Score):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIMul(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Div(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat | Score):
            temp_name = self.api.prefix.SpecTemp()
            temp = Score(self.api).InitsType(
                temp_name, temp_name
            ).Assign(self).IDiv(other)
            return temp
        assert False

    def IDiv(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIDiv(
                self.attr.toString(), self.scoreboard.attr.toString(),
                self.getConst(other.value).attr.toString(),
                self.getConst(other.value).scoreboard.attr.toString()
            ))
            return self
        if isinstance(other, Score):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIDiv(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Mod(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat | Score):
            temp_name = self.api.prefix.SpecTemp()
            temp = Score(self.api).InitsType(
                temp_name, temp_name
            ).Assign(self).IDiv(other)
            return temp
        assert False

    def IMod(self, other: LangApi.abstract.Abstract) -> Score:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIMod(
                self.attr.toString(), self.scoreboard.attr.toString(),
                self.getConst(other.value).attr.toString(),
                self.getConst(other.value).scoreboard.attr.toString()
            ))
            return self
        if isinstance(other, Score):
            self.api.system(LangApi.bytecode.ScoreboardPlayersOpIMod(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    # Comparison methods
    # ------------------

    def _getComparePredicate(self, value: LangApi.bytecode.NBTLiteral):
        return {
            "condition": "minecraft:value_check",
            "value": {
                "type": "minecraft:score",
                "target": {
                    "type": "minecraft:fixed",
                    "name": self.api.prefix.useConverter(
                        self.attr.toString()
                    )
                },
                "score": self.api.prefix.useConverter(
                    self.scoreboard.attr.toString()
                )
            },
            "range": value
        }

    def Equals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            return self._getComparePredicate(other.value)
        if isinstance(other, Score):
            return self._getComparePredicate({
                "min": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": self.api.prefix.useConverter(
                            other.attr.toString()
                        )
                    },
                    "score": self.api.prefix.useConverter(
                        other.scoreboard.attr.toString()
                    )
                },
                "max": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": self.api.prefix.useConverter(
                            other.attr.toString()
                        )
                    },
                    "score": self.api.prefix.useConverter(
                        other.scoreboard.attr.toString()
                    )
                }
            })
        assert False

    def NotEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        return {
            "condition": "minecraft:inverted",
            "term": self.Equals(other)
        }

    def GreaterThanEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            return self._getComparePredicate({
                "min": other.value
            })
        if isinstance(other, Score):
            return self._getComparePredicate({
                "min": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": self.api.prefix.useConverter(
                            other.attr.toString()
                        )
                    },
                    "score": self.api.prefix.useConverter(
                        other.scoreboard.attr.toString()
                    )
                }
            })
        assert False

    def LessThanEquals(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        if isinstance(other, Kiwi.tokens.number.IntegerFormat):
            return self._getComparePredicate({
                "max": other.value
            })
        if isinstance(other, Score):
            return self._getComparePredicate({
                "max": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": self.api.prefix.useConverter(
                            other.attr.toString()
                        )
                    },
                    "score": self.api.prefix.useConverter(
                        other.scoreboard.attr.toString()
                    )
                }
            })
        assert False

    def GreaterThan(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        return {
            "condition": "minecraft:inverted",
            "term": self.LessThanEquals(other)
        }

    def LessThan(self, other: LangApi.abstract.Abstract) -> LangApi.bytecode.NBTLiteral:
        return {
            "condition": "minecraft:inverted",
            "term": self.GreaterThanEquals(other)
        }

    # Another methods
    # ---------------

    def transPredicate(self) -> LangApi.bytecode.NBTLiteral:
        return self.NotEquals(Kiwi.tokens.number.IntegerFormat(self.api).Formalize(0))

    def PrintSource(self) -> LangApi.bytecode.NBTLiteral:
        return {
            "score": {
                "name": self.api.prefix.useConverter(self.attr.toString()),
                "objective": self.api.prefix.useConverter(self.scoreboard.attr.toString())
            }
        }


class ScoreClass(LangApi.abstract.Class):
    def Call(self, *args: LangApi.abstract.Abstract):
        pass

    def GetChild(self) -> Type[Score]:
        return Score


associations = {
    'score': ScoreClass,
}
