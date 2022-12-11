from __future__ import annotations

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi.abstract import *
from LangApi.api import Construct
from LangApi.bytecode import *

const_predicate_true = {
    "condition": "minecraft:value_check",
    "value": 1,
    "range": 1
}

const_predicate_false = {
    "condition": "minecraft:value_check",
    "value": 0,
    "range": 1
}
