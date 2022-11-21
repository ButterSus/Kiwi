from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, List, Tuple, Type, Iterator

# Custom libraries
# ----------------

from src.assets.kiwiTools import AST_Visitor
from src.assets.kiwiScope import ScopeSystem, Reference
from src.kiwiAST import AST
import src.assets.kiwiASO as kiwi
import src.assets.kiwiCommands as cmd
import std as std

if TYPE_CHECKING:
    from build import Constructor

Argument = Reference | std.Constant


class Analyzer(AST_Visitor):
    """
    The main task of this class is
    - connect variables to their memory locations
    """

    scope: ScopeSystem
    ast: AST
    constructor: Constructor

    def __init__(self, ast: AST, libScope: dict, constructor: Constructor):
        self.ast = ast
        self.scope = ScopeSystem(libScope)
        self.constructor = constructor
        self.visit(ast.module)

    # AST analysis
    # ------------

    def Expression(self, node: kiwi.Expression):
        return self.visit(node.value)

    # Variables
    # ---------

    def Name(self, node: kiwi.Name):
        return self.scope.ref(node.toAttr())

    def Attribute(self, node: kiwi.Attribute):
        return self.scope.ref(node.toAttr())

    # Constants
    # ---------

    def Number(self, node: kiwi.Number):
        return std.Constant(int(node.value))

    # Annotations
    # -----------

    def AnnAssignment(self, node: kiwi.AnnAssignment):
        return (
            self.visit(kiwi.Annotation(node.targets, node.data_type, node.args)),
            self.visit(kiwi.Assignment(node.targets, node.value))
        )

    def Annotation(self, node: kiwi.Annotation):
        data_type: Type[std.KiwiType] = self.visit(node.data_type).var
        result: List[cmd.CallMethod] = list()
        for target in node.targets:
            # Target should be expression
            # ---------------------------

            assert isinstance(target, kiwi.Expression)
            target = target.value

            # Target should be name or attribute
            # ----------------------------------

            assert isinstance(target, kiwi.Name) or isinstance(target, kiwi.Attribute)
            target = target.toAttr()

            # Forming command request
            # -----------------------

            variable = data_type(target.toString(), self.constructor)
            self.scope.write(target, variable)
            arguments = self.visit(node.args)
            result.append(cmd.CallMethod(variable.Annotation, arguments))

        return tuple(result)

    # Assignments
    # -----------

    def Assignment(self, node: kiwi.Assignment):
        targets: List[Reference] = list(map(self.visit, node.targets))
        values: List[Argument] = list(map(self.visit, node.values))
        result: List[cmd.CallMethod] = list()
        assert len(values) == len(targets)
        for target, value in zip(targets, values):
            result.append(cmd.CallMethod(
                target.var.Assignment, [value]
            ))
        return tuple(result)

    # Compound declaration
    # --------------------

    def FuncDef(self, node: kiwi.FuncDef):
        # Visiting body
        # -------------

        self.scope.newLocalSpace()
        body = self.visit(node.body)
        self.scope.leaveSpace()

        # Forming command request
        # -----------------------

        target = node.name.toAttr()
        variable = std.Function(target.toString(), self.constructor)
        self.scope.write(target, variable)

        return cmd.CallMethod(
            variable.Annotation, [body]
        )

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        # Visiting body
        # -------------

        self.scope.newNamedSpace(node.name)
        self.scope.enablePrivate()
        body_private = self.visit(node.body_private)
        self.scope.disablePrivate()
        body_public = self.visit(node.body_public)
        if self.constructor.configGeneral['default_scope'] == 'private':
            self.scope.enablePrivate()
        else:
            assert self.constructor.configGeneral['default_scope'] == 'public'
        body_default = self.visit(node.body_default)
        self.scope.leaveSpace()

        # Forming command request
        # -----------------------

        target = node.name.toAttr()
        variable = std.Namespace(target.toString(), self.constructor)
        self.scope.write(target, variable)

        return cmd.CallMethod(
            variable.Annotation, [body_private, body_public, body_default]
        )
