from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from built_in.types import *


class Tellraw(KiwiCallable):
    def Call(self, compiler: Compiler, *args: Argument):
        new = '\n'
        tab = ' ' * 12
        args = map(toNonReference, *args)
        constructor = compiler.constructor
        constructor.cmd(f'tellraw @a [{(", " + new + tab).join(map(lambda x: x.toDisplay(), args))}]')


scope = {
    "tellraw": Tellraw()
}
