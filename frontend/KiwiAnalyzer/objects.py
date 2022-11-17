from dataclasses import dataclass
import frontend.std as std


class KiwiObject:
    ...


@dataclass
class Variable(KiwiObject):
    type: std.KiwiType


@dataclass
class Function(KiwiObject):
    ...
