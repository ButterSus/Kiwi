from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING

# Custom libraries
# ----------------

from src.assets.kiwiTools import AST_Visitor
from src.assets.kiwiScope import ScopeSystem, Reference
import src.assets.kiwiASO as kiwi
import std
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
