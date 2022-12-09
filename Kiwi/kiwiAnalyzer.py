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
    from build import Constructor


class Analyzer(AST_Visitor):
    """
    The main task of this class is
    - connect variables to their memory locations
    """

    scope: ScopeSystem
    ast: AST
    api: API
    constructor: Constructor

    def __init__(self, ast: AST, libScope: dict, constructor: Constructor):
        self.ast = ast
        self.scope = ScopeSystem(libScope)
        self.constructor = constructor
        LangCode.built_annotationsInit(API)
        self.api = API(self)
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

    def Call(self, node: kiwi.Call):
        return Construct(
            'Call',
            self.visit(node.target),
            self.visit(node.args)
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
        try:
            return self.scope.get(node.toAttr())
        except AssertionError:
            return Construct(
                'Declare',
                LangCode.Undefined,
                [node.toAttr()]
            )

    Attribute = Name

    # ASSIGNMENTS
    # ===========

    def Annotation(self, node: kiwi.Annotation):
        for target in node.targets:
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

    def Assignment(self, node: kiwi.Assignment):
        result = list()

        passed_targets = list()
        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            target = self.visit(a)
            value = self.visit(b)
            if value in passed_targets:
                temp = value.__class__(self.api).InitsType(value)
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
                        ..., ..., node.targets, node.values)
               )

    # SPACE DECLARATIONS
    # ==================

    def FuncDef(self, node: kiwi.FuncDef):
        return self.api.visit(
            Construct(
                'Declare',
                LangCode.Function(self.api),
                [node.name.toAttr(),
                 node.body]
            )
        )

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        return self.api.visit(
            Construct(
                'Declare',
                LangCode.Namespace,
                [node.name.toAttr(),
                 node.body_private, node.body_public, node.body_default]
            )
        )

    # OPERATORS
    # =========

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
