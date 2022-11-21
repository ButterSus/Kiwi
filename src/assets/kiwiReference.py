from __future__ import annotations

# Default libraries
# -----------------

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

# Custom libraries
# ----------------

if TYPE_CHECKING:
    from src.assets.kiwiScope import ScopeType, Key

@dataclass
class Reference:
    scope: ScopeType
    showKeys: Key
    _keys: str

    def __init__(self, scope: ScopeType, keys: Key, showKeys: Key = None):
        if showKeys is None:
            showKeys = keys
        self.scope = scope
        self._keys = keys
        self.showKeys = showKeys

    def _getter(self) -> Any | ScopeType:
        return self.scope.content.get(self._keys)

    def _setter(self, value: Any):
        self.scope.write(self._keys, value)

    var: Any = property(
        fset=_setter,
        fget=_getter
    )
