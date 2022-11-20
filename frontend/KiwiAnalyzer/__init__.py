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
import frontend.std as std
from typing import Any, List, Optional, Type, Callable, TYPE_CHECKING
from frontend.KiwiAnalyzer.scopes import ScopeSystem, Names


if TYPE_CHECKING:
    from build import Builder


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
            return [], []
        for annotation in targets:
            attribute = node.__getattribute__(annotation)
            yield annotation, attribute

    def knockCall(self, node: Any) -> Callable[[Any], None]:
        name = node.__class__.__name__
        if name in dir(self):
            return self.__getattribute__(name)

    def visit(self, node: Any) -> Any:
        if isinstance(node, list):
            result = list()
            for item in node:
                visited = self.visit(item)
                if isinstance(visited, tuple):
                    result.extend(visited)
                    continue
                if visited is None:
                    continue
                result.append(visited)
            return result
        if isinstance(node, kiwi.Token):
            if function := self.knockCall(node):
                return function(node)
            return node
        if isinstance(node, kiwi.AST):
            if function := self.knockCall(node):
                return function(node)
            for annotation, attribute in self.getAttributes(node):
                visited = self.visit(attribute)
                node.__setattr__(annotation, visited)
            return node

    def visitAST(self, node: kiwi.AST) -> List[Any]:
        result = list()
        for annotation, attribute in self.getAttributes(node):
            result.append(self.visit(attribute))
        return result

    # ANNOTATION STATEMENTS
    # =====================

    def Annotation(self, node: kiwi.Annotation):
        """
        This expression is always hided for compiler
        """
        type = self.visit(node.type)
        for target in node.targets:
            self.scope.write(target.value.dump(), type)
        return

    def Expression(self, node: kiwi.Expression):
        """
        I think it is one of the most useless nodes in AST
        """
        return self.visit(node.value)

    def Name(self, node: kiwi.Name):
        return self.scope.ref(node.value)

    def Attribute(self, node: kiwi.Attribute):
        return self.scope.ref(node.dump())

    # SCOPE STATEMENTS
    # ================

    def NamespaceDef(self, node: kiwi.NamespaceDef):
        self.scope.write(node.name)

        name = node.name
        self.scope.newNamedSpace(str(node.name))
        public = self.visit(node.body_public)
        default = self.visit(node.body_default)
        self.scope.enablePrivate()
        private = self.visit(node.body_private)
        self.scope.leaveSpace()
        return kiwi.NamespaceDef(name, private, public, default)

    def FuncDef(self, node: kiwi.FuncDef):
        self.scope.newLocalSpace()
        name = node.name
        parameters = self.visit(node.params)
        default = self.visit(node.default)
        returns = self.visit(node.returns)
        promiser = self.visit(node.promiser)
        body = self.visit(node.body)
        self.scope.leaveSpace()

        result = kiwi.FuncDef(name, parameters, default, returns, promiser, body)
        self.scope.write(name, result)
        return result

    def Parameter(self, node: kiwi.Parameter):
        type: std.KiwiType = self.visit(node.type)
        targets: List[kiwi.Reference] = list()
        for target in node.target:
            target = target.value.dump()
            self.scope.write(target, type)
            targets.append(self.scope.ref(target))
        return kiwi.Parameter(targets, type)

    def IfElse(self, node: kiwi.IfElse):
        self.scope.newLocalSpace()
        condition = self.visit(node.condition)
        then = self.visit(node.then)
        or_else = self.visit(node.or_else)
        self.scope.leaveSpace()
        return kiwi.IfElse(condition, then, or_else)

    def While(self, node: kiwi.While):
        self.scope.newLocalSpace()
        condition = self.visit(node.condition)
        body = self.visit(node.body)
        self.scope.leaveSpace()
        return kiwi.While(condition, body)


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

    def openModule(self, file: str, name: str = '__main__', debug=False) -> Optional[Module]:
        file = self.getFileDir(file)
        with open(file) as kiwiFile:
            ast: kiwi.Module = frontend.parse(
                        kiwiFile.read()
                    )
            if debug:
                print(f'AST:\n{frontend.dump(ast)}\n')
            libScope = dict()
            for alias in ast.imports:
                importScope = self.openModule(alias.directory, debug=debug).scope.globalScope
                if isinstance(alias.as_name, list):
                    fromAliases: List[kiwi.Alias] = alias.as_name
                    for fromAlias in fromAliases:
                        libScope[fromAlias.as_name] = importScope.get(fromAlias.directory)
                    continue
                libScope[alias.as_name] = importScope
            visitor = KiwiVisitor(libScope)
            visitor.visit(ast)
            return Module(name, ast, visitor.scope)

    def __init__(self, builder: Builder):
        self.builder = builder

    def build(self, debug: bool = False) -> Module:
        self.directories_init()
        module = self.openModule(
            self.builder.project['entry_file'], debug=debug
        )

        if debug:
            print(f'AST:\n{frontend.dump(module.AST)}\n')
            print(f'Scopes:\n{module.scope.dump()}\n')

        return module

    def directories_init(self):
        if self.builder.options is not None:
            if (include_directories := self.builder.options['include_directories']) is not None:
                self.include_directories.extend(map(pathlib.Path, include_directories))
