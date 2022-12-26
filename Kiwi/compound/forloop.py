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


class ForClassic(LangApi.abstract.Block):
    attr: Attr
    for_attr: Attr
    predicate_attr: Attr
    check_var: Optional[Kiwi.scoreboard.score.Score]

    body_local: int

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

        self.for_attr = self.api.prefix.FileForClassic()
        self.predicate_attr = self.api.prefix.FilePredicate()

        # Body analyzing
        # --------------

        self.name = self.for_attr.toName()
        self.api.enterCodeScope(self, codeKey='main')
        self.body_local = self.analyzer.scope.useLocalSpace(hideMode=True)
        body = self.analyzer.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [initialize, condition, increment, body],
            raw_args=True
        )

    def Reference(self,
                  initialize: List[LangApi.abstract.Construct],
                  condition: LangApi.abstract.Construct,
                  increment: List[LangApi.abstract.Construct],
                  body: List[LangApi.abstract.Construct]):
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
        self.analyzer.scope.useLocalSpace(self.body_local, hideMode=True)
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


class ForIterator(LangApi.abstract.Block):
    attr: Attr
    for_attr: Attr
    check_var: Optional[Kiwi.scoreboard.score.Score]

    body_local: int

    def Formalize(self,
                  target: LangApi.abstract.Assignable,
                  iterator: kiwi.expression,
                  body: List[kiwi.statement]):
        iterator = self.analyzer.visit(iterator)

        # Prefix initialization
        # ---------------------

        self.for_attr = self.api.prefix.FileForIterator()

        # Body analyzing
        # --------------

        self.name = self.for_attr.toName()
        self.api.enterCodeScope(self, codeKey='main')
        self.body_local = self.analyzer.scope.useLocalSpace(hideMode=True)
        body = self.analyzer.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [target, iterator, body],
            raw_args=True
        )

    def Reference(self,
                  target: LangApi.abstract.Assignable,
                  iterator: LangApi.abstract.Construct,
                  body: List[LangApi.abstract.Construct]):
        iterator: LangApi.abstract.Iterable = self.api.visit(
            iterator
        )

        self.api.system(
            LangApi.bytecode.Execute(
                [
                    LangApi.bytecode.StepIfPredicate(
                        self.api.prefix.FileAttrToDirectory(
                            iterator.iterationCondition
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
        self.analyzer.scope.useLocalSpace(self.body_local, hideMode=True)
        self.api.visit(
            LangApi.abstract.Construct(
                LangApi.abstract.ConstructMethod.AssignOperation,
                target,
                [iterator.iterationItem]
            )
        )
        self.api.visit(body)
        iterator.NewIteration()
        self.api.system(
            LangApi.bytecode.Execute(
                [
                    LangApi.bytecode.StepIfPredicate(
                        self.api.prefix.FileAttrToDirectory(
                            iterator.iterationCondition
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
        assert False


associations = dict()
