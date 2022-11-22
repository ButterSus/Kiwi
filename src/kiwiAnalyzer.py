from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, List, Tuple, Type, Iterator

# Custom libraries
# ----------------

from src.assets.kiwiTools import AST_Visitor
from src.assets.kiwiScope import ScopeSystem, Reference, reserve
from src.kiwiAST import AST
import src.assets.kiwiASO as kiwi
import src.assets.kiwiCommands as cmd
import built_in

if TYPE_CHECKING:
    from build import Constructor

NonRef = built_in.KiwiClass | built_in.KiwiConst | built_in.KiwiType | built_in.Function
Argument = Reference | NonRef


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

    def Module(self, node: kiwi.Module):
        node.body = self.visit(node.body)
        return node

    def Expression(self, node: kiwi.Expression):
        return self.visit(node.value)

    def Call(self, node: kiwi.Call):
        target: built_in.KiwiCallable = built_in.toNonReference(self.visit(node.target))
        method = target.Call
        return cmd.UseMethodWithCompiler(method, [self.visit(node.args)])

    # Variables
    # ---------

    def Name(self, node: kiwi.Name):
        return self.scope.ref(node.toAttr())

    def Attribute(self, node: kiwi.Attribute):
        return self.scope.ref(node.toAttr())

    # Constants
    # ---------

    def Number(self, node: kiwi.Number):
        return built_in.Number(node.value, self.constructor)

    def String(self, node: kiwi.String):
        return built_in.String(node.value, self.constructor)

    # Operators
    # ---------

    def BinaryOp(self, node: kiwi.BinaryOp):
        target = built_in.toNonReference(self.visit(node.x))
        method = target.__getattribute__(built_in.StdOps[node.op.value])
        return cmd.UseMethod(method, [self.visit(node.y)])

    # Annotations
    # -----------

    def AnnAssignment(self, node: kiwi.AnnAssignment):
        return (
            self.visit(kiwi.Annotation(node.targets, node.data_type, node.args)),
            self.visit(kiwi.Assignment(node.targets, node.value))
        )

    def Annotation(self, node: kiwi.Annotation):
        data_type: Type[built_in.KiwiClass] = self.visit(node.data_type).var
        result: List[cmd.UseMethod] = list()
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
            result.append(cmd.UseMethod(variable.Annotation, arguments))

        return tuple(result)

    # Assignments
    # -----------

    def Assignment(self, node: kiwi.Assignment):
        targets: List[Reference] = list(map(self.visit, node.targets))
        values: List[Argument] = list(map(self.visit, node.values))
        result: List[cmd.UseMethod] = list()
        assert len(values) == len(targets)
        for target, value in zip(targets, values):
            result.append(cmd.UseMethod(
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
        variable: built_in.Function = built_in.Function(target.toString(), self.constructor)
        self.scope.write(target, variable)

        return cmd.UseMethodWithCompiler(
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

        target = reserve(node.name.toAttr())
        variable: built_in.Namespace = built_in.Namespace(
            target.toString()[1:],
            self.constructor)
        self.scope.write(target, variable)

        return cmd.UseMethodWithCompiler(
            variable.Annotation, [body_private, body_public, body_default]
        )
