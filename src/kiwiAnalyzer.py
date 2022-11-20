from __future__ import annotations

# Default libraries
# -----------------

from typing import List

# Custom libraries
# ----------------

from src.assets.kiwiTools import AST_Visitor
from src.assets.kiwiScope import ScopeSystem
import src.assets.kiwiASO as kiwi
import std
from src.kiwiAST import AST


class Analyzer(AST_Visitor):
    """
    The main task of this class is
    - connect variables to their memory locations
    """

    scope: ScopeSystem
    ast: AST

    def __init__(self, ast: AST, libScope: dict):
        self.ast = ast
        self.scope = ScopeSystem(libScope)
        self.visit(ast.module)

    # ANNOTATION STATEMENTS
    # =====================

    def Annotation(self, node: kiwi.Annotation):
        data_type = self.visit(node.data_type)
        for target in node.targets:
            self.scope.write(target.value.dump(), data_type)
        return

    def Expression(self, node: kiwi.Expression):
        return self.visit(node.value)

    def Name(self, node: kiwi.Name):
        return self.scope.ref(node.value)

    def Attribute(self, node: kiwi.Attribute):
        return self.scope.ref(node.dump())

    # SCOPE STATEMENTS
    # ================

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        self.scope.write(node.name)
        name = node.name
        self.scope.newNamedSpace(str(node.name))
        public = self.visit(node.body_public)
        default = self.visit(node.body_default)
        self.scope.enablePrivate()
        private = self.visit(node.body_private)
        self.scope.leaveSpace()
        return kiwi.NamespaceDef(name, private, public, default)

    def FuncDef(self, node: kiwi.FuncDef):
        self.scope.newLocalSpace()
        name = node.name
        parameters = self.visit(node.params)
        default = self.visit(node.default)
        returns = self.visit(node.returns)
        promiser = self.visit(node.promiser)
        body = self.visit(node.body)
        self.scope.leaveSpace()

        result = kiwi.FuncDef(name, parameters, default, returns, promiser, body)
        self.scope.write(name, result)
        return result

    def Parameter(self, node: kiwi.Parameter):
        data_type: std.KiwiType = self.visit(node.data_type)
        targets: List[kiwi.Reference] = list()
        for target in node.target:
            target = target.value.dump()
            self.scope.write(target, data_type)
            targets.append(self.scope.ref(target))
        return kiwi.Parameter(targets, data_type)

    def IfElse(self, node: kiwi.IfElse):
        self.scope.newLocalSpace()
        condition = self.visit(node.condition)
        then = self.visit(node.then)
        or_else = self.visit(node.or_else)
        self.scope.leaveSpace()
        return kiwi.IfElse(condition, then, or_else)

    def While(self, node: kiwi.While):
        self.scope.newLocalSpace()
        condition = self.visit(node.condition)
        body = self.visit(node.body)
        self.scope.leaveSpace()
        return kiwi.While(condition, body)
