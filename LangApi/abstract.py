"""
# Abstract

Pass
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Any, Type
from abc import ABC, abstractmethod

# Custom libraries
# ----------------

from LangApi.api import API, Construct


# BASIC OBJECTS
# =============


class Abstract(ABC):
    api: API

    def __init__(self, api: API):
        self.api = api


class Argument(Abstract, ABC):
    @abstractmethod
    def Annotation(self, *args: Argument) -> Optional[Argument]:
        ...


class Constant(Argument, ABC):
    value: Any

    @abstractmethod
    def Annotation(self, token: str, *args: Argument) -> Type[Constant]:
        ...


class Callable(Abstract, ABC):
    @abstractmethod
    def Call(self, *args: Argument) -> Optional[Argument]:
        ...


class Function(Argument, Callable, ABC):
    ...


class Class(Argument, Callable, ABC):
    child: Type[Argument]


# MATH EXPRESSIONS
# ================


class SupportAdd(Argument, ABC):
    @abstractmethod
    def Add(self, other: Argument) -> Optional[Argument]:
        pass


class SupportSub(Argument, ABC):
    @abstractmethod
    def Sub(self, other: Argument) -> Optional[Argument]:
        pass


class SupportAddSub(SupportAdd, SupportSub, ABC):
    ...


class SupportMul(Argument, ABC):
    @abstractmethod
    def Mul(self, other: Argument) -> Optional[Argument]:
        pass


class SupportDiv(Argument, ABC):
    @abstractmethod
    def Div(self, other: Argument) -> Optional[Argument]:
        pass


class SupportMod(Argument, ABC):
    @abstractmethod
    def Mod(self, other: Argument) -> Optional[Argument]:
        pass


class SupportMulDivMod(SupportMul, SupportDiv, SupportMod, ABC):
    ...


class SupportArithmetic(SupportAddSub, SupportMulDivMod, ABC):
    ...
