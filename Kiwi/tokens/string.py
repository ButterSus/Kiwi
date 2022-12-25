from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable, List
from string import Formatter
from itertools import chain
from copy import deepcopy

# Custom libraries
# ----------------

import LangApi

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


class StringFormat(LangApi.abstract.Format,
                   LangApi.abstract.SupportAdd,
                   LangApi.abstract.SupportMul,
                   LangApi.abstract.Printable):
    _formatter = Formatter()
    values: List[list[str, bool]]

    def _optimize(self):
        i = 0
        while i < len(self.values) - 1:
            if self.values[i][1] == self.values[i + 1][1]:
                self.values[i][0] += self.values[i + 1][0]
                del self.values[i + 1]
                i -= 1
            i += 1

    def Formalize(self, token: str, isFormatted: bool) -> StringFormat:
        self.values = list()
        self.values.append([token, isFormatted])
        return self

    def Add(self, other: StringFormat) -> StringFormat:
        assert isinstance(other, StringFormat)
        self.values.extend(other.values)
        self._optimize()
        return self

    def Mul(self, other: Kiwi.tokens.number.IntegerFormat) -> StringFormat:
        assert isinstance(other, Kiwi.tokens.number.IntegerFormat)
        self.values = list(
            chain.from_iterable([deepcopy(self.values) for _ in range(other.value)])
        )
        self._optimize()
        return self

    def PrintSource(self) -> LangApi.bytecode.NBTLiteral:
        print_result = list()
        for value, isFormatted in self.values:
            if isFormatted:
                information = self._formatter.parse(value)
                result = list()
                for string, expression, _, _ in information:
                    if string is not None:
                        result.append(
                            StringFormat(self.api).Formalize(
                                string, False
                            ).PrintSource()
                        )
                    if expression is not None:
                        evaluated: LangApi.abstract.Printable = self.api.eval(expression)
                        result.append(evaluated.PrintSource())
                print_result.append(result)
            else:
                print_result.append({
                    'text': value
                })
        if len(print_result) == 1:
            return print_result[0]
        return print_result


associations = dict()
