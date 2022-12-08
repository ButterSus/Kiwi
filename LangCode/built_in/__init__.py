from __future__ import annotations

# Default libraries
# -----------------

from typing import Type

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
            name=self.attr.toName(),
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
                self.api.getTemp()
            ).Assign(other).IAdd(self)
            return temp
        return super().Add(other)

    def Sub(self, other: Abstract) -> Optional[Abstract]:
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTemp()
            ).Assign(other).ISub(self)
            return temp
        return super().Add(other)


class Score(Variable, Assignable,
            SupportAdd, SupportSub,
            SupportIAdd, SupportISub,
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
                self.attr.toName(), self.scoreboard.attr.toName(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpEq(
                self.attr.toName(), self.scoreboard.attr.toName(),
                other.attr.toName(), other.scoreboard.attr.toName()
            ))
            return self
        assert False

    def Add(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            temp = Score(self.api).InitsType(
                self.api.getTemp()
            ).Assign(self).IAdd(other)
            return temp
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTemp()
            ).Assign(self).IAdd(other)
            return temp
        assert False

    def IAdd(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersAdd(
                self.attr.toName(), self.scoreboard.attr.toName(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpIAdd(
                self.attr.toName(), self.scoreboard.attr.toName(),
                other.attr.toName(), other.scoreboard.attr.toName()
            ))
            return self
        assert False

    def Sub(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            temp = Score(self.api).InitsType(
                self.api.getTemp()
            ).Assign(self).ISub(other)
            return temp
        if isinstance(other, Score):
            temp = Score(self.api).InitsType(
                self.api.getTemp()
            ).Assign(self).ISub(other)
            return temp
        assert False

    def ISub(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(ScoreboardPlayersRemove(
                self.attr.toName(), self.scoreboard.attr.toName(),
                str(other.value)
            ))
            return self
        if isinstance(other, Score):
            self.api.system(ScoreboardPlayersOpISub(
                self.attr.toName(), self.scoreboard.attr.toName(),
                other.attr.toName(), other.scoreboard.attr.toName()
            ))
            return self
        assert False

    # Another methods
    # ---------------

    def PrintSource(self) -> NBTLiteral:
        return {"score": {
            "name": convert_var_name(self.attr.toName()),
            "objective": convert_var_name(self.scoreboard.attr.toName())
        }}


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
            result
        ))


def built_annotationsInit(apiObject: Type[API]):
    apiObject.build('builtins', {
        'score': ScoreClass,
        'scoreboard': ScoreboardClass,
        'print': Print,
        'str': StringClass,
        'fstr': FStringClass
    })


def built_codeInit(apiObject: API):
    # General scoreboard
    # ------------------

    apiObject.enterScope(Module(apiObject))
    scoreboard = Scoreboard(apiObject).InitsType(
        apiObject.useGlobalPrefix(['globals']),
        apiObject.useGlobalPrefix(['globals']))
    apiObject.analyzer.scope.write(
        'globals',
        scoreboard
    )
    apiObject.general.scoreboard = scoreboard


def built_codeFinish(apiObject: API):
    apiObject.leaveScope()
