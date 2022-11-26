from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *


class ScoreChild(Argument):
    def Annotation(self, *args: Argument) -> Optional[Argument]:
        pass


class Score(Class):
    child = ScoreChild

    def Annotation(self, *_) -> Optional[Argument]:
        print(1)
        return self

    def Call(self, *args: Argument) -> Optional[Argument]:
        pass


def built_init(api: Type[API]):
    api.build('builtins', {
        'score': Score
    })
