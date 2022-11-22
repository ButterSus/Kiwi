from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from built_in.types import *
from built_in.std import stdout


built_in = {
    "score": Score,
    "scoreboard": Scoreboard
} | stdout.scope
