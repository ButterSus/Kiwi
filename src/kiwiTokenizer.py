from __future__ import annotations

# Default libraries
# -----------------

from tokenize import TokenInfo, NEWLINE, NL, DEDENT, generate_tokens
from io import StringIO
from typing import Iterator
from copy import copy

# Custom libraries
# ----------------

from pegen.tokenizer import Tokenizer as PegenTokenizer


class Tokenizer:
    lexer: PegenTokenizer
    text: str

    def __init__(self, text: str):
        self.text = text
        self.lexer = PegenTokenizer(Tokenize(generate_tokens(StringIO(text).readline)))


def Tokenize(stream: Iterator[TokenInfo]):
    """
    The main task of this function is
    - append newline tokens to both sides of dedent tokens
    """
    for x in stream:
        if x.type in {NEWLINE, NL}:
            y = next(stream)
            while y.type == NL:
                yield y
                y = next(stream)
            if y.type == DEDENT:
                while y.type == DEDENT:
                    yield x
                    yield y
                    yield x
                    y = next(stream)
            else:
                yield x
                yield y
                continue
            yield y
        else:
            yield x
