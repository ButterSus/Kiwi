from __future__ import annotations

# Default libraries
# -----------------

from typing import Type

# Custom libraries
# ----------------

from LangApi import *
from LangCode import Number, String


class Scoreboard(Variable):
    criteria: String

    def InitsType(self, name: Attr, criteria: String = None) -> Scoreboard:
        # Handle <NAME>
        # -------------

        assert isinstance(name, Attr)
        self.name = name

        # Handle <CRITERIA>
        # -----------------

        if criteria is None:
            criteria = String(self.api).Formalize('"dummy"')
        assert isinstance(criteria, String)
        self.criteria = criteria

        self.api.system(f'scoreboard objectives add {self.name.toName()} {self.criteria.value}')
        return self


class ScoreboardClass(Class):
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass

    def GetChild(self) -> Scoreboard:
        return Scoreboard(self.api)


class Score(Variable, Assignable,
            SupportAdd, SupportSub,
            SupportIAdd, SupportISub):
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

    def Assign(self, other: Abstract) -> Score:
        if isinstance(other, Number):
            self.api.system(f'scoreboard players set {self.attr.toName()} '
                            f'{self.scoreboard.name.toName()} {other.value}')
            return self
        if isinstance(other, Score):
            self.api.system(f'scoreboard players operation {self.attr.toName()} '
                            f'{self.scoreboard.name.toName()} = '
                            f'{other.attr.toName()} {other.scoreboard.name.toName()}')
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
            self.api.system(f'scoreboard players operation {self.attr.toName()} '
                            f'{self.scoreboard.name.toName()} add '
                            f'{other.value}')
            return self
        if isinstance(other, Score):
            self.api.system(f'scoreboard players operation {self.attr.toName()} '
                            f'{self.scoreboard.name.toName()} += '
                            f'{other.attr.toName()} {other.scoreboard.name.toName()}')
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
            self.api.system(f'scoreboard players operation {self.attr.toName()} '
                            f'{self.scoreboard.name.toName()} remove '
                            f'{other.value}')
            return self
        if isinstance(other, Score):
            self.api.system(f'scoreboard players operation {self.attr.toName()} '
                            f'{self.scoreboard.name.toName()} += '
                            f'{other.attr.toName()} {other.scoreboard.name.toName()}')
            return self
        assert False


class ScoreClass(Class):
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        pass

    def GetChild(self) -> Score:
        return Score(self.api)


def built_annotationsInit(apiObject: Type[API]):
    apiObject.build('builtins', {
        'score': ScoreClass,
        'scoreboard': ScoreboardClass
    })


def built_codeInit(apiObject: API):
    # General scoreboard
    # ------------------

    scoreboard = Scoreboard(apiObject).InitsType(
        Attr([apiObject.config['project_name']]))
    apiObject.analyzer.scope.write(
        apiObject.config['project_name'],
        scoreboard
    )
    apiObject.general.scoreboard = scoreboard
