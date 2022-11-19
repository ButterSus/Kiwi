from dataclasses import dataclass
from typing import Type
import frontend.std as std


class KiwiObject:
    ...


@dataclass
class Variable(KiwiObject):
    type: std.KiwiType | Type[std.KiwiType]


@dataclass
class Function(KiwiObject):
    ...
