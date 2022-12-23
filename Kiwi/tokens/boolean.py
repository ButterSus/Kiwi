from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable, List
from abc import ABC

# Custom libraries
# ----------------

import LangApi


if TYPE_CHECKING:
    import compiler
    import LangApi
    import Kiwi
    import components.kiwiASO as kiwi


# Initialization of modules
# -------------------------

def init(_compiler: Any, _LangApi: Any, _Kiwi: Any):
    globals()['compiler'] = _compiler  # noqa
    globals()['LangApi'] = _LangApi  # noqa
    globals()['Kiwi'] = _Kiwi  # noqa


# Content of file
# ---------------


class Expression(LangApi.abstract.Formalizable,
                 LangApi.abstract.TransPredicate,
                 ABC):
    predicate: LangApi.bytecode.NBTLiteral


class Disjunctions(Expression):
    def Formalize(self, values: List[kiwi.expression]) -> Disjunctions:
        self.predicate = dict()
        self.predicate['condition'] = 'minecraft:alternative'
        self.predicate['terms'] = list()
        for value in values:
            if isinstance(value, Expression):
                self.predicate['terms'].append(value.predicate)
                continue
            assert isinstance(value, LangApi.abstract.TransPredicate)
            self.predicate['terms'].append(value.transPredicate())
        return self

    def transPredicate(self) -> LangApi.bytecode.NBTLiteral:
        return self.predicate


class Conjunctions(Expression):
    def Formalize(self, values: List[kiwi.expression]) -> Conjunctions:
        self.predicate = dict()
        self.predicate['condition'] = 'minecraft:inverted'
        self.predicate['term'] = dict()
        self.predicate['term']['condition'] = 'minecraft:alternative'
        self.predicate['term']['terms'] = list()
        for value in values:
            predicate = dict()
            predicate['condition'] = 'minecraft:inverted'
            if isinstance(value, Expression):
                predicate['term'] = value.predicate
                self.predicate['term']['terms'].append(predicate)
                continue
            assert isinstance(value, LangApi.abstract.TransPredicate)
            predicate['term'] = value.transPredicate()
            self.predicate['term']['terms'].append(predicate)
        return self

    def transPredicate(self) -> LangApi.bytecode.NBTLiteral:
        return self.predicate


class Comparisons(Expression):
    def Formalize(self, values: List[kiwi.expression], ops: List[kiwi.Token]) -> Comparisons:
        self.predicate = dict()
        self.predicate['condition'] = 'minecraft:inverted'
        self.predicate['term'] = dict()
        self.predicate['term']['condition'] = 'minecraft:alternative'
        self.predicate['term']['terms'] = list()
        for i, op in enumerate(ops):
            predicate = dict()
            predicate['condition'] = 'minecraft:inverted'
            match op.value:
                case '==':
                    value = values[i]
                    assert isinstance(value, LangApi.abstract.SupportEquals)
                    predicate['term'] = value.Equals(values[i + 1])
                case '!=':
                    value = values[i]
                    assert isinstance(value, LangApi.abstract.SupportNotEquals)
                    predicate['term'] = value.NotEquals(values[i + 1])
                case '<=':
                    value = values[i]
                    assert isinstance(value, LangApi.abstract.SupportLessThanEquals)
                    predicate['term'] = value.LessThanEquals(values[i + 1])
                case '>=':
                    value = values[i]
                    assert isinstance(value, LangApi.abstract.SupportGreaterThanEquals)
                    predicate['term'] = value.GreaterThanEquals(values[i + 1])
                case '>':
                    value = values[i]
                    assert isinstance(value, LangApi.abstract.SupportGreaterThan)
                    predicate['term'] = value.GreaterThan(values[i + 1])
                case '<':
                    value = values[i]
                    assert isinstance(value, LangApi.abstract.SupportLessThan)
                    predicate['term'] = value.LessThan(values[i + 1])
            self.predicate['term']['terms'].append(predicate)
        return self

    def transPredicate(self) -> LangApi.bytecode.NBTLiteral:
        return self.predicate


associations = dict()
