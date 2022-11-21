from __future__ import annotations

# Default libraries
# -----------------

from dataclasses import dataclass
from typing import Callable, Type, List, Any

# Custom libraries
# ----------------

from std.tools import KiwiType


class Command:
    pass


# Declarations
# ------------

@dataclass
class CallMethod(Command):
    method: Callable[[Type[KiwiType], ...], None]
    arguments: List[Any]
