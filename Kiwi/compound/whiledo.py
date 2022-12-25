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


class While(LangApi.abstract.Block):
    attr: Attr
    while_attr: Attr
    predicate_attr: Attr
    check_var: Optional[Kiwi.scoreboard.score.Score]

    body_local: int

    def Formalize(self,
                  condition: kiwi.expression,
                  body: List[kiwi.statement]):
        condition = self.analyzer.visit(condition)

        # Prefix initialization
        # ---------------------

        self.while_attr = self.api.prefix.FileWhile()
        self.predicate_attr = self.api.prefix.FilePredicate()

        # Body analyzing
        # --------------

        self.name = self.while_attr.toName()
        self.api.enterCodeScope(self, codeKey='main')
        self.body_local = self.analyzer.scope.useLocalSpace(hideMode=True)
        body = self.analyzer.visit(body)
        self.analyzer.scope.leaveSpace()
        self.api.leaveScopeWithKey()

        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [condition, body],
            raw_args=True
        )

    def Reference(self,
                  condition: LangApi.abstract.Construct,
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
                                self.while_attr
                            )
                        )
                    )
                ]
            )
        )

        self.name = self.while_attr.toName()
        self.api.enterCodeScope(self, codeKey='main')
        self.analyzer.scope.useLocalSpace(self.body_local, hideMode=True)
        self.api.visit(body)
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
                                self.while_attr
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
                    *self.while_attr[:-1],
                    f'{self.while_attr.toName()}.mcfunction'
                ]
            case 'predicate':
                return [
                    *self.constructor.attributes.predicates,
                    *self.predicate_attr[:-1],
                    f'{self.predicate_attr.toName()}.json'
                ]
        assert False


associations = dict()
