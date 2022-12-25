from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Callable, List, Optional

# Custom libraries
# ----------------

import LangApi
from components.kiwiScope import Attr
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


# Content of file
# ---------------


class If(LangApi.abstract.Block):
    attr: Attr
    if_attr: Attr
    else_attr: Attr
    predicate_attr: Attr
    check_var: Optional[Kiwi.scoreboard.score.Score]

    then_local: int
    or_else_local: int

    def Formalize(self,
                  condition: kiwi.expression,
                  then: List[kiwi.statement],
                  or_else: List[kiwi.statement]):
        condition = self.analyzer.visit(condition)

        # Prefix initialization
        # ---------------------

        self.if_attr = self.api.prefix.FileIf()
        self.else_attr = self.api.prefix.FileElse()
        self.predicate_attr = self.api.prefix.FilePredicate()

        # Body analyzing
        # --------------

        self.name = self.if_attr.toName()
        self.api.enterCodeScope(self, codeKey='if')
        self.then_local = self.analyzer.scope.useLocalSpace(hideMode=True)
        then = self.analyzer.visit(then)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        self.name = self.else_attr.toName()
        self.api.enterCodeScope(self, codeKey='else')
        self.or_else_local = self.analyzer.scope.useLocalSpace(hideMode=True)
        or_else = self.analyzer.visit(or_else)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [condition, then, or_else],
            raw_args=True
        )

    def Reference(self,
                  condition: LangApi.abstract.Construct,
                  then: List[LangApi.abstract.Construct],
                  or_else: List[LangApi.abstract.Construct]):
        predicate = self.api.visit(
            condition)
        assert isinstance(predicate, LangApi.abstract.TransPredicate)

        if len(or_else) != 0:
            check_name = self.api.prefix.VarCheck()
            self.check_var = Kiwi.scoreboard.score.Score(self.api).InitsType(
                check_name, check_name
            ).Assign(Kiwi.tokens.number.IntegerFormat(self.api).Formalize(1))

        self.api.enterCodeScope(self, codeKey='predicate')
        self.api.system(
            LangApi.bytecode.RawJSON(
                predicate.transPredicate()
            )
        )
        self.api.leaveScopeWithKey()

        self.api.system(
            LangApi.bytecode.Execute(
                [
                    LangApi.bytecode.StepIfPredicate(
                        self.api.prefix.FileAttrToDirectory(
                            self.predicate_attr
                        )
                    ),
                    LangApi.bytecode.StepRun(
                        LangApi.bytecode.FunctionDirectCall(
                            self.api.prefix.FileAttrToDirectory(
                                self.if_attr
                            )
                        )
                    )
                ]
            )
        )

        self.name = self.if_attr.toName()
        self.api.enterCodeScope(self, codeKey='if')
        self.analyzer.scope.useLocalSpace(self.then_local, hideMode=True)
        self.api.visit(then)
        if len(or_else) != 0:
            self.check_var.Assign(Kiwi.tokens.number.IntegerFormat(self.api).Formalize(0))
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        self.name = self.else_attr.toName()
        self.api.enterCodeScope(self, codeKey='else')
        self.analyzer.scope.useLocalSpace(self.or_else_local, hideMode=True)
        self.api.visit(or_else)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        if len(or_else) != 0:
            self.api.system(
                LangApi.bytecode.Execute(
                    [
                        LangApi.bytecode.StepIfScoreMatch(
                            self.check_var.attr.toString(),
                            self.check_var.scoreboard.attr.toString(),
                            1
                        ),
                        LangApi.bytecode.StepRun(
                            LangApi.bytecode.FunctionDirectCall(
                                self.api.prefix.FileAttrToDirectory(
                                    self.else_attr
                                )
                            )
                        )
                    ]
                )
            )

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'if':
                return [
                    *self.constructor.attributes.functions,
                    *self.if_attr[:-1],
                    f'{self.if_attr.toName()}.mcfunction'
                ]
            case 'else':
                return [
                    *self.constructor.attributes.functions,
                    *self.else_attr[:-1],
                    f'{self.else_attr.toName()}.mcfunction'
                ]
            case 'predicate':
                return [
                    *self.constructor.attributes.predicates,
                    *self.predicate_attr[:-1],
                    f'{self.predicate_attr.toName()}.json'
                ]
        assert False


associations = dict()
