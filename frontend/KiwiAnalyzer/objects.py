"""
This code is unlicensed
By ButterSus

Previous stage:
    AST

About current stage:
    This stage is used to generate Semantic Analyzer Objects
    SAO -> Compiler

Next stage:
    Compiler
"""


from dataclasses import dataclass
from typing import Type
import frontend.std as std


class KiwiObject:
    ...


# SIMPLE STATEMENTS
# =================





@dataclass
class Variable(KiwiObject):
    type: std.KiwiType | Type[std.KiwiType]


@dataclass
class Function(KiwiObject):
    ...
