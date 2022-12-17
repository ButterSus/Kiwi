"""
Copyright (c) 2022 Krivoshapkin Edward

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Any, TYPE_CHECKING  # noqa: F401
from abc import ABC, abstractmethod

# Custom libraries
# ----------------

from LangApi.api import API
from Kiwi.components.kiwiScope import Attr

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
