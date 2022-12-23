"""
This module provides you basic classes to
create new frontend objects.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Any, TYPE_CHECKING, Callable as _Callable  # noqa: F401
from abc import ABC, abstractmethod

# Custom libraries
# ----------------

from LangApi.api import API as _API, ConstructMethod as _ConstructMethod
from components.kiwiScope import Attr as _Attr
from components.kiwiScope import CodeScope

if TYPE_CHECKING:
    from LangApi.bytecode import NBTLiteral as _NBTLiteral
    from frontend.kiwiAnalyzer import Analyzer as _Analyzer
    from components.kiwiConstructor import Constructor as _Constructor


# BASIC CLASS
# ===========


class Abstract(ABC):
    constructor: _Constructor
    analyzer: _Analyzer
    api: _API

    def __init__(self, analyzer: _Analyzer, api: _API):
        self.constructor = analyzer.constructor
        self.analyzer = analyzer
        self.api = api

    def loader(self, command: _ConstructMethod) -> _Callable:
        cases = {
            _ConstructMethod.InitsType: 'InitsType',
            _ConstructMethod.Formalize: 'Formalize',

            _ConstructMethod.AddOperation: 'Add',
            _ConstructMethod.SubOperation: 'Sub',
            _ConstructMethod.MulOperation: 'Mul',
            _ConstructMethod.DivOperation: 'Div',
            _ConstructMethod.ModOperation: 'Mod',
            _ConstructMethod.PlusOperation: 'Plus',
            _ConstructMethod.MinusOperation: 'Minus',

            _ConstructMethod.AssignOperation: 'Assign',

            _ConstructMethod.Call: 'Call',
            _ConstructMethod.Reference: 'Reference',
            _ConstructMethod.Annotation: 'Annotation',
            _ConstructMethod.GetChild: 'GetChild',
        }
        assert command in cases.keys()
        method = cases.get(command)
        assert method in dir(self)
        return self.__getattribute__(method)


# BASIC PROPERTIES
# ================


class InitableType(Abstract, ABC):
    """
    Object that can be annotated.
    """

    @abstractmethod
    def InitsType(self, *args: Abstract | Any) -> Optional[Abstract]:
        ...


class Callable(Abstract, ABC):
    """
    Object that can be called (Can be not function).
    """

    @abstractmethod
    def Call(self, *args: Abstract) -> Optional[Abstract]:
        ...


class Assignable(Abstract, ABC):
    """
    Object that supports equals operator.
    """

    @abstractmethod
    def Assign(self, other: Abstract) -> Optional[Abstract]:
        ...


class Formalizable(Abstract, ABC):
    """
    Object that can be initialized in compile time.
    """

    @abstractmethod
    def Formalize(self, *args) -> Optional[Abstract]:
        ...


class Printable(Abstract, ABC):
    """
    Object that can be printed.
    """

    @abstractmethod
    def PrintSource(self) -> _NBTLiteral:
        ...


class TransPredicate(Abstract, ABC):
    """
    Object that can be used as a predicate.
    """

    @abstractmethod
    def transPredicate(self) -> _NBTLiteral:
        ...


# BASIC OBJECT TYPES
# ==================


class Class(Callable, ABC):
    """
    It's used to represent a class
    """

    @abstractmethod
    def GetChild(self) -> Abstract:
        ...


class Variable(InitableType, ABC):
    """
    It's used to represent a class that support variables
    """

    attr: _Attr
    address: _Attr
    isNative = False

    @abstractmethod
    def InitsType(self, attr: _Attr, address: _Attr, *args: Abstract) -> Optional[Abstract]:
        ...


class Const(Assignable, ABC):
    """
    It's used to represent a class that support compile time AnnAssign
    """


class Format(Formalizable, ABC):
    """
    It's used to represent a constant token,
    that will be initialized with a token string
    """

class Block(Formalizable, CodeScope, ABC):
    """
    It's used to represent a construction with
    code block, code block can be also a predicate, JSON,
    or even something else.
    """
    def __init__(self, analyzer: _Analyzer, api: _API):
        self.content = dict()
        self.code = dict()
        super().__init__(analyzer, api)



# MATH EXPRESSIONS
# ================


# Compare operators
# -----------------


class SupportEquals(Abstract, ABC):
    """
    <self> == <other>
    """

    @abstractmethod
    def Equals(self, other: Abstract) -> _NBTLiteral:
        ...


class SupportNotEquals(Abstract, ABC):
    """
    <self> != <other>
    """

    @abstractmethod
    def NotEquals(self, other: Abstract) -> _NBTLiteral:
        ...


class SupportLessThanEquals(Abstract, ABC):
    """
    <self> <= <other>
    """

    @abstractmethod
    def LessThanEquals(self, other: Abstract) -> _NBTLiteral:
        ...


class SupportGreaterThanEquals(Abstract, ABC):
    """
    <self> >= <other>
    """

    @abstractmethod
    def GreaterThanEquals(self, other: Abstract) -> _NBTLiteral:
        ...


class SupportLessThan(Abstract, ABC):
    """
    <self> < <other>
    """

    @abstractmethod
    def LessThan(self, other: Abstract) -> _NBTLiteral:
        ...


class SupportGreaterThan(Abstract, ABC):
    """
    <self> > <other>
    """

    @abstractmethod
    def GreaterThan(self, other: Abstract) -> _NBTLiteral:
        ...


class SupportComparison(SupportEquals, SupportNotEquals,
                        SupportLessThan, SupportLessThanEquals,
                        SupportGreaterThan, SupportGreaterThanEquals,
                        ABC):
    ...


# Arithmetic operators
# --------------------


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


class SupportArithmetic(SupportAdd, SupportSub,
                        SupportMul, SupportDiv, SupportMod,
                        ABC):
    ...


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


class SupportAugArithmetic(SupportIAdd, SupportISub,
                           SupportIMul, SupportIDiv, SupportIMod,
                           ABC):
    ...
