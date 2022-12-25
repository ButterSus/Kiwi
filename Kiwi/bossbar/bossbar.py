from __future__ import annotations

# Default libraries
# -----------------

from typing import TYPE_CHECKING, Any, Optional, Callable, Type

# Custom libraries
# ----------------

import LangApi
import components.kiwiASO as kiwi
from components.kiwiScope import Attr


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


default_criteria = 'dummy'


# Content of file
# ---------------


class Bossbar(LangApi.abstract.Variable):
    isNative = True
    """
    Specifies for analyzer not to handle AST parameters in annotation.
    """

    _general: Bossbar = None
    @classmethod
    @property
    def general(cls) -> Scoreboard:  # noqa
        api = LangApi.api.API.general
        if cls._general is None:
            api.enableGlobal()
            cls._general = Bossbar(api).InitsType(api.prefix.default_bossbar,
                                                                   api.prefix.default_bossbar)
            api.disableGlobal()
        return cls._general

    def InitsType(self, attr: Attr, address: Attr, *args) -> Bossbar:
        assert not args

        self.attr = self.api.prefix.SpecStatic(attr)
        self.address = address


        return self

    def Assign(self, other: LangApi.abstract.Abstract) -> Bossbar:
        if isinstance(other, Kiwi.tokens.string.StringFormat):
            self.api.system(
                LangApi.bytecode.BossbarCreate(

                    name=self.attr.toString(),
                    id=self.attr.toName()
                )
            )
            return self

        assert False



class BossbarClass(LangApi.abstract.Class):
    def Call(self, *args: LangApi.abstract.Abstract):
        pass

    def GetChild(self) -> Type[Bossbar]:
        return Bossbar


associations = {
    'bossbar': BossbarClass
}
