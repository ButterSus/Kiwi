"""
Copyright (c) 2022 Krivoshapkin Edward

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This module represents the first step of compiler frontend.
It creates a lexical (or tokenizer) tokens, that can be used by the second step of frontend (parser).
Basically, the tokenizer is Python tokenizer post processor.
"""

from __future__ import annotations

# Default libraries
# -----------------

from tokenize import TokenInfo, NEWLINE, NL, DEDENT, COMMENT, generate_tokens
from io import StringIO
from typing import Iterator

# Custom libraries
# ----------------

from pegen.tokenizer import Tokenizer as PegenTokenizer


class Tokenizer:
    lexer: PegenTokenizer
    text: str

    def __init__(self, text: str):
        self.text = text
        self.lexer = PegenTokenizer(
            Tokenize(
                Ignores(
                    generate_tokens(StringIO(text).readline)
                )
            )
        )


def Ignores(stream: Iterator[TokenInfo]) -> Iterator[TokenInfo]:
    for token in stream:
        if token.type == COMMENT:
            continue
        yield token


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
