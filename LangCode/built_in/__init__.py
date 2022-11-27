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

    def ChangeType(self, name: Attr, criteria: String = None) -> Scoreboard:
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


class Score(Variable):
    scoreboard: Scoreboard

    def ChangeType(self, name: Attr, scoreboard: Abstract = None) -> Score:
        # Handle <NAME>
        # -------------

        assert isinstance(name, Attr)
        self.name = name

        # Handle <SCOREBOARD>
        # -------------------

        if scoreboard is None:
            scoreboard = self.api.general.scoreboard
        assert isinstance(scoreboard, Scoreboard)
        self.scoreboard = scoreboard

        return self

    def Assign(self, arg: Abstract):
        if isinstance(arg, Number):
            self.api.system(f'scoreboard players set {self.name.toName()} '
                            f'{self.scoreboard.name.toName()} {arg.value}')
            return
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

    scoreboard = Scoreboard(apiObject).ChangeType(
        Attr([apiObject.config['project_name']]))
    apiObject.analyzer.scope.write(
        apiObject.config['project_name'],
        scoreboard
    )
    apiObject.general.scoreboard = scoreboard
