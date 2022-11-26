from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING
from LangApi import Construct, API

# Custom libraries
# ----------------

from header.components.kiwiTools import AST_Visitor
from header.components.kiwiScope import ScopeSystem
from header.kiwiAST import AST
import LangCode
import header.components.kiwiASO as kiwi

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
        LangCode.built_init(API)
        self.api = API(self)
        self.constructor = constructor
        self.visit(ast.module)

    # EXPRESSIONS
    # ===========

    def Expression(self, node: kiwi.Expression):
        return Construct(
            LangCode.Expression.Annotation,
            LangCode.Expression,
            [self.visit(node.value)]
        )

    # CONSTANT / TOKENS
    # =================

    def Number(self, node: kiwi.Number):
        return Construct(
            LangCode.Number.Annotation,
            LangCode.Number,
            [node.value]
        )

    # VARIABLE NOTATIONS
    # ==================

    def Name(self, node: kiwi.Name | kiwi.Attribute):
        return self.scope.get(node.toAttr())

    Attribute = Name

    # ASSIGNMENTS
    # ===========

    def Annotation(self, node: kiwi.Annotation):
        return
