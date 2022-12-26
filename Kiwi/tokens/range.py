from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable, Type, List

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


class Range(LangApi.abstract.Block, LangApi.abstract.Formalizable, LangApi.abstract.Iterable):
    _start: LangApi.abstract.Abstract
    _end: LangApi.abstract.Abstract
    iterationItem: Kiwi.scoreboard.score.Score

    def Formalize(self,
                  start: kiwi.expression,
                  end: kiwi.expression):
        start = self.analyzer.visit(start)
        end = self.analyzer.visit(end)
        self.iterationCondition = self.api.prefix.FilePredicate()

        return LangApi.abstract.Construct(
            LangApi.abstract.ConstructMethod.Reference,
            self,
            [start, end],
            raw_args=True
        )

    def Reference(self,
                  start: kiwi.expression,
                  end: kiwi.expression):
        self._start = self.api.visit(start)
        self._end = self.api.visit(end)
        assert isinstance(self._start, Kiwi.tokens.number.IntegerFormat)
        assert isinstance(self._end, Kiwi.tokens.number.IntegerFormat)
        item_attr = self.api.prefix.VarItem()
        self.iterationItem = Kiwi.scoreboard.score.Score(
            self.api
        ).InitsType(
            item_attr, item_attr
        ).Assign(
            self._start
        )
        self.api.enterCodeScope(self, codeKey='predicate')
        self.api.system(
            LangApi.bytecode.RawJSON(
                self.iterationItem.LessThanEquals(
                    self._end
                )
            )
        )
        self.api.leaveScopeWithKey()
        return self

    def NewIteration(self):
        self.iterationItem.IAdd(
            Kiwi.tokens.number.IntegerFormat(
            self.api
        ).Formalize(1))

    def toPath(self, key: str) -> List[str]:
        match key:
            case 'predicate':
                return [
                    *self.constructor.attributes.predicates,
                    *self.iterationCondition[:-1],
                    f'{self.iterationCondition.toName()}.json'
                ]
        assert False


associations = dict()
