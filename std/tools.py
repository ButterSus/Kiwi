from __future__ import annotations

# Default libraries
# -----------------

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

# Custom libraries
# ----------------

if TYPE_CHECKING:
    from src.assets.kiwiScope import Argument
    from build import Constructor


@dataclass
class Constant:
    value: int | float | str | list


class KiwiType(ABC):
    name: str
    constructor: Constructor

    @abstractmethod
    def __init__(self, name: str, constructor: Constructor):
        self.name = name
        self.constructor = constructor

    @abstractmethod
    def Annotation(self, *args: Any):
        pass

    @abstractmethod
    def Assignment(self, value: Argument):
        pass


StdOps = {
    '=': 'Assignment'
}
