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

This module represents the third step of compiler frontend.
It creates requests for API visitor, which can be used to generate code.
Also, it creates associations in memory for variables, functions and so on.
"""

from __future__ import annotations

# Default libraries
# -----------------

from LangApi import *

# Custom libraries
# ----------------

from Kiwi.components.kiwiTools import AST_Visitor
from Kiwi.components.kiwiScope import ScopeSystem
from Kiwi.kiwiParser import AST
import LangCode
import Kiwi.components.kiwiASO as kiwi

if TYPE_CHECKING:
    from build import ConfigGeneral


class Analyzer(AST_Visitor):
    scope: ScopeSystem
    ast: AST
    api: API
    config: ConfigGeneral

    def __init__(self, ast: AST, libScope: dict, config: ConfigGeneral):
        self.ast = ast
        self.scope = ScopeSystem(libScope)
        self.config = config
        LangCode.built_annotationsInit(API)
        self.api = API(self, LangCode)
        LangCode.built_codeInit(self.api)
        self.visit(ast.module)

    # MODULE DECLARATION
    # ==================

    def Module(self, node: kiwi.Module):
        node.body = self.visit(node.body)

    # EXPRESSIONS
    # ===========

    def Expression(self, node: kiwi.Expression):
        return Construct(
            'Formalize',
            LangCode.Expression,
            [self.visit(node.value)]
        )

    def NotFullExpression(self, node: kiwi.NotFullExpression):
        return Construct(
            'Formalize',
            LangCode.NotFullExpression,
            [self.visit(node.value)]
        )

    # Function calls
    # --------------

    def Call(self, node: kiwi.Call):
        return Construct(
            'Call',
            self.visit(node.target),
            self.visit(node.args)
        )

    def Return(self, node: kiwi.Return):
        return self.api.visit(
            Construct(
                'Return',
                self.api.getThisScope(),
                [self.visit(node.value)],
                raw_args=True
            )
        )

    # CONSTANT / TOKENS
    # =================

    def Token(self, node: kiwi.Token):
        match node.value:
            case 'none':
                return Construct(
                    'Formalize',
                    LangCode.AbsoluteNone,
                    []
                )
        self.visitAST(node)
        return node

    @staticmethod
    def Number(node: kiwi.Number):
        return Construct(
            'Formalize',
            LangCode.Number,
            [node.value]
        )

    @staticmethod
    def String(node: kiwi.String):
        prefix = node.getPrefix()
        if not prefix:
            return Construct(
                'Formalize',
                LangCode.String,
                [node]
            )
        match prefix:
            case "f":
                return Construct(
                    'Formalize',
                    LangCode.FString,
                    [node]
                )
        assert False

    # VARIABLE NOTATIONS
    # ==================

    def VariableReference(self, node: kiwi.Name | kiwi.Attribute):
        if not self._no_references:
            try:
                return self.scope.get(node.toAttr())
            except AssertionError:
                pass
        return Construct(
            'Formalize',
            LangCode.Undefined,
            [node.toAttr()]
        )

    Attribute = Name = VariableReference

    # ASSIGNMENTS
    # ===========

    def Annotation(self, node: kiwi.Annotation):
        for target in node.targets:
            assert not target.isGroup()
            self.api.visit(
                Construct(
                    'AnnotationDeclare',
                    self.visit(target),
                    [Construct(
                        'GetChild',
                        self.visit(node.data_type),
                        []
                    ), *self.visit(node.args)]
                )
            )

    _augAssignOps = {
        '+=': 'IAdd',
        '-=': 'ISub',
        '*=': 'IMul',
        '/=': 'IDiv',
        '%=': 'IMod'
    }

    def AugAssignment(self, node: kiwi.AugAssignment):
        result = list()

        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            target = self.visit(a)
            value = self.visit(b)
            result.append(
                Construct(
                    self._augAssignOps[node.op.value],
                    target,
                    [value]
                )
            )
        return tuple(result)

    def Assignment(self, node: kiwi.Assignment):
        result = list()

        passed_targets = list()
        associations = list()
        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            target = self.visit(a)
            value = self.visit(b)
            if value in passed_targets:
                associations.append(b)
            result.append(
                Construct(
                    'Assign',
                    target,
                    [value]
                )
            )
            passed_targets.append(target)
        return tuple(result)

    def AnnAssignment(self, node: kiwi.AnnAssignment):
        self.visit(
            kiwi.Annotation(
                ..., ..., node.targets, node.data_type, node.args))
        return self.visit(
            kiwi.Assignment(
                ..., ..., node.targets, node.values))

    # SPACE DECLARATIONS
    # ==================

    def IfElse(self, node: kiwi.IfElse):
        return self.api.visit(
            Construct(
                'InitsType',
                LangCode.IfElse(self.api),
                [
                    node.condition,
                    node.then,
                    node.or_else
                ]
            )
        )

    def While(self, node: kiwi.While):
        result = self.api.visit(
            Construct(
                'InitsType',
                LangCode.While(self.api),
                [
                    node.condition,
                    node.body
                ]
            )
        )
        return result

    def FuncDef(self, node: kiwi.FuncDef):
        result = self.api.visit(
                Construct(
                    'AnnotationDeclare',
                    self.visit(node.name),
                    [
                        LangCode.Function(self.api),
                        node.body,
                        node.params,
                        node.returns
                    ]
                )
            )
        return result

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        result = self.api.visit(
            Construct(
                'InitsType',
                LangCode.Namespace(self.api),
                [
                    node.name.toAttr(),
                    node.blocks
                ]
            )
        )
        return result

    # PARAMS AND LAMBDAS
    # ==================

    def Parameter(self, node: kiwi.Parameter):
        result = list()
        for target in node.targets:
            assert not target.isGroup()
            self.api.visit(
                Construct(
                    'AnnotationDeclare',
                    self.visit(target, no_references=True),
                    [
                        Construct(
                            'GetChild',
                            self.visit(node.data_type),
                            []
                        ),
                        *self.api.visit(
                            self.visit(node.args)
                        )
                    ]
                )
            )
            result.append(self.visit(target))
        return tuple(result)

    def RefParameter(self, node: kiwi.RefParameter):
        assert not node.target.isGroup()
        return self.api.analyzer.scope.get(node.target.toAttr())

    def ReturnParameter(self, node: kiwi.ReturnParameter):
        target = kiwi.Name(..., ..., self.api.getReturnEx().toName())
        self.api.visit(
            Construct(
                'AnnotationDeclare',
                self.visit(target),
                [
                    Construct(
                        'GetChild',
                        self.visit(node.data_type),
                        []
                    ),
                    *self.api.visit(
                        self.visit(node.args)
                    )
                ]
            )
        )
        return self.visit(target)

    def ReturnRefParameter(self, node: kiwi.ReturnRefParameter):
        return self.api.analyzer.scope.get(node.target.toAttr())

    # COMPARISONS
    # ===========

    def Disjunctions(self, node: kiwi.Disjunctions):
        return self.api.visit(
            Construct(
                'Formalize',
                LangCode.Disjunctions(self.api),
                [self.visit(node.values)]
            )
        )

    def Conjunctions(self, node: kiwi.Conjunctions):
        return self.api.visit(
            Construct(
                'Formalize',
                LangCode.Conjunctions(self.api),
                [self.visit(node.values)]
            )
        )

    def Comparisons(self, node: kiwi.Comparisons):
        return self.api.visit(
            Construct(
                'Formalize',
                LangCode.Comparisons(self.api),
                [self.visit(node.values), self.visit(node.ops)]
            )
        )

    # OPERATORS
    # =========

    def UnaryOp(self, node: kiwi.UnaryOp):
        x = self.visit(node.x)
        match str(node.op):
            case "+":
                x: SupportPlus
                return Construct(
                    'Plus',
                    x,
                    []
                )
            case "-":
                x: SupportMinus
                return Construct(
                    'Minus',
                    x,
                    []
                )

    def BinaryOp(self, node: kiwi.BinaryOp):
        x, y = self.visit(node.x), self.visit(node.y)
        match str(node.op):
            case "+":
                x: SupportAdd
                return Construct(
                    'Add',
                    x,
                    [y]
                )
            case "-":
                x: SupportSub
                return Construct(
                    'Sub',
                    x,
                    [y]
                )
            case "*":
                x: SupportMul
                return Construct(
                    'Mul',
                    x,
                    [y]
                )
            case "/":
                x: SupportDiv
                return Construct(
                    'Div',
                    x,
                    [y]
                )
            case "%":
                x: SupportMod
                return Construct(
                    'Mod',
                    x,
                    [y]
                )
