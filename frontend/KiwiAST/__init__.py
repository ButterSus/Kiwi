from __future__ import annotations

from typing import List, Literal
from dataclasses import dataclass

import frontend.KiwiAST.colors

_type = Literal['score', 'scoreboard', 'auto']


# DUMP COLORS
# ===========

class Theme_Undefined:
    color = colors.White + colors.BackgroundDefault


class Theme_Start:
    color = colors.Red + colors.BackgroundDefault


class Theme_Statements:
    color = colors.LightYellow + colors.BackgroundDefault


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
    body: List[_statement]


# SIMPLE STATEMENTS
# =================


@dataclass
class Pass(Theme_Statements, AST):
    ...


@dataclass
class AnnAssignment(Theme_Statements, AST):
    targets: List[Name]
    type: _type
    value: List[_expression]


@dataclass
class Assignment(Theme_Statements, AST):
    targets: List[Name]
    value: List[_expression]


@dataclass
class AugAssignment(Theme_Statements, AST):
    targets: List[Name]
    op: str
    value: List[_expression]


@dataclass
class Annotation(Theme_Statements, AST):
    targets: List[Name]
    type: _type


@dataclass
class Return(Theme_Statements, AST):
    value: _expression


# COMPOUND STATEMENTS
# ===================


@dataclass
class NamespaceDef(Theme_Statements, AST):
    name: Name
    body_private: List[_statement]
    body_public: List[_statement]
    body_default: List[_statement]


@dataclass
class FuncDef(Theme_Statements, AST):
    name: Name
    params: List[Parameter | RefParameter]
    default: List[_expression]
    returns: Parameter | RefParameter
    body: List[_statement]


@dataclass
class Parameter(Theme_Statements, AST):
    target: Name
    type: _type


@dataclass
class RefParameter(Theme_Statements, AST):
    target: Name


@dataclass
class IfElse(Theme_Statements, AST):
    condition: _expression
    then: List[_statement]
    or_else: List[_statement]

# EXPRESSIONS
# ===========


@dataclass
class Expression(Theme_Expressions, AST):
    value: _expression


@dataclass
class IfExpression(Theme_Expressions, AST):
    condition: _expression
    then: _expression
    or_else: _expression


@dataclass
class Compare(Theme_Expressions, AST):
    values: List[_expression]
    ops: List[str]


@dataclass
class UnaryOp(Theme_Expressions, AST):
    x: _expression
    op: str


@dataclass
class BinaryOp(Theme_Expressions, AST):
    x: _expression
    y: _expression
    op: str


class Token:
    ...


class Name(str, Theme_Tokens, Token):
    ...


class String(str, Theme_Tokens, Token):
    ...


class Int(int, Theme_Tokens, Token):
    ...


class Float(float, Theme_Tokens, Token):
    ...


_expression = \
    Expression | \
    IfExpression | \
    Compare | \
    UnaryOp | \
    BinaryOp | \
    Name | \
    String | \
    Int | \
    Float

_simple_stmt = \
    Assignment | \
    Return | \
    Pass

_compound_stmt = \
    FuncDef | \
    NamespaceDef | \
    IfElse

_statement = \
    _simple_stmt | \
    _compound_stmt
