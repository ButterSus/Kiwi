from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from std.tools import *
if TYPE_CHECKING:
    from src.assets.kiwiScope import Argument


# DATA TYPES
# ==========


class Score(KiwiType):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, *args: Any):
        pass

    def Assignment(self, value: Argument):
        pass


class Namespace(KiwiType):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, *args: Any):
        assert False

    def Assignment(self, value: Argument):
        assert False


class Function(KiwiType):
    name: str
    constructor: Constructor

    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    def Annotation(self, *args: Any):
        assert False

    def Assignment(self, value: Argument):
        assert False
