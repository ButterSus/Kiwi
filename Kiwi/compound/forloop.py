from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Callable, List, Optional

# Custom libraries
# ----------------

import LangApi
from components.kiwiScope import Attr
import components.kiwiASO as kiwi
from components.kiwiTools import dumpAST


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


class For(LangApi.abstract.Block):
    attr: Attr
    for_attr: Attr
    predicate_attr: Attr
    check_var: Optional[Kiwi.scoreboard.score.Score]

    def Formalize(self,
                  initialize: kiwi.statement,
                  condition: kiwi.expression,
                  increment: kiwi.statement,
                  body: List[kiwi.statement]):
        initialize = self.analyzer.visit([initialize])
        condition = self.analyzer.visit(condition)
        increment = [self.analyzer.visit([increment])]

        # Prefix initialization
        # ---------------------

        self.for_attr = self.api.prefix.FileFor()
        self.predicate_attr = self.api.prefix.FilePredicate()

        # Body analyzing
        # --------------

        self.name = self.for_attr.toName()
        self.api.enterCodeScope(self, codeKey='main')
        self.analyzer.scope.useCustomSpace(self, hideMode=True)
        body = self.analyzer.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        return LangApi.api.Construct(
            LangApi.api.ConstructMethod.Reference,
            self,
            [initialize, condition, increment, body],
            raw_args=True
        )

    def Reference(self,
                  initialize: List[LangApi.api.Construct],
                  condition: LangApi.api.Construct,
                  increment: List[LangApi.api.Construct],
                  body: List[LangApi.api.Construct]):
        self.api.bufferPush()
        predicate = self.api.visit(
            condition)
        condition_buffer = self.api.bufferPop()
        assert isinstance(predicate, LangApi.abstract.TransPredicate)

        self.api.enterCodeScope(self, codeKey='predicate')
        self.api.system(
            LangApi.bytecode.RawJSON(
                predicate.transPredicate()
            )
        )
        self.api.leaveScopeWithKey()

        self.api.visit(
            initialize
        )

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
                                self.for_attr
                            )
                        )
                    )
                ]
            )
        )

        self.name = self.for_attr.toName()
        self.api.enterCodeScope(self, codeKey='main')
        self.analyzer.scope.useCustomSpace(self, hideMode=True)
        self.api.visit(body)
        self.api.visit(increment)
        self.api.bufferPaste(condition_buffer)
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
                                self.for_attr
                            )
                        )
                    )
                ]
            )
        )
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'main':
                return [
                    *self.constructor.attributes.functions,
                    *self.for_attr[:-1],
                    f'{self.for_attr.toName()}.mcfunction'
                ]
            case 'predicate':
                return [
                    *self.constructor.attributes.predicates,
                    *self.predicate_attr[:-1],
                    f'{self.predicate_attr.toName()}.json'
                ]
        assert False


associations = dict()
