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
class CallMethod(Command):
    method: Callable[[...], None]
    arguments: List[Any]


@dataclass
class CallMethodWithCompiler(Command):
    method: Callable[[Compiler, ...], None]
    arguments: List[Any]
