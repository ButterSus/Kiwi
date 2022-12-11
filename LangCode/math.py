from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *
import Kiwi.components.kiwiASO as kiwi


class Expression(Formalizable):
    def Formalize(self, value: Construct = None) -> Optional[Abstract]:
        if value is None:
            return
        result = self.api.visit(value)
        self.api.resetExpression()
        return result


class NotFullExpression(Formalizable):
    def Formalize(self, value: Construct = None) -> Optional[Abstract]:
        if value is None:
            return
        result = self.api.visit(value)
        return result


class AnyBool:
    predicate: NBTLiteral


class Disjunctions(Formalizable, AnyBool):
    def Formalize(self, values: List[kiwi.expression]) -> Disjunctions:
        self.predicate = dict()
        self.predicate['condition'] = 'minecraft:alternative'
        self.predicate['terms'] = list()
        for value in values:
            if isinstance(value, AnyBool):
                self.predicate['terms'].append(value.predicate)
                continue
            assert isinstance(value, TransPredicate)
            self.predicate['terms'].append(value.transPredicate())
        return self


class Conjunctions(Formalizable, AnyBool):
    def Formalize(self, values: List[kiwi.expression]) -> Conjunctions:
        self.predicate = dict()
        self.predicate['condition'] = 'minecraft:inverted'
        self.predicate['term'] = dict()
        self.predicate['term']['condition'] = 'minecraft:alternative'
        self.predicate['term']['terms'] = list()
        for value in values:
            predicate = dict()
            predicate['condition'] = 'minecraft:inverted'
            if isinstance(value, AnyBool):
                predicate['term'] = value.predicate
                self.predicate['term']['terms'].append(predicate)
                continue
            assert isinstance(value, TransPredicate)
            predicate['term'] = value.transPredicate()
            self.predicate['term']['terms'].append(predicate)
        return self


class Comparisons(Formalizable, AnyBool):
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
                    assert isinstance(value, SupportEquals)
                    predicate['term'] = value.Equals(values[i + 1])
                case '!=':
                    value = values[i]
                    assert isinstance(value, SupportNotEquals)
                    predicate['term'] = value.NotEquals(values[i + 1])
                case '<=':
                    value = values[i]
                    assert isinstance(value, SupportLessThanEquals)
                    predicate['term'] = value.LessThanEquals(values[i + 1])
                case '>=':
                    value = values[i]
                    assert isinstance(value, SupportGreaterThanEquals)
                    predicate['term'] = value.GreaterThanEquals(values[i + 1])
                case '>':
                    value = values[i]
                    assert isinstance(value, SupportGreaterThan)
                    predicate['term'] = value.GreaterThan(values[i + 1])
                case '<':
                    value = values[i]
                    assert isinstance(value, SupportLessThan)
                    predicate['term'] = value.LessThan(values[i + 1])
            self.predicate['term']['terms'].append(predicate)
        return self
