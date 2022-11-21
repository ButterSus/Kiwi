from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING

# Custom libraries
# ----------------

from src.assets.kiwiTools import AST_Visitor
from src.assets.kiwiScope import ScopeSystem, Reference
import src.assets.kiwiASO as kiwi
import src.assets.kiwiCommands as cmd
from src.kiwiAST import AST

if TYPE_CHECKING:
    from build import Constructor


class Compiler(AST_Visitor):
    """
    The main task of this class is
    - Compile: statements -> functions -> modules -> project
    """

    scope: ScopeSystem
    ast: AST
    constructor: Constructor

    def __init__(self, ast: AST, scope: ScopeSystem, constructor: Constructor):
        self.ast = ast
        self.scope = scope
        self.constructor = constructor
        self.visit(ast.module)

    # Compiling AST
    # -------------

    def Module(self, node: kiwi.Module):
        node.body = self.visit(node.body)
        return node

    def CallMethod(self, node: cmd.CallMethod):
        print(node)
        arguments = map(self.visit, node.arguments)
        return node.method(*arguments)

    def CallMethodWithCompiler(self, node: cmd.CallMethodWithCompiler):
        arguments = node.arguments
        return node.method(self, *arguments)
