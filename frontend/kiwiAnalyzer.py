"""
This module represents the third step of compiler frontend.
It creates requests for API visitor, which can be used to generate code.
Also, it creates associations in memory for variables, functions and so on.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, List, Dict

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

    Analyzer._augAssignOps = {
        '+=': LangApi.abstract.ConstructMethod.AugAddOperation,
        '-=': LangApi.abstract.ConstructMethod.AugSubOperation,
        '*=': LangApi.abstract.ConstructMethod.AugMulOperation,
        '/=': LangApi.abstract.ConstructMethod.AugDivOperation,
        '%=': LangApi.abstract.ConstructMethod.AugModOperation,
    }

    Analyzer._unaryOps = {
        "+": LangApi.abstract.ConstructMethod.PlusOperation,
        "-": LangApi.abstract.ConstructMethod.MinusOperation,
    }

    Analyzer._binaryOps = {
        "+": LangApi.abstract.ConstructMethod.AddOperation,
        "-": LangApi.abstract.ConstructMethod.SubOperation,
        "*": LangApi.abstract.ConstructMethod.MulOperation,
        "/": LangApi.abstract.ConstructMethod.DivOperation,
        "%": LangApi.abstract.ConstructMethod.ModOperation,
    }


class IsAttribute(Exception):
    ...


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
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.module.Module,
                [node.body]
            )
        )

    # EXPRESSIONS
    # ===========

    def Range(self, node: kiwi.Range):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.range.Range,
                [node.expr_start, node.expr_end],
                raw_args=True
            )
        )

    def Expression(self, node: kiwi.Expression):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.expression.Expression,
                [node.value],
                raw_args=True
            )
        )

    # Function calls
    # --------------

    def Call(self, node: kiwi.Call):
        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Call,
            self.visit(node.target),
            self.visit(node.args)
        )

    def Return(self, node: kiwi.Return):
        i = 0
        while i < len(self.api.scopeFolder):
            function = self.api.getThisScope(i)
            if isinstance(function, Kiwi.compound.function.Function):
                break
            i += 1
        else:
            assert False
        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Return,
            function,
            [self.visit(node.value)]
        )

    # CONSTANT / TOKENS
    # =================

    def Number(self, node: kiwi.Number):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.number.IntegerFormat,
                [node.value]
            )
        )

    def String(self, node: kiwi.String):
        prefix = node.getPrefix()
        if not prefix:
            return LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.string.StringFormat,
                [node.getString(), False]
            )
        match prefix:
            case "f":
                return LangApi.abstract.Construct(
                    LangApi.abstract.ConstructMethod.Formalize,
                    Kiwi.tokens.string.StringFormat(self.api),
                    [node.getString(), True]
                )
        assert False

    # VARIABLE NOTATIONS
    # ==================

    def VariableReference(self, node: kiwi.Name | kiwi.Attribute):
        if self._checkAttribute and self.scope.localScope.isAttribute(node.toAttr()):
            raise IsAttribute(node.toAttr())
        if not self._no_references:
            try:
                return self.scope.get(node.toAttr())
            except AssertionError:
                pass
        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Formalize,
            Kiwi.tokens.undefined.Undefined,
            [node.toAttr()]
        )

    Attribute = Name = VariableReference

    # ASSIGNMENTS
    # ===========

    def Annotation(self, node: kiwi.Annotation):
        parent: LangApi.abstract.Variable = self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.GetChild,
                self.visit(node.data_type),
                []
            )
        )
        for target in node.targets:
            assert not target.isGroup
            if parent.isNative:
                args = node.args
            else:
                args = self.visit(node.args)
            self.api.visit(
                LangApi.abstract.Construct(
                    LangApi.abstract.ConstructMethod.Annotation,
                    self.visit(target),
                    [parent, *args]
                )
            )

    _augAssignOps: Dict[str, LangApi.abstract.ConstructMethod]

    def AugAssignment(self, node: kiwi.AugAssignment):
        result = list()
        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            result.append(
                LangApi.abstract.Construct(
                    self._augAssignOps[node.op.value],
                    self.visit(a),
                    [self.visit(b)]
                )
            )
        return tuple(result)

    _checkAttribute = False

    def Assignment(self, node: kiwi.Assignment):
        result = list()
        assert len(node.targets) == len(node.values)
        for a, b in zip(node.targets, node.values):
            self._checkAttribute = True
            try:
                target = self.visit(a)
            except IsAttribute as attribute:
                target = attribute.args[0]
                value = self.visit(b)
                result.append(
                    self.scope.write(target, value)
                )
            else:
                self._checkAttribute = False
                value = self.visit(b)
                result.append(
                    LangApi.abstract.Construct(
                        LangApi.abstract.ConstructMethod.AssignOperation,
                        target,
                        [value]
                    )
                )
        return tuple(result)

    def AnnAssignment(self, node: kiwi.AnnAssignment):
        parent: LangApi.abstract.Variable = self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.GetChild,
                self.visit(node.data_type),
                []
            )
        )
        if isinstance(parent, LangApi.abstract.Const):
            result = list()
            assert len(node.targets) == len(node.values)
            for a, b in zip(node.targets, node.values):
                target = self.visit(a)
                value = self.visit(b)
                result.append(
                    self.api.visit(
                        LangApi.abstract.Construct(
                            LangApi.abstract.ConstructMethod.AnnAssign,
                            target,
                            [parent, value]
                        )
                    )
                )
            return tuple(result)
        self.visit(
            kiwi.Annotation(..., ..., node.targets, node.data_type, node.args)
        )
        return self.visit(
            kiwi.Assignment(..., ..., node.targets, node.values)
        )

    # SPACE DECLARATIONS
    # ==================

    def IfElse(self, node: kiwi.IfElse):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.ifelse.If(self.api),
                [
                    node.condition,
                    node.then,
                    node.or_else,
                ],
                raw_args=True
            )
        )

    def ForClassic(self, node: kiwi.ForClassic):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.forloop.ForClassic(self.api),
                [
                    node.init,
                    node.condition,
                    node.increment,
                    node.body,
                ],
                raw_args=True
            )
        )

    def ForIterator(self, node: kiwi.ForIterator):
        self.visit(
            kiwi.Annotation(
                ..., ...,
                node.targets,
                node.parent,
                node.args,
            )
        )
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.forloop.ForIterator(self.api),
                [
                    self.visit(node.targets[0]),
                    node.iterator,
                    node.body,
                ],
                raw_args=True
            )
        )

    def While(self, node: kiwi.While):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.whiledo.While(self.api),
                [
                    node.condition,
                    node.body
                ],
                raw_args=True
            )
        )

    def FuncDef(self, node: kiwi.FuncDef):
        result = self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.function.Function,
                [
                    node.name.toAttr(),
                    node.body,
                    node.params,
                    node.returns,
                ],
                raw_args=True
            )
        )
        return result

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        result = self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.compound.namespace.Namespace,
                [
                    node.name.toAttr(),
                    node.blocks
                ],
                raw_args=True
            )
        )
        return result

    # PARAMS AND LAMBDAS
    # ==================

    def Parameter(self, node: kiwi.Parameter):
        result = list()
        for target in node.targets:
            assert not target.isGroup
            self.api.visit(
                LangApi.abstract.Construct(
                    LangApi.abstract.ConstructMethod.Annotation,
                    self.visit(target, no_references=True),
                    [
                        LangApi.abstract.Construct(
                            LangApi.abstract.ConstructMethod.GetChild,
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
        assert not node.target.isGroup
        return self.api.analyzer.scope.get(node.target.toAttr())

    def ReturnParameter(self, node: kiwi.ReturnParameter):
        return self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.GetChild,
                self.visit(node.data_type),
                []
            )
        )

    def ReturnRefParameter(self, node: kiwi.ReturnRefParameter):
        return self.api.analyzer.scope.get(node.target.toAttr())

    # COMPARISONS
    # ===========

    def Disjunctions(self, node: kiwi.Disjunctions):
        return LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.boolean.Disjunctions(self.api),
                [self.visit(node.values)]
            )

    def Conjunctions(self, node: kiwi.Conjunctions):
        return LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.boolean.Conjunctions(self.api),
                [self.visit(node.values)]
            )

    def Comparisons(self, node: kiwi.Comparisons):
        return LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.Formalize,
                Kiwi.tokens.boolean.Comparisons(self.api),
                [self.visit(node.values), self.visit(node.ops)]
            )

    # OPERATORS
    # =========

    _unaryOps: Dict[str, LangApi.abstract.ConstructMethod]

    def UnaryOp(self, node: kiwi.UnaryOp):
        x = self.visit(node.x)
        return LangApi.abstract.Construct(
            self._unaryOps[str(node.op)],
            x,
            []
        )

    _binaryOps: Dict[str, LangApi.abstract.ConstructMethod]

    def BinaryOp(self, node: kiwi.BinaryOp):
        x, y = self.visit(node.x), self.visit(node.y)
        return LangApi.abstract.Construct(
            self._binaryOps[str(node.op)],
            x,
            [y]
        )
