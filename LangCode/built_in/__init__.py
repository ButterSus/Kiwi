from __future__ import annotations

# Default libraries
# -----------------

from typing import Type  # noqa: F401
from functools import reduce  # noqa: F401

# Custom libraries
# ----------------

from LangCode import *
from LangCode.constant import *
from Kiwi.components.kiwiASO import String as TokenString


class Scoreboard(Variable):
    criteria: String

    def InitsType(self, attr: Attr, address: Attr, criteria: String = None) -> Scoreboard:
        # Handle <ADDRESS>
        # ----------------

        assert isinstance(address, Attr)
        self.address = address

        # Handle <NAME>
        # -------------

        assert isinstance(attr, Attr)
        self.attr = attr

        # Handle <CRITERIA>
        # -----------------

        if criteria is None:
            criteria = String(self.api).Formalize(TokenString(..., ..., '"dummy"'))
        assert isinstance(criteria, String)
        self.criteria = criteria

        self.api.system(ScoreboardObjectiveCreate(
            name=self.attr.toString(),
            criteria=self.criteria.value
        ))
        return self


class ScoreboardClass(Class):
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass

    def GetChild(self) -> Scoreboard:
        return Scoreboard(self.api)


class Number(Number):
    def Add(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IAdd(other)
            return temp
        return super().Add(other)

    def Sub(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).ISub(other)
            return temp
        return super().Sub(other)

    def Mul(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IMul(other)
            return temp
        return super().Mul(other)

    def Div(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IDiv(other)
            return temp
        return super().Div(other)

    def Equals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Score):
            return other.Equals(self)
        return super().Equals(other)

    def NotEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Score):
            return other.NotEquals(self)
        return super().NotEquals(other)

    def GreaterThanEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Score):
            return other.LessThanEquals(self)
        return super().GreaterThanEquals(other)

    def LessThanEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Score):
            return other.GreaterThanEquals(self)
        return super().LessThanEquals(other)

    def GreaterThan(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Score):
            return other.LessThan(self)
        return super().GreaterThan(other)

    def LessThan(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Score):
            return other.GreaterThan(self)
        return super().LessThan(other)


