from __future__ import annotations

# Default libraries
# -----------------

from typing import List
from tokenize import TokenInfo as _TokenInfo
from dataclasses import dataclass, field

# Custom libraries
# ----------------

import Kiwi.components.kiwiColors as colors
from Kiwi.components.kiwiScope import Attr, DirAttr  # noqa


# Colors for dumping
# ------------------

class Theme_Undefined:
    color = colors.White + colors.BackgroundDefault


class Theme_Start:
    color = colors.Red + colors.BackgroundDefault


class Theme_Statements:
    color = colors.White + colors.BackgroundDefault


class Theme_CStatements:
    color = colors.Yellow + colors.BackgroundDefault


class Theme_Expressions:
    color = colors.Cyan + colors.BackgroundDefault


class Theme_Tokens:
    color = colors.Magenta + colors.BackgroundBlack


# STARTING RULES
# ==============


@dataclass
class AST(Theme_Undefined):
    start: tuple[int, int]
    end: tuple[int, int]


@dataclass
class Module(Theme_Start, AST):
    imports: List[Alias]
    body: List[statement]


# IMPORT STATEMENTS
# =================


@dataclass
class Alias(Theme_Expressions, AST):
    directory: Name
    as_name: Name | List[Alias]


# SIMPLE STATEMENTS
# =================


@dataclass
class Pass(Theme_Statements, AST):
    pass


@dataclass
class Break(Theme_Statements, AST):
    pass


@dataclass
class Continue(Theme_Statements, AST):
    pass


@dataclass
class AnnAssignment(Theme_Statements, AST):
    targets: List[expression]
    data_type: data_type
    args: List[expression]
    values: List[expression]


@dataclass
class Assignment(Theme_Statements, AST):
    targets: List[expression]
    values: List[expression]


@dataclass
class AugAssignment(Theme_Statements, AST):
    targets: List[expression]
    op: Token
    values: List[expression]


@dataclass
class Annotation(Theme_Statements, AST):
    targets: List[expression]
    data_type: data_type
    args: List[expression]


@dataclass
class Return(Theme_Statements, AST):
    value: expression


# COMPOUND STATEMENTS
# ===================


@dataclass
class NamespaceDef(Theme_CStatements, AST):
    name: Name
    blocks: List[PrivateBlock | PublicBlock | DefaultBlock]


@dataclass
class PrivateBlock(Theme_CStatements, AST):
    body: List[statement]


@dataclass
class PublicBlock(Theme_CStatements, AST):
    body: List[statement]


@dataclass
class DefaultBlock(Theme_CStatements, AST):
    body: List[statement]


@dataclass
class FuncDef(Theme_CStatements, AST):
    name: Name
    params: List[Parameter | RefParameter]
    default: List[expression]
    returns: ReturnParameter | ReturnRefParameter
    promiser: expression
    body: List[statement]


@dataclass
class ReturnParameter(Theme_Statements, AST):
    data_type: data_type
    args: List[expression]


@dataclass
class ReturnRefParameter(Theme_Statements, AST):
    target: expression


@dataclass
class Parameter(Theme_Statements, AST):
    targets: List[expression]
    data_type: data_type
    args: List[expression]


@dataclass
class RefParameter(Theme_Statements, AST):
    target: expression


@dataclass
class LambdaDef(Theme_Statements, AST):
    targets: List[expression]
    returns: expression


@dataclass
class LambdaParameter(Theme_Statements, AST):
    target: expression


@dataclass
class IfElse(Theme_CStatements, AST):
    condition: expression
    then: List[statement]
    or_else: List[statement]


@dataclass
class While(Theme_CStatements, AST):
    condition: expression
    body: List[statement]


@dataclass
class MatchCase(Theme_CStatements, AST):
    value: expression
    cases: List[Case]


@dataclass
class Case(Theme_Statements, AST):
    key: expression
    body: List[statement]


# EXPRESSIONS
# ===========


@dataclass
class Expression(Theme_Expressions, AST):
    value: expression

    def isGroup(self) -> bool:
        if isinstance(self.value, NotFullExpression):
            return self.value.isGroup
        return False


@dataclass
class NotFullExpression(Theme_Expressions, AST):
    value: expression
    isGroup: bool = field(default=False)

    def setGroup(self, value: bool):
        self.isGroup = value
        return self


@dataclass
class IfExpression(Theme_Expressions, AST):
    condition: expression
    then: expression
    or_else: expression


@dataclass
class Disjunctions(Theme_Expressions, AST):
    values: List[expression]


@dataclass
class Conjunctions(Theme_Expressions, AST):
    values: List[expression]


@dataclass
class Comparisons(Theme_Expressions, AST):
    values: List[expression]
    ops: List[Token]


@dataclass
class UnaryOp(Theme_Expressions, AST):
    x: expression
    op: Token


@dataclass
class BinaryOp(Theme_Expressions, AST):
    x: expression
    y: expression
    op: Token


@dataclass
class Call(Theme_Expressions, AST):
    target: expression
    args: List[expression]


@dataclass
class Attribute(Theme_Expressions, AST):
    target: expression
    attribute: Name

    def toAttr(self) -> Attr:
        return Attr(self.target.toAttr() + self.attribute.toAttr())


# MATCH KEYS
# ==========


@dataclass
class MatchExpr(Theme_Expressions, AST):
    value: expression
    cases: List[MatchKey]


@dataclass
class MatchKey(Theme_Expressions, AST):
    from_this: expression
    to_this: expression
    value: expression


class Token(Theme_Tokens):
    start: tuple[int, int]
    end: tuple[int, int]
    value: str

    def __init__(self, start: tuple[int, int],
                 end: tuple[int, int],
                 value: str):
        self.start = start
        self.end = end
        self.value = value

    def __repr__(self) -> str:
        return self.value


# STATES AND SELECTORS
# ====================


@dataclass
class Selector(Theme_Expressions, AST):
    target: str
    state: State


@dataclass
class State(Theme_Expressions, AST):
    key: str
    value: NBT


@dataclass
class NBT(Theme_Expressions, AST):
    tag: str



# TOKEN BASICS
# ============


class Name(Token):
    def toAttr(self) -> Attr:
        return Attr([self.value])


class Word(Token):
    pass


class String(Token):
    def getString(self) -> str:
        value = str()
        match self.value[-1]:
            case "\"":
                value = self.value[self.value.index("\""):]
            case "\'":
                value = self.value[self.value.index("\'"):]

        match value[-1]:
            case "\"":
                return value.strip("\"")
            case "\'":
                return value.strip("\'")

    def getPrefix(self) -> str:
        match self.value[-1]:
            case "\"":
                return self.value[:self.value.index("\"")]
            case "\'":
                return self.value[:self.value.index("\'")]


class Number(Token):
    pass


expression = \
    Expression | \
    IfExpression | \
    LambdaDef | \
    Disjunctions | \
    Conjunctions | \
    Comparisons | \
    UnaryOp | \
    BinaryOp | \
    Selector | \
    Call | \
    MatchExpr | \
    Name | Attribute | \
    String | \
    Number

data_type = expression

simple_stmt = \
    Assignment | \
    expression | \
    Return | \
    Pass | \
    Break | \
    Continue

compound_stmt = \
    Module | \
    FuncDef | \
    NamespaceDef | \
    IfElse | \
    While | \
    MatchCase

statement = \
    simple_stmt | \
    compound_stmt
