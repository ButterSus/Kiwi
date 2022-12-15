from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Any, TYPE_CHECKING  # noqa: F401
from abc import ABC, abstractmethod

import LangApi

# Custom libraries
# ----------------

from LangApi.api import API, Attr
from Kiwi.components.kiwiTools import AST_Task
from Kiwi.components.kiwiScope import (
    CodeScope as _CodeScope,
    NoCodeScope as _NoCodeScope
)

if TYPE_CHECKING:
    from LangApi.bytecode import NBTLiteral
    import LangCode  # noqa: F401


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

    @abstractmethod
    def InitsType(self, *args: Abstract | Attr) -> Optional[Abstract]:
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
    <TOKEN> or any scope
    """

    @abstractmethod
    def Formalize(self, *args) -> Optional[Abstract]:
        ...


class Printable(Abstract, ABC):
    """
    print(<self>
    """

    @abstractmethod
    def PrintSource(self) -> NBTLiteral:
        ...


class TransPredicate(Abstract, ABC):
    """
    <self> to JSON-PREDICATE
    """

    @abstractmethod
    def transPredicate(self) -> NBTLiteral:
        ...


# BASIC OBJECT TYPES
# ==================


class ScopeWithCode(_CodeScope, ABC):
    def Return(self, value: LangApi.Construct):
        i = 0
        while not isinstance(function:=self.api.getThisScope(i), self.api.LangCode.Function):  # noqa
            i += 1
        function: LangCode.Function
        return self.api.Construct(
                'Assign',
                function.returns,
                [value]
            )

class ScopeWithoutCode(_NoCodeScope):
    ...


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

    @abstractmethod
    def InitsType(self, attr: Attr, address: Attr, *args: Abstract) -> Optional[Abstract]:
        ...


# MATH EXPRESSIONS
# ================


# Arithmetic operators
# --------------------


class SupportEquals(Abstract, ABC):
    """
    <self> == <other>
    """

    @abstractmethod
    def Equals(self, other: Abstract) -> NBTLiteral:
        ...


class SupportNotEquals(Abstract, ABC):
    """
    <self> != <other>
    """

    @abstractmethod
    def NotEquals(self, other: Abstract) -> NBTLiteral:
        ...


class SupportLessThanEquals(Abstract, ABC):
    """
    <self> <= <other>
    """

    @abstractmethod
    def LessThanEquals(self, other: Abstract) -> NBTLiteral:
        ...


class SupportGreaterThanEquals(Abstract, ABC):
    """
    <self> >= <other>
    """

    @abstractmethod
    def GreaterThanEquals(self, other: Abstract) -> NBTLiteral:
        ...


class SupportLessThan(Abstract, ABC):
    """
    <self> < <other>
    """

    @abstractmethod
    def LessThan(self, other: Abstract) -> NBTLiteral:
        ...


class SupportGreaterThan(Abstract, ABC):
    """
    <self> > <other>
    """

    @abstractmethod
    def GreaterThan(self, other: Abstract) -> NBTLiteral:
        ...


class SupportPlus(Abstract, ABC):
    """
    + <self>
    """

    @abstractmethod
    def Plus(self) -> Optional[Abstract]:
        ...


class SupportMinus(Abstract, ABC):
    """
    - <self>
    """

    @abstractmethod
    def Minus(self) -> Optional[Abstract]:
        ...


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
