"""
# Abstract

Pass
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Any
from abc import ABC, abstractmethod

# Custom libraries
# ----------------

from LangApi.api import API, Attr


# BASIC CLASS
# ===========


class Abstract(ABC):
    api: API

    def __init__(self, api: API):
        self.api = api


# BASIC PROPERTIES
# ================


class InitableType(Abstract, ABC):
    """
    <self.name>: <self> <ARGS>

    # except for Undefined:
    <self>: <PARENT> <ARGS>
    """

    def InitsType(self, *args: Abstract) -> Optional[Abstract]:
        ...


class Callable(Abstract, ABC):
    """
    <self> ( <ARGS> )
    """

    @abstractmethod
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        ...


class Assignable(Abstract, ABC):
    """
    <self> = <ARG>
    """

    @abstractmethod
    def Assign(self, other: Abstract) -> Optional[Abstract]:
        ...


class Formalizable(Abstract, ABC):
    """
    <TOKEN>
    """

    @abstractmethod
    def Formalize(self, token: str) -> Optional[Abstract]:
        ...


class Declareable(Abstract, ABC):
    """
    function <NAME>
    """

    attr: Attr

    @abstractmethod
    def Declare(self, *args: Any):
        ...


# BASIC OBJECT TYPES
# ==================


class Class(Callable, ABC):
    """
    Used properties:
    - Callable

    Also:
    - Added child for <ChangeableType> objects
    """

    @abstractmethod
    def GetChild(self) -> Abstract:
        ...


class Variable(InitableType, ABC):
    """
    Used properties:
    - ChangeableType

    Also:
    - Added name for getting a name
    """

    attr: Attr
    address: Attr

    def InitsType(self, attr: Attr, address: Attr, *args: Abstract) -> Optional[Abstract]:
        ...


# MATH EXPRESSIONS
# ================


# Arithmetic operators
# --------------------


class SupportAdd(Abstract, ABC):
    """
    <self> + <OTHER>
    """

    @abstractmethod
    def Add(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportSub(Abstract, ABC):
    """
    <self> - <OTHER>
    """

    @abstractmethod
    def Sub(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportMul(Abstract, ABC):
    """
    <self> * <OTHER>
    """
    @abstractmethod
    def Mul(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportDiv(Abstract, ABC):
    """
    <self> / <OTHER>
    """

    @abstractmethod
    def Div(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportMod(Abstract, ABC):
    """
    <self> % <OTHER>
    """

    @abstractmethod
    def Mod(self, other: Abstract) -> Optional[Abstract]:
        pass


# AugAssignment operators
# -----------------------


class SupportIAdd(Abstract, ABC):
    """
    <self> += <OTHER>
    """

    @abstractmethod
    def IAdd(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportISub(Abstract, ABC):
    """
    <self> -= <OTHER>
    """

    @abstractmethod
    def ISub(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportIMul(Abstract, ABC):
    """
    <self> *= <OTHER>
    """

    @abstractmethod
    def IMul(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportIDiv(Abstract, ABC):
    """
    <self> /= <OTHER>
    """

    @abstractmethod
    def IDiv(self, other: Abstract) -> Optional[Abstract]:
        pass


class SupportIMod(Abstract, ABC):
    """
    <self> %= <OTHER>
    """

    @abstractmethod
    def IMod(self, other: Abstract) -> Optional[Abstract]:
        pass
