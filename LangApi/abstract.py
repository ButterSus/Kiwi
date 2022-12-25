"""
This module provides you basic classes to
create new frontend objects.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Optional, Any, TYPE_CHECKING, Callable as _Callable, Type, Dict, List  # noqa: F401
from abc import ABC, abstractmethod
from inspect import isclass
from enum import Enum, auto
from dataclasses import dataclass, field

# Custom libraries
# ----------------

from LangApi.api import API as _API
from components.kiwiScope import Attr as _Attr
from components.kiwiScope import CodeScope

if TYPE_CHECKING:
    from LangApi.bytecode import NBTLiteral as _NBTLiteral
    from frontend.kiwiAnalyzer import Analyzer as _Analyzer
    from components.kiwiConstructor import Constructor as _Constructor


# BASIC CLASS
# ===========


class ConstructMethod(Enum):
    """
    This enum defines all methods of Kiwi objects
    """

    # Basic initializations
    # ---------------------

    InitsType = auto()
    Formalize = auto()

    # Binary operators
    # ----------------

    AddOperation = auto()
    SubOperation = auto()
    MulOperation = auto()
    DivOperation = auto()
    ModOperation = auto()

    # Unary operators
    # ----------------

    PlusOperation = auto()
    MinusOperation = auto()

    # Aug operators
    # -------------

    AugAddOperation = auto()
    AugSubOperation = auto()
    AugMulOperation = auto()
    AugDivOperation = auto()
    AugModOperation = auto()

    # Another operators
    # -----------------

    AssignOperation = auto()

    # Special methods
    # ---------------

    Return = auto()
    Call = auto()
    Reference = auto()
    Annotation = auto()
    AnnAssign = auto()
    GetChild = auto()


@dataclass
class Construct:
    """
    This dataclass stores analyzer request to run any method of built-in object or grammar constructions.
    API.visit method can launch it.
    """
    method: ConstructMethod
    """
    The method identifier to run
    e.g:
    ConstructMethod.AddOperation
    """
    parent: Type[Abstract] | Abstract
    """
    The object or class of the method to run,
    if it's class, then it should take api parameter to initialize
    """
    arguments: List[Any]
    """
    The arguments of the method to run,
    It can be absolutely anything
    """
    raw_args: bool = field(default=False)
    """
    By default, arguments will be passed to visitor, that will launch Construct before to pass
    it as argument. (it's made to make it more abstract)
    e.g:
    Let's assume we have this structure:
    Construct(  # This construct will be handled last of all
        method = "Add",
        parent = SomeClassOrObject
        arguments = [
            Construct(  # This construct will be handled first of all
                method = "Add",
                parent = SomeClassOrObject
                arguments = [1, 2]
            )
        ]
    ),
    But if raw_args equals to True, then arguments will not be handled by visitor
    """


class Abstract(ABC):
    constructor: _Constructor
    analyzer: _Analyzer
    api: _API

    _was_associated = False

    def __init__(self, api: _API):
        self.constructor = api.analyzer.constructor
        self.analyzer = api.analyzer
        self.api = api

        if self.__class__._was_associated:
            return
        for key, value in self.associations.items():
            if isclass(value):
                value: Type[Abstract]
                self.associations[key] = value(self.api)
        self.__class__._was_associated = True

    def loader(self, command: ConstructMethod) -> _Callable:
        cases = {
            ConstructMethod.InitsType: 'InitsType',
            ConstructMethod.Formalize: 'Formalize',

            ConstructMethod.AddOperation: 'Add',
            ConstructMethod.SubOperation: 'Sub',
            ConstructMethod.MulOperation: 'Mul',
            ConstructMethod.DivOperation: 'Div',
            ConstructMethod.ModOperation: 'Mod',
            ConstructMethod.PlusOperation: 'Plus',
            ConstructMethod.MinusOperation: 'Minus',

            ConstructMethod.AugAddOperation: 'IAdd',
            ConstructMethod.AugSubOperation: 'ISub',
            ConstructMethod.AugMulOperation: 'IMul',
            ConstructMethod.AugDivOperation: 'IDiv',
            ConstructMethod.AugModOperation: 'IMod',

            ConstructMethod.AssignOperation: 'Assign',

            ConstructMethod.Return: 'Return',
            ConstructMethod.Call: 'Call',
            ConstructMethod.Reference: 'Reference',
            ConstructMethod.Annotation: 'Annotation',
            ConstructMethod.AnnAssign: 'AnnAssign',
            ConstructMethod.GetChild: 'GetChild',
        }
        assert command in cases.keys()
        method = cases.get(command)
        assert method in dir(self)
        return self.__getattribute__(method)

    associations: Dict[str, Abstract] = dict()
    """
    It's used to create attributes
    """

    def setAttribute(self, attr: _Attr, value: Any) -> Any:
        """
        You can override this method
        to handle setting attributes by yourself
        """
        if len(attr) > 1:
            result = self.associations[attr[0]]
            assert isinstance(result, Abstract)
            return result.setAttribute(attr[1:], value)
        return Construct(
            ConstructMethod.AssignOperation,
            self.getAttribute(attr),
            [value]
        )

    def getAttribute(self, attr: _Attr) -> Abstract | Any:
        """
        You can override this method
        to handle getting attributes by yourself
        """
        assert attr[0] in self.associations.keys()
        if len(attr) > 1:
            result = self.associations[attr[0]]
            assert isinstance(result, Abstract)
            return result.getAttribute(attr[1:])
        return self.associations[attr[0]]


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


class Returnable(Abstract, ABC):
    """
    Object that can return a value.
    """

    @abstractmethod
    def Return(self, value: Abstract):
        ...


# BASIC OBJECT TYPES
# ==================


class Class(Callable, ABC):
    """
    It's used to represent a class
    """

    @abstractmethod
    def GetChild(self) -> Type[Abstract]:
        ...


class Variable(InitableType, ABC):
    """
    It's used to represent a class that support variables
    """

    attr: _Attr
    """
    Absolute path to the object
    """

    address: _Attr
    """
    Relative path to the object
    """

    isNative = False
    """
    It's used if you want to pass *args without analyzer handling
    """

    @abstractmethod
    def InitsType(self, attr: _Attr, address: _Attr, *args: Abstract) -> Optional[Abstract]:
        ...


class Const(Abstract, ABC):
    """
    It's used to represent a class that support compile time AnnAssign
    """

    @abstractmethod
    def InitsTypeAssign(self, attr: _Attr, address: _Attr, *args: Abstract) -> Optional[Abstract]:
        ...


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
    def __init__(self, api: _API):
        self.content = dict()
        self.code = dict()
        super().__init__(api)



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
