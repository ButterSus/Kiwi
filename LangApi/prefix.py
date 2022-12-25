"""

"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Callable, TYPE_CHECKING
from enum import Enum
from copy import deepcopy
import functools

# Custom libraries
# ----------------

from components.kiwiScope import Attr, DirAttr

if TYPE_CHECKING:
    from LangApi.api import API


def _StaticAttrCounter(function: Callable[[Prefix, int], Attr]) -> Callable[[], Attr]:
    function.iterator = 0
    @functools.wraps(function)
    def _Counter(self: Prefix) -> Attr:
        result = function.iterator  # noqa
        function.iterator += 1  # noqa
        return function(self, result)
    return _Counter


def _DefaultAttrCounter(function: Callable[[Prefix, int], Attr]) -> Callable[[], Attr]:
    function.iterator = dict()
    @functools.wraps(function)
    def _Counter(self: Prefix) -> Attr:
        current_scope = self.api.getThisScope()
        if current_scope in function.iterator.keys():  # noqa
            result = function.iterator[current_scope]  # noqa
            function.iterator[current_scope] += 1  # noqa
        else:
            function.iterator[current_scope] = 1  # noqa
            result = 0  # noqa
        return function(self, result)
    return _Counter


def _StaticNameCounter(function: Callable[[Prefix, int], str]) -> Callable[[], str]:
    function.iterator = 0
    @functools.wraps(function)
    def _Counter(self: Prefix) -> str:
        result = function.iterator  # noqa
        function.iterator += 1  # noqa
        return function(self, result)
    return _Counter


def _DefaultNameCounter(function: Callable[[Prefix, int], str]) -> Callable[[], str]:
    function.iterator = dict()
    @functools.wraps(function)
    def _Counter(self: Prefix) -> str:
        current_scope = self.api.getThisScope()
        if current_scope in function.iterator.keys():  # noqa
            result = function.iterator[current_scope]  # noqa
            function.iterator[current_scope] += 1  # noqa
        else:
            function.iterator[current_scope] = 1  # noqa
            result = 0  # noqa
        return function(self, result)
    return _Counter


def _FileName(function: Callable[[..., str], str]) -> Callable[[str], str]:
    @functools.wraps(function)
    def _Wrapper(self: Prefix, name: str) -> str:
        result = function(self, name)
        mode = True
        final_result = str()
        for symbol in result:
            if mode == symbol.isupper():
                mode = not mode
                final_result += '-'
                symbol = symbol.lower()
            final_result += symbol
        return final_result
    return _Wrapper


def _FileAttr(function: Callable[[..., str], Attr]) -> Callable[[str], Attr]:
    @functools.wraps(function)
    def _Wrapper(self: Prefix, name: str) -> Attr:
        result = function(self, name)
        final_result = deepcopy(result)
        for i in range(len(result)):
            mode = True
            string_result = str()
            for symbol in result[i]:
                if mode == symbol.isupper():
                    mode = not mode
                    string_result += '-'
                    symbol = symbol.lower()
                string_result += symbol
            final_result[i] = string_result
        return final_result
    return _Wrapper


def _FileAttrName(function: Callable[[..., Attr], str]) -> Callable[[Attr], str]:
    @functools.wraps(function)
    def _Wrapper(self: Prefix, name: Attr) -> str:
        result = function(self, name)
        mode = True
        final_result = str()
        for symbol in result:
            if mode == symbol.isupper():
                mode = not mode
                final_result += '-'
                symbol = symbol.lower()
            final_result += symbol
        return final_result
    return _Wrapper


class ScopeMode(Enum):
    GLOBAL = 0
    LOCAL = 1


class Prefix:
    mode: ScopeMode = ScopeMode.LOCAL
    api: API

    def __init__(self, api: API):
        self.api = api

    # CONSTANT VALUES
    # ===============

    default_scoreboard = Attr(['default_scoreboard'])

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
                prefix = list()
                for scope in self.api.scopeFolder[1:]:
                    prefix.append(scope.name)
                return Attr(prefix + attr)
            case ScopeMode.GLOBAL:
                return attr

    # SPECIFIC PREFIXES
    # =================

    @_DefaultAttrCounter
    def SpecTemp(self, counter: int) -> Attr:
        """
        Used to add prefix for temporary variables
        """
        return self.ModLocal(Attr([f"$temp--{counter}"]))

    def SpecStatic(self, attr: Attr) -> Attr:
        """
        Used to add project name for specific
        object names, for example scoreboards.
        They have no any binding to project, so that means,
        we should add additional prefix
        :param attr:
        Input attribute
        :return:
        Output attribute with prefix
        """
        return Attr([self.api.configGeneral['project_name']] + attr)

    def SpecFileProject(self, attr: Attr) -> DirAttr:
        return DirAttr(Attr([self.api.configGeneral['project_name']]), attr)

    @staticmethod
    def SpecConst(value: int) -> Attr:
        """
        Used to formalize value to attribute with constant format
        e.g:
        We have 2 local scopes:
        IfElse -> While -> <attr>
        So, <value> is the number by default, we don't need to
        add any additional prefixes like scope or global prefix,
        the output use "#" sign, because Minecraft don't display
        players with that prefix
        :param value:
        Input number
        :return:
        Output cut attribute
        """
        return Attr([f'#{value}'])

    # VARIABLE PREFIXES
    # =================

    @_DefaultAttrCounter
    def VarReturn(self, counter: int) -> Attr:
        """
        Returns attribute for variable of return statement
        """
        return self.ModLocal(Attr([f'$return--{counter}']))

    @_DefaultAttrCounter
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

    @_DefaultAttrCounter
    def FileIf(self, counter: int) -> Attr:
        """
        Return attribute for file name of if statement
        """
        return self.ModLocal(Attr([f'--if--{counter}']))

    @_DefaultAttrCounter
    def FileElse(self, counter: int) -> Attr:
        """
        Return attribute for file name of else statement
        """
        return self.ModLocal(Attr([f'--else--{counter}']))

    @_DefaultAttrCounter
    def FileFor(self, counter: int) -> Attr:
        """
        Return attribute for file name of for statement
        """
        return self.ModLocal(Attr([f'--for--{counter}']))

    @_DefaultAttrCounter
    def FileWhile(self, counter: int) -> Attr:
        """
        Return attribute for file name of while statement
        """
        return self.ModLocal(Attr([f'--while--{counter}']))

    @_DefaultAttrCounter
    def FilePredicate(self, counter: int) -> Attr:
        """
        Return attribute for file name of predicate,
        which is used by if statement as condition, described in JSON
        """
        return self.ModLocal(Attr([f'--predicate--{counter}']))

    @_FileAttr
    def FileNamespace(self, name: str) -> Attr:
        return self.ModLocal(Attr([f'--namespace--{name}--']))

    @_FileAttr
    def FileFunction(self, name: str) -> Attr:
        return Attr([name])

    # Special methods
    # ---------------

    @_FileName
    def FileNameToDirectory(self, name: str) -> str:
        return DirAttr(Attr([self.api.configGeneral['project_name']]), Attr([name])).toString()

    @_FileAttrName
    def FileAttrToDirectory(self, attr: Attr) -> str:
        return DirAttr(Attr([self.api.configGeneral['project_name']]), attr).toString()

    @_FileName
    def useConverter(self, name: str) -> str:
        return name
