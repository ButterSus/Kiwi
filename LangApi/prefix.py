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
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Callable, TYPE_CHECKING
from enum import Enum
import functools

# Custom libraries
# ----------------

from Kiwi.components.kiwiScope import Attr
if TYPE_CHECKING:
    from LangApi import API


def _StaticCounter(function: Callable[[Prefix, int], Attr]) -> Callable[[], Attr]:
    function.iterator = 0
    @functools.wraps(function)
    def _Counter(self: Prefix) -> Attr:
        result = function.iterator  # noqa
        function.iterator += 1  # noqa
        return function(self, result)
    return _Counter


def _DefaultCounter(function: Callable[[Prefix, int], Attr]) -> Callable[[], Attr]:
    function.iterator = 0
    @functools.wraps(function)
    def _Counter(self: Prefix) -> Attr:
        result = function.iterator  # noqa
        function.iterator += 1  # noqa
        return function(self, result)
    return _Counter


class ScopeMode(Enum):
    GLOBAL = 0
    LOCAL = 1


class Prefix:
    mode: ScopeMode = ScopeMode.LOCAL
    api: API

    def __init__(self, api: API):
        self.api = api

    # GENERAL MODIFIERS
    # =================

    @staticmethod
    def ModGlobal(attr: Attr) -> Attr:
        """
        Used to add global prefix
        For example you can add project prefix to
        avoid some scope conflicts, but I think it's useless
        at the moment because we have datapack folder
        :param attr:
        Input attribute
        :return:
        Output attribute with prefix
        """
        return attr

    def ModLocal(self, attr: Attr) -> Attr:
        """
        Used to add local prefix
        In this situation it's used to save up
        scope attributes to get final attribute
        e.g:
        We have 2 local scopes:
        IfElse -> While -> <attr>
        Let's assume IfElse have name "a",
        While have name "b", then we will get
        "a.b.<attr>"
        :param attr:
        Input attribute
        :return:
        Output attribute with prefix
        """
        match self.mode:
            case ScopeMode.LOCAL:
                return attr
            case ScopeMode.GLOBAL:
                return attr

    # SPECIFIC PREFIXES
    # =================

    @_DefaultCounter
    def SpecTemp(self, counter: int) -> Attr:
        """
        Used to add prefix for temporary variables
        """
        return Attr(f"$temp--{counter}")

    @staticmethod
    def SpecStatic(attr: Attr) -> Attr:
        """
        Used to add project name for specific
        object names, for example scoreboards.
        They have no any binding to project, so that means,
        we should add additional prefix.
        :param attr:
        Input attribute
        :return:
        Output attribute with prefix
        """
        return attr

    @staticmethod
    def SpecConst(attr: Attr) -> Attr:
        """
        Used to formalize attr to constant format
        e.g:
        We have 2 local scopes:
        IfElse -> While -> <attr>
        So, <attr> is the number by default, we don't need to
        add any additional prefixes like scope or global prefix,
        the output use "#" sign, because Minecraft don't display
        players with that prefix
        :param attr:
        Input attribute
        :return:
        Output cut attribute
        """
        return Attr([f'#{attr[-1]}'])

    # VARIABLE PREFIXES
    # =================

    @_DefaultCounter
    def VarReturn(self, counter: int) -> Attr:
        """
        Returns attribute for variable of return statement
        """
        return self.ModLocal(Attr([f'$return--{counter}']))

    @_DefaultCounter
    def VarIf(self, counter: int) -> Attr:
        """
        Returns attribute for variable of if statement
        """
        return self.ModLocal(Attr([f'$if--{counter}']))

    @_DefaultCounter
    def VarElse(self, counter: int) -> Attr:
        """
        Returns attribute for variable of else statement
        """
        return self.ModLocal(Attr([f'$else--{counter}']))

    @_DefaultCounter
    def VarFor(self, counter: int) -> Attr:
        """
        Returns attribute for variable of for statement
        """
        return self.ModLocal(Attr([f'$for--{counter}']))

    @_DefaultCounter
    def VarWhile(self, counter: int) -> Attr:
        """
        Returns attribute for variable of while statement
        """
        return self.ModLocal(Attr([f'$while--{counter}']))

    @_DefaultCounter
    def VarCheck(self, counter: int) -> Attr:
        """
        Returns attribute for variable of check,
        that is used to check:
        if condition was true, then do not run else body
        else if condition was not true, then run else body
        """
        return self.ModLocal(Attr([f'$check--{counter}']))

    # FILE PREFIXES
    # =============

    @_StaticCounter
    def FileIf(self, counter: int) -> Attr:
        """
        Return attribute for file name of if statement
        """
        return self.ModLocal(Attr([f'--if--{counter}']))

    @_StaticCounter
    def FileElse(self, counter: int) -> Attr:
        """
        Return attribute for file name of else statement
        """
        return self.ModLocal(Attr([f'--else--{counter}']))

    @_StaticCounter
    def FileFor(self, counter: int) -> Attr:
        """
        Return attribute for file name of for statement
        """
        return self.ModLocal(Attr([f'--for--{counter}']))

    @_StaticCounter
    def FileWhile(self, counter: int) -> Attr:
        """
        Return attribute for file name of while statement
        """
        return self.ModLocal(Attr([f'--while--{counter}']))

    @_StaticCounter
    def FilePredicate(self, counter: int) -> Attr:
        """
        Return attribute for file name of predicate,
        which is used by if statement as condition, described in JSON
        """
        return self.ModLocal(Attr([f'--predicate--{counter}']))
