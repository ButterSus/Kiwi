"""
This module represents the third step of compiler frontend.
It creates requests for API visitor, which can be used to generate code.
Also, it creates associations in memory for variables, functions and so on.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, List

# Custom libraries
# ----------------

from components.kiwiTools import AST_Visitor
from components.kiwiScope import ScopeSystem
import components.kiwiASO as kiwi


if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi


# Initialization of modules
# -------------------------

def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa
    _Kiwi.init(_compiler, _LangApi, _Kiwi)


class Analyzer(AST_Visitor):
    """
    This class represents the third step of compiler frontend.
    """
    scope: ScopeSystem

    # Parts of compiler
    # -----------------

    constructor: compiler.KiwiConstructor.Constructor
    builder: compiler.Builder
    tokenizer: compiler.Tokenizer
    ast: compiler.AST
    api: LangApi.api.API

    # General parameters
    # ------------------

    config: compiler.ConfigGeneral
    text: List[str]

    def __init__(
            self,
            constructor: compiler.KiwiConstructor.Constructor,
            builder: compiler.Builder,
            tokenizer: compiler.Tokenizer,
            ast: compiler.AST,
            api: LangApi.api.API,
            text: str
    ):
        # Parts of compiler
        # -----------------

        self.constructor = constructor
        self.builder = builder
        self.tokenizer = tokenizer
        self.ast = ast
        self.api = api

        # General parameters
        # ------------------

        self.config = builder.configGeneral
        self.text = text.splitlines()

        # Initialization
        # --------------

        api.analyzer = self
        self.scope = ScopeSystem(
            Kiwi.associations
        )

    def native(self, node: kiwi.AST) -> str:
        """
        This method is used to get native string from AST element.
        """
        result = list()
        if (line := node.start[0]) == node.end[0]:
            return self.text[line - 1][node.start[1]:node.end[1] + 1]
        result.append(self.text[node.start[0] - 1][node.start[1]:])
        for line in range(node.start[0], node.end[0] - 1):
            result.append(self.text[line])
        result.append(self.text[node.end[0] - 1][:node.end[1] + 1])
        return '\n'.join(result)

    # MODULE DECLARATION
    # ==================

    def Module(self, node: kiwi.Module):
        node.body = self.api.visit(
            LangApi.api.Construct(
                LangApi.api.ConstructMethod.Formalize,
                Kiwi.compound.module.Module,
                [node.body]
            )
        )

    # EXPRESSIONS
    # ===========

    def Expression(self, node: kiwi.Expression):
        return self.api.visit(
            LangApi.api.Construct(
                LangApi.api.ConstructMethod.Formalize,
                Kiwi.tokens.expression.Expression,
                [node.value],
                raw_args=True
            )
        )

    # Function calls
    # --------------

    def Call(self, node: kiwi.Call):
        return LangApi.api.Construct(
            LangApi.api.ConstructMethod.Call,
            self.visit(node.target),
            self.visit(node.args)
        )
    #
    # def Return(self, node: kiwi.Return):
    #     return self.api.visit(
    #         Construct(
    #             'Return',
    #             self.api.getThisScope(),
    #             [self.visit(node.value)],
    #             raw_args=True
    #         )
    #     )

    # CONSTANT / TOKENS
    # =================

    def Number(self, node: kiwi.Number):
        return self.api.visit(
            LangApi.api.Construct(
                LangApi.api.ConstructMethod.Formalize,
                Kiwi.tokens.number.IntegerFormat,
                [node.value]
            )
        )

    def String(self, node: kiwi.String):
        prefix = node.getPrefix()
        if not prefix:
            return LangApi.api.Construct(
                LangApi.api.ConstructMethod.Formalize,
                Kiwi.tokens.string.StringFormat,
                [node.getString()]
            )
        match prefix:
            case "f":
                assert False
        assert False

    # def Token(self, node: kiwi.Token):
    #     match node.value:
    #         case 'none':
    #             return Construct(
    #                 'Formalize',
    #                 LangCode.AbsoluteNone,
    #                 []
    #             )
    #     self.visitAST(node)
    #     return node
    #
    # @staticmethod
    # def Number(node: kiwi.Number):
    #     return Construct(
    #         'Formalize',
    #         LangCode.Number,
    #         [node.value]
    #     )
    #

    # VARIABLE NOTATIONS
    # ==================

    def VariableReference(self, node: kiwi.Name | kiwi.Attribute):
        if not self._no_references:
            try:
                return self.scope.get(node.toAttr())
            except AssertionError:
                pass
        return LangApi.api.Construct(
            LangApi.api.ConstructMethod.Formalize,
            Kiwi.tokens.undefined.Undefined,
            [node.toAttr()]
        )

    Attribute = Name = VariableReference

    # ASSIGNMENTS
    # ===========

    def Annotation(self, node: kiwi.Annotation):
        for target in node.targets:
            assert not target.isGroup
            parent: LangApi.abstract.Variable = self.api.visit(
                LangApi.api.Construct(
                    LangApi.api.ConstructMethod.GetChild,
                    self.visit(node.data_type),
                    []
                )
            )
            if parent.isNative:
                args = node.args
            else:
                args = self.visit(node.args)
            self.api.visit(
                LangApi.api.Construct(
                    LangApi.api.ConstructMethod.Annotation,
                    self.visit(target),
                    [parent, *args]
                )
            )

    # _augAssignOps = {
    #     '+=': 'IAdd',
    #     '-=': 'ISub',
    #     '*=': 'IMul',
    #     '/=': 'IDiv',
    #     '%=': 'IMod'
    # }
    #
    # def AugAssignment(self, node: kiwi.AugAssignment):
    #     result = list()
    #
    #     assert len(node.targets) == len(node.values)
    #     for a, b in zip(node.targets, node.values):
    #         target = self.visit(a)
    #         value = self.visit(b)
    #         result.append(
    #             Construct(
    #                 self._augAssignOps[node.op.value],
    #                 target,
    #                 [value]
    #             )
    #         )
    #     return tuple(result)

    def Assignment(self, node: kiwi.Assignment):
        result = list()
        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            target = self.visit(a)
            value = self.visit(b)
            result.append(
                LangApi.api.Construct(
                    LangApi.api.ConstructMethod.AssignOperation,
                    target,
                    [value]
                )
            )
        return tuple(result)

    # def AnnAssignment(self, node: kiwi.AnnAssignment):
    #     self.visit(
    #         kiwi.Annotation(
    #             ..., ..., node.targets, node.data_type, node.args))
    #     return self.visit(
    #         kiwi.Assignment(
    #             ..., ..., node.targets, node.values))

    # SPACE DECLARATIONS
    # ==================

    # def IfElse(self, node: kiwi.IfElse):
    #     return self.api.visit(
    #         Construct(
    #             'InitsType',
    #             LangCode.IfElse(self.api),
    #             [
    #                 node.condition,
    #                 node.then,
    #                 node.or_else
    #             ]
    #         )
    #     )
    #
    # def While(self, node: kiwi.While):
    #     result = self.api.visit(
    #         Construct(
    #             'InitsType',
    #             LangCode.While(self.api),
    #             [
    #                 node.condition,
    #                 node.body
    #             ]
    #         )
    #     )
    #     return result

    # def FuncDef(self, node: kiwi.FuncDef):
    #     result = self.api.visit(
    #             Construct(
    #                 'AnnotationDeclare',
    #                 self.visit(node.name),
    #                 [
    #                     LangCode.Function(self.api),
    #                     node.body,
    #                     node.params,
    #                     node.returns
    #                 ]
    #             )
    #         )
    #     return result
    #
    # def NamespaceDef(self, node: kiwi.NamespaceDef):
    #     result = self.api.visit(
    #         Construct(
    #             'InitsType',
    #             LangCode.Namespace(self.api),
    #             [
    #                 node.name.toAttr(),
    #                 node.blocks
    #             ]
    #         )
    #     )
    #     return result

    # PARAMS AND LAMBDAS
    # ==================

    # def Parameter(self, node: kiwi.Parameter):
    #     result = list()
    #     for target in node.targets:
    #         assert not target.isGroup()
    #         self.api.visit(
    #             Construct(
    #                 'AnnotationDeclare',
    #                 self.visit(target, no_references=True),
    #                 [
    #                     Construct(
    #                         'GetChild',
    #                         self.visit(node.data_type),
    #                         []
    #                     ),
    #                     *self.api.visit(
    #                         self.visit(node.args)
    #                     )
    #                 ]
    #             )
    #         )
    #         result.append(self.visit(target))
    #     return tuple(result)
    #
    # def RefParameter(self, node: kiwi.RefParameter):
    #     assert not node.target.isGroup()
    #     return self.api.analyzer.scope.get(node.target.toAttr())
    #
    # def ReturnParameter(self, node: kiwi.ReturnParameter):
    #     target = kiwi.Name(..., ..., self.api.getReturnEx().toName())
    #     self.api.visit(
    #         Construct(
    #             'AnnotationDeclare',
    #             self.visit(target),
    #             [
    #                 Construct(
    #                     'GetChild',
    #                     self.visit(node.data_type),
    #                     []
    #                 ),
    #                 *self.api.visit(
    #                     self.visit(node.args)
    #                 )
    #             ]
    #         )
    #     )
    #     return self.visit(target)
    #
    # def ReturnRefParameter(self, node: kiwi.ReturnRefParameter):
    #     return self.api.analyzer.scope.get(node.target.toAttr())

    # COMPARISONS
    # ===========

    # def Disjunctions(self, node: kiwi.Disjunctions):
    #     return self.api.visit(
    #         Construct(
    #             'Formalize',
    #             LangCode.Disjunctions(self.api),
    #             [self.visit(node.values)]
    #         )
    #     )
    #
    # def Conjunctions(self, node: kiwi.Conjunctions):
    #     return self.api.visit(
    #         Construct(
    #             'Formalize',
    #             LangCode.Conjunctions(self.api),
    #             [self.visit(node.values)]
    #         )
    #     )
    #
    # def Comparisons(self, node: kiwi.Comparisons):
    #     return self.api.visit(
    #         Construct(
    #             'Formalize',
    #             LangCode.Comparisons(self.api),
    #             [self.visit(node.values), self.visit(node.ops)]
    #         )
    #     )

    # OPERATORS
    # =========

    def UnaryOp(self, node: kiwi.UnaryOp):
        x = self.visit(node.x)
        match str(node.op):
            case "+":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.PlusOperation,
                    x,
                    []
                )
            case "-":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.MinusOperation,
                    x,
                    []
                )

    def BinaryOp(self, node: kiwi.BinaryOp):
        x, y = self.visit(node.x), self.visit(node.y)
        match str(node.op):
            case "+":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.AddOperation,
                    x,
                    [y]
                )
            case "-":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.SubOperation,
                    x,
                    [y]
                )
            case "*":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.MulOperation,
                    x,
                    [y]
                )
            case "/":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.DivOperation,
                    x,
                    [y]
                )
            case "%":
                return LangApi.api.Construct(
                    LangApi.api.ConstructMethod.ModOperation,
                    x,
                    [y]
                )