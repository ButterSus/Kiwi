from __future__ import annotations

# Default libraries
# -----------------

from dataclasses import dataclass
from typing import Callable, List, Any, TYPE_CHECKING

# Custom libraries
# ----------------

if TYPE_CHECKING:
    from src.kiwiCompiler import Compiler


class Command:
    pass


# Declarations
# ------------

@dataclass
class UseMethod(Command):
    method: Callable[[...], Any]
    arguments: List[Any]


@dataclass
class UseMethodWithCompiler(Command):
    method: Callable[[Compiler, ...], Any]
    arguments: List[Any]


@dataclass
class ResetExpression(Command):
    ...
