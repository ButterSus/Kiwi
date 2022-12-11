from __future__ import annotations

# Default libraries
# -----------------

from LangApi import *

# Custom libraries
# ----------------

from Kiwi.components.kiwiTools import AST_Visitor
from Kiwi.components.kiwiScope import ScopeSystem
from Kiwi.kiwiAST import AST
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
        return Construct(
            'Return',
            self.api.getThisScope(),
            [self.visit(node.value)]
        )

    # CONSTANT / TOKENS
    # =================

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

    def Name(self, node: kiwi.Name | kiwi.Attribute):
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

    Attribute = Name

    # ASSIGNMENTS
    # ===========

    def Annotation(self, node: kiwi.Annotation):
        for target in node.targets:
            assert not target.isGroup()
            self.api.visit(
                Construct(
                    'InitsType',
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
        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            target = self.visit(a)
            value = self.visit(b)
            if value in passed_targets:
                print('boom!')
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
                'Formalize',
                LangCode.IfElse(self.api),
                [
                    node.condition,
                    node.then,
                    node.or_else
                ]
            )
        )

    def FuncDef(self, node: kiwi.FuncDef):
        return self.api.visit(
            Construct(
                'Formalize',
                LangCode.Function(self.api),
                [
                    node.name.toAttr(),
                    node.body,
                    node.params,
                    node.returns
                ]
            )
        )

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        return self.api.visit(
            Construct(
                'Formalize',
                LangCode.Namespace(self.api),
                [
                    node.name.toAttr(),
                    node.blocks
                ]
            )
        )

    # PARAMS AND LAMBDAS
    # ==================

    def Parameter(self, node: kiwi.Parameter):
        result = list()
        for target in node.targets:
            assert not target.isGroup()
            self.api.visit(
                Construct(
                    'InitsType',
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
                'InitsType',
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
