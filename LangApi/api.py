from __future__ import annotations

# Default libraries
# -----------------

from typing import Dict, TYPE_CHECKING, Callable as FCallable, Any, List, Type
from dataclasses import dataclass
from itertools import chain

# Custom libraries
# ----------------

if TYPE_CHECKING:
    import LangApi.abstract as LangApi
    from header.kiwiAnalyzer import Analyzer


@dataclass
class Construct:
    method: FCallable[..., Any]
    parent: Any
    arguments: List[Construct | LangApi.Argument | str]


class API:
    defaultLibScope: Dict[str, Dict[str, Type[LangApi.Argument]]] = {
        'builtins': dict()
    }
    analyzer: Analyzer

    def __init__(self, analyzer: Analyzer):
        self.analyzer = analyzer
        for name, value in self.defaultLibScope['builtins'].items():
            self.analyzer.scope.write(
                name, Construct(
                    value.Annotation,
                    value,
                    []
                ))
        del (self.defaultLibScope['builtins'])
        for module_name, module_scope in self.defaultLibScope.items():
            self.analyzer.scope.newNamedSpace(module_name)
            for name, value in module_scope.items():
                self.analyzer.scope.write(
                    name, Construct(
                        value.Annotation,
                        value,
                        []
                    ))
            self.analyzer.scope.leaveSpace()

    def _unpackTuple(self, value: tuple) -> tuple:
        try:
            return self._unpackTuple(tuple(chain.from_iterable(value)))
        except TypeError:
            return value

    def visit(self, expr: list | Construct) -> list | Construct:
        if isinstance(expr, list):
            result = list()
            for item in expr:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(self._unpackTuple(visited))
                    continue
                if visited is None:
                    continue
                result.append(visited)
            return result
        if isinstance(expr, Construct):
            return expr.method(expr.parent(self), *expr.arguments)

    @classmethod
    def build(cls, module_name, scope: Dict[str, Type[LangApi.Argument]]):
        if module_name not in cls.defaultLibScope.keys():
            cls.defaultLibScope[module_name] = scope
        else:
            cls.defaultLibScope[module_name] |= scope
