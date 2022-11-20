"""
This code is unlicensed
By ButterSus

Previous stage:
    Tokenizer

About current stage:
    This stage is used to generate Abstract Syntax Tree
    AST -> SAO

Next stage:
    SAO
"""


from __future__ import annotations

from typing import List
from dataclasses import dataclass
from frontend.KiwiAnalyzer.scopes import Reference, Names
from frontend.std import KiwiType

import frontend.KiwiAST.colors


# DUMP COLORS
# ===========

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


class AST(Theme_Undefined):
    ...


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
    ...


@dataclass
class Break(Theme_Statements, AST):
    ...


@dataclass
class Continue(Theme_Statements, AST):
    ...


@dataclass
class AnnAssignment(Theme_Statements, AST):
    targets: List[expression]
    type: type
    value: List[expression]


@dataclass
class Assignment(Theme_Statements, AST):
    targets: List[expression]
    value: List[expression]


@dataclass
class AugAssignment(Theme_Statements, AST):
    targets: List[variable]
    op: str
    value: List[expression]


@dataclass
class Annotation(Theme_Statements, AST):
    targets: List[expression]
    type: type


@dataclass
class Return(Theme_Statements, AST):
    value: expression


# COMPOUND STATEMENTS
# ===================


@dataclass
class NamespaceDef(Theme_CStatements, AST):
    name: variable
    body_private: List[statement]
    body_public: List[statement]
    body_default: List[statement]


@dataclass
class FuncDef(Theme_CStatements, AST):
    name: variable
    params: List[Parameter | RefParameter]
    default: List[expression]
    returns: Parameter | RefParameter
    promiser: expression
    body: List[statement]


@dataclass
class Parameter(Theme_Statements, AST):
    target: List[variable]
    type: type


@dataclass
class LambdaDef(Theme_Statements, AST):
    targets: List[variable]
    returns: expression


@dataclass
class LambdaParameter(Theme_Statements, AST):
    target: variable


@dataclass
class RefParameter(Theme_Statements, AST):
    target: variable


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


@dataclass
class IfExpression(Theme_Expressions, AST):
    condition: expression
    then: expression
    or_else: expression


@dataclass
class Compare(Theme_Expressions, AST):
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

    def dump(self) -> Names:
        return Names(self.target.dump() + self.attribute.dump())


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
    value: str

    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return self.value


# TOKEN BASICS
# ============


class Selector(str, Token):
    ...


class Name(str, Token):
    def dump(self) -> Names:
        return Names([self])


class Word(str, Token):
    ...


class String(str, Token):
    ...


class Number(str, Token):
    ...


variable = Name | Attribute | Reference

expression = \
    Expression | \
    IfExpression | \
    LambdaDef | \
    Compare | \
    UnaryOp | \
    BinaryOp | \
    Selector | \
    Call | \
    MatchExpr | \
    variable | \
    String | \
    Number

type = expression | Reference

simple_stmt = \
    Assignment | \
    expression | \
    Return | \
    Pass | \
    Break | \
    Continue

compound_stmt = \
    FuncDef | \
    NamespaceDef | \
    IfElse | \
    While | \
    MatchCase

statement = \
    simple_stmt | \
    compound_stmt
