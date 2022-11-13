from __future__ import annotations

from typing import Any, List, Literal
from dataclasses import dataclass

_identifier = str
_type = Literal['score', 'scoreboard', 'auto']


# STARTING RULES
# ==============


class AST:
    ...


@dataclass
class Module(AST):
    body: List[_statement]


# SIMPLE STATEMENTS
# =================


@dataclass
class Pass(AST):
    ...


@dataclass
class AnnAssignment(AST):
    targets: List[_identifier]
    type: _type
    value: List[_expression]


@dataclass
class Assignment(AST):
    targets: List[_identifier]
    value: List[_expression]


@dataclass
class AugAssignment(AST):
    targets: List[_identifier]
    op: str
    value: List[_expression]


@dataclass
class Annotation(AST):
    targets: List[_identifier]
    type: _type


@dataclass
class Return(AST):
    value: _expression


# COMPOUND STATEMENTS
# ===================


@dataclass
class NamespaceDef(AST):
    name: _identifier
    body_private: List[_statement]
    body_public: List[_statement]
    body_default: List[_statement]


@dataclass
class FuncDef(AST):
    name: _identifier
    params: List[Parameter | RefParameter]
    default: List[_expression]
    returns: Parameter | RefParameter
    body: List[_statement]


@dataclass
class Parameter(AST):
    target: _identifier
    type: _type


@dataclass
class RefParameter(AST):
    target: _identifier


@dataclass
class IfElse(AST):
    condition: _expression
    then: List[_statement]
    or_else: List[_statement]

# EXPRESSIONS
# ===========


@dataclass
class Expression(AST):
    value: _expression


@dataclass
class IfExpression(AST):
    condition: _expression
    then: _expression
    or_else: _expression


@dataclass
class Compare(AST):
    values: List[_expression]
    ops: List[str]


@dataclass
class UnaryOp(AST):
    x: _expression
    op: str


@dataclass
class BinaryOp(AST):
    x: _expression
    y: _expression
    op: str


class String(AST, str):
    ...


class Int(AST, int):
    ...


class Float(AST, float):
    ...


_expression = \
    Expression | \
    IfExpression | \
    Compare | \
    UnaryOp | \
    BinaryOp | \
    _identifier | \
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
