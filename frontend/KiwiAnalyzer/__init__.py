"""
This code is unlicensed
By ButterSus

Previous stage:
    AST

About current stage:
    This stage is used to generate Semantic Analyzer Objects
    SAO -> Compiler

Next stage:
    Compiler
"""


from __future__ import annotations

import frontend
from frontend import KiwiAST as kiwi
import pathlib
from dataclasses import dataclass
from typing import Any, List, Optional, Type, Callable, TYPE_CHECKING
from frontend.KiwiAnalyzer.scopes import ScopeSystem
import frontend.std as std
import frontend.KiwiAnalyzer.objects as kiwiBranch


if TYPE_CHECKING:
    from build import Builder


Token: kiwi.Token | kiwi.AST | list


@dataclass
class Module:
    name: str
    AST: kiwi.Module
    scope: ScopeSystem


class KiwiVisitor:
    scope: ScopeSystem

    def __init__(self, libScope: Optional[dict] = None):
        self.scope = ScopeSystem(libScope)

    def getAttributes(self, node: kiwi.AST):
        try:
            targets = node.__annotations__
        except AttributeError:
            return []
        for annotation in targets:
            attribute = node.__getattribute__(annotation)
            yield attribute

    def knockCall(self, node: Token) -> Callable[[Token], None]:
        name = node.__class__.__name__
        if name in dir(self):
            return self.__getattribute__(name)

    def visit(self, node: Token) -> Any:
        if isinstance(node, list):
            result = list()
            for item in node:
                result.append(self.visit(item))
            return result
        if isinstance(node, kiwi.Token):
            if function := self.knockCall(node):
                return function(node)
            return node
        if isinstance(node, kiwi.AST):
            if function := self.knockCall(node):
                return function(node)
            result = list()
            for attribute in self.getAttributes(node):
                result.append(self.visit(attribute))
            return result

    def visitAST(self, node: kiwi.AST) -> List[Any]:
        result = list()
        for attribute in self.getAttributes(node):
            result.append(self.visit(attribute))
        return result

    def getName(self, node: kiwi.Name | kiwi.Attribute) -> List[str]:
        if isinstance(node, kiwi.Attribute):
            result = self.getName(node.target)
            result.append(node.attribute)
            return result
        return [str(node)]

    # SIMPLE STATEMENTS
    # =================

    # Assignment Statements
    # ---------------------

    def AnnAssignment(self, node: kiwi.AnnAssignment):
        names = map(lambda x: x.value, node.targets)
        targets: List[List[str]] = list(map(self.getName, names))
        type: Type[std.KiwiType] = self.visit(node.type)
        assert issubclass(type, std.KiwiType)
        for target in targets:
            self.scope.write(target, kiwiBranch.Variable(type))
        return

    def Assignment(self, node: kiwi.Assignment):
        return

    def Annotation(self, node: kiwi.Annotation):
        names = map(lambda x: x.value, node.targets)
        targets: List[List[str]] = list(map(self.getName, names))
        type: Type[std.KiwiType] = self.visit(node.type)
        assert issubclass(type, std.KiwiType)
        for target in targets:
            self.scope.write(target, kiwiBranch.Variable(type))
        return

    # COMPOUND STATEMENTS
    # ===================

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        self.scope.newNamedSpace(node.name)
        self.visit([*node.body_default, *node.body_public])
        self.scope.enablePrivate()
        self.visit(node.body_private)
        self.scope.leaveSpace()
        return

    def FuncDef(self, node: kiwi.FuncDef):
        self.scope.newLocalSpace()
        self.visit(node.body)
        self.scope.leaveSpace()
        return

    # EXPRESSIONS
    # ===========

    def Expression(self, node: kiwi.Expression):
        if isinstance(node.value, kiwi.Name):
            return self.scope.get(node.value)
        if isinstance(node.value, kiwi.Number):
            return node.value
        self.visitAST(node)


class KiwiAnalyzer:
    builder: Builder
    include_directories: List[pathlib.Path] = [pathlib.Path('./')]

    def getFileDir(self, file: str) -> Optional[str]:
        for directory in map(lambda x: x / file, self.include_directories):
            directory: pathlib.Path
            if directory.exists():
                return str(directory)
            if not directory.suffix:
                directory = directory.with_suffix('.kiwi')
                if directory.exists():
                    return str(directory)
        return None

    def openModule(self, file: str, name: str = '__main__') -> Optional[Module]:
        file = self.getFileDir(file)
        with open(file) as kiwiFile:
            ast: kiwi.Module = frontend.parse(
                        kiwiFile.read()
                    )
            libScope = dict()
            for alias in ast.imports:
                importScope = self.openModule(alias.directory).scope.globalScope
                if isinstance(alias.as_name, list):
                    fromAliases: List[kiwi.Alias] = alias.as_name
                    for fromAlias in fromAliases:
                        libScope[fromAlias.as_name] = importScope.get(fromAlias.directory)
                    continue
                libScope[alias.as_name] = importScope
            visitor = KiwiVisitor(libScope)
            visitor.visit(ast)
            return Module(name, ast, visitor.scope)

    def __init__(self, builder: Builder, debug: bool = False):
        self.builder = builder
        self.directories_init()
        module = self.openModule(
            self.builder.project['entry_file']
        )

        if debug:
            print(f'AST:\n{frontend.dump(module.AST)}\n')
            print(f'Scopes:\n{module.scope.dump()}\n')

    def directories_init(self):
        if self.builder.options is not None:
            if (include_directories := self.builder.options['include_directories']) is not None:
                self.include_directories.extend(map(pathlib.Path, include_directories))