class Score(Variable, Assignable,
            SupportAdd, SupportSub, SupportPlus,
            SupportIAdd, SupportISub, SupportMinus,
            SupportEquals, SupportNotEquals, SupportLessThanEquals, SupportLessThan,
            SupportGreaterThanEquals, SupportGreaterThan,
            TransPredicate,
            Printable):
    attr: Attr
    address: Attr
    scoreboard: Scoreboard

    def InitsType(self, attr: Attr, address: Attr = None, scoreboard: Abstract = None) -> Score:
        # Handle <ADDRESS>
        # ----------------

        if address is None:
            address = attr
        assert isinstance(address, Attr)
        self.address = address

        # Handle <ATTR>
        # -------------

        assert isinstance(attr, Attr)
        self.attr = attr

        # Handle <SCOREBOARD>
        # -------------------

        if scoreboard is None:
            scoreboard = self.api.general.scoreboard
        assert isinstance(scoreboard, Scoreboard)
        self.scoreboard = scoreboard

        return self

    # Extendable operators
    # --------------------

    def Assign(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersSet(
                self.attr.toString(), self.scoreboard.attr.toString(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpAss(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Plus(self) -> Optional[Abstract]:
        return self

    def Minus(self) -> Optional[Abstract]:
        self.api.system(ScoreboardPlayersOpIMul(
            self.attr.toString(), self.scoreboard.attr.toString(),
            self._getConstVar(-1).attr.toString(), self._getConstVar(-1).scoreboard.attr.toString()
        ))
        return self

    def Add(self, other: Abstract) -> Score:
        if isinstance(other, Number | Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IAdd(other)
            return temp
        assert False

    def IAdd(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersAdd(
                self.attr.toString(), self.scoreboard.attr.toString(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpIAdd(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Sub(self, other: Abstract) -> Score:
        if isinstance(other, Number | Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).ISub(other)
            return temp
        assert False

    def ISub(self, other: Abstract) -> Score:
        if isinstance(other, Number | Score):
            self.api.system(ScoreboardPlayersRemove(
                self.attr.toString(), self.scoreboard.attr.toString(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpISub(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Mul(self, other: Abstract) -> Score:
        if isinstance(other, Number | Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IMul(other)
            return temp
        assert False

    def IMul(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersOpIMul(
                self.attr.toString(), self.scoreboard.attr.toString(),
                self._getConstVar(other.value).attr.toString(),
                self._getConstVar(other.value).scoreboard.attr.toString()
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpIMul(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Div(self, other: Abstract) -> Score:
        if isinstance(other, Number | Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IDiv(other)
            return temp
        assert False

    def IDiv(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersOpIDiv(
                self.attr.toString(), self.scoreboard.attr.toString(),
                self._getConstVar(other.value).attr.toString(),
                self._getConstVar(other.value).scoreboard.attr.toString()
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpIDiv(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def Mod(self, other: Abstract) -> Score:
        if isinstance(other, Number | Score):
            temp = Score(self.api).InitsType(
                self.api.getTempEx()
            ).Assign(self).IDiv(other)
            return temp
        assert False

    def IMod(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersOpIMod(
                self.attr.toString(), self.scoreboard.attr.toString(),
                self._getConstVar(other.value).attr.toString(),
                self._getConstVar(other.value).scoreboard.attr.toString()
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpIMod(
                self.attr.toString(), self.scoreboard.attr.toString(),
                other.attr.toString(), other.scoreboard.attr.toString()
            ))
            return self
        assert False

    def _getComparePredicate(self, value: NBTLiteral):
        return {
            "condition": "minecraft:value_check",
            "value": {
                "type": "minecraft:score",
                "target": {
                    "type": "minecraft:fixed",
                    "name": convert_var_name(
                        self.attr.toString()
                    )
                },
                "score": convert_var_name(
                    self.scoreboard.attr.toString()
                )
            },
            "range": value
        }

    def Equals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._getComparePredicate(other.value)
        if isinstance(other, Score):
            return self._getComparePredicate({
                "min": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": convert_var_name(
                            other.attr.toString()
                        )
                    },
                    "score": convert_var_name(
                        other.scoreboard.attr.toString()
                    )
                },
                "max": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": convert_var_name(
                            other.attr.toString()
                        )
                    },
                    "score": convert_var_name(
                        other.scoreboard.attr.toString()
                    )
                }
            })
        assert False

    def NotEquals(self, other: Abstract) -> NBTLiteral:
        return {
            "condition": "minecraft:inverted",
            "term": self.Equals(other)
        }

    def GreaterThanEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._getComparePredicate({
                "min": other.value
            })
        if isinstance(other, Score):
            return self._getComparePredicate({
                "min": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": convert_var_name(
                            other.attr.toString()
                        )
                    },
                    "score": convert_var_name(
                        other.scoreboard.attr.toString()
                    )
                }
            })
        assert False

    def LessThanEquals(self, other: Abstract) -> NBTLiteral:
        if isinstance(other, Number):
            return self._getComparePredicate({
                "max": other.value
            })
        if isinstance(other, Score):
            return self._getComparePredicate({
                "max": {
                    "type": "minecraft:score",
                    "target": {
                        "type": "minecraft:fixed",
                        "name": convert_var_name(
                            other.attr.toString()
                        )
                    },
                    "score": convert_var_name(
                        other.scoreboard.attr.toString()
                    )
                }
            })
        assert False

    def GreaterThan(self, other: Abstract) -> NBTLiteral:
        return {
            "condition": "minecraft:inverted",
            "term": self.LessThanEquals(other)
        }

    def LessThan(self, other: Abstract) -> NBTLiteral:
        return {
            "condition": "minecraft:inverted",
            "term": self.GreaterThanEquals(other)
        }

    # Private methods
    # ---------------

    def _getConstVar(self, value: int) -> Score:
        if value in self.api.general.constants.keys():
            return self.api.general.constants[value]
        self.api.globalScope()
        name = self.api.getConstEx(Attr([str(value)]))
        result = Score(self.api).InitsType(
            name, name
        ).Assign(Number(self.api).Formalize(str(value)))
        self.api.general.constants[value] = result
        self.api.localScope()
        return result

    # Another methods
    # ---------------

    def PrintSource(self) -> NBTLiteral:
        return {"score": {
            "name": convert_var_name(self.attr.toString()),
            "objective": convert_var_name(self.scoreboard.attr.toString())
        }}

    def transPredicate(self) -> NBTLiteral:
        return self.NotEquals(Number(self.api).Formalize("0"))


class ScoreClass(Class):
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass

    def GetChild(self) -> Score:
        return Score(self.api)


class Print(Callable):
    def Call(self, *args: Abstract):
        result = list()
        for arg in args:
            assert isinstance(arg, Printable)
            result.append(arg.PrintSource())
        self.api.system(Tellraw(
            '@a',
            reduce(lambda r, v: r + [' ', v], result[1:], result[:1])
        ))


class Sidebar(Callable):
    def Call(self, scoreboard: Scoreboard):
        assert isinstance(scoreboard, Scoreboard)
        self.api.system(ScoreboardObjectiveSetDisplay(
            'sidebar',
            scoreboard.attr.toString(),
        ))


class Remove(Callable):
    def Call(self, variable: Abstract):
        if isinstance(variable, self.api.LangCode):
            self.api.system(ScoreboardPlayersReset(
                variable.attr.toString(),
                variable.scoreboard.attr.toString()
            ))
            return
        if isinstance(variable, Scoreboard):
            self.api.system(ScoreboardObjectiveRemove(
                variable.attr.toString()
            ))
            return
        assert False


def built_annotationsInit(apiObject: Type[API]):
    apiObject.build('builtins', {
        'score': ScoreClass,
        'scoreboard': ScoreboardClass,
        'print': Print,
        'str': StringClass,
        'fstr': FStringClass,
        'sidebar': Sidebar,
        'remove': Remove
    })


def built_codeInit(apiObject: API):
    # General scoreboard
    # ------------------

    apiObject.enterScope(Module(apiObject))
    scoreboard_name = apiObject.useGlobalPrefix(Attr(['globals']), withFuse=True)
    scoreboard = Scoreboard(apiObject).InitsType(
        scoreboard_name, scoreboard_name)
    apiObject.analyzer.scope.write(
        'globals', scoreboard
    )
    apiObject.general.scoreboard = scoreboard
    apiObject.general.constants = dict()


def built_codeFinish(apiObject: API):
    apiObject.leaveScope()
