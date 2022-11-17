from __future__ import annotations

import frontend
from frontend import KiwiAST as kiwi
import pathlib
from typing import List, Set, Optional, Callable, TYPE_CHECKING
from frontend.KiwiAnalyzer.memory import KiwiAnnotations
import frontend.KiwiAnalyzer.objects as kiwiObject


kiwiAnnotations = KiwiAnnotations()


if TYPE_CHECKING:
    from main import Builder


Token: kiwi.Token | kiwi.AST | list


class KiwiVisitor:
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

    def visit(self, node: Token):
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

    def visitAST(self, node: kiwi.AST):
        result = list()
        for attribute in self.getAttributes(node):
            result.append(self.visit(attribute))
        return result

    # SIMPLE STATEMENTS
    # =================

    def Annotation(self, node: kiwi.Annotation):
        targets = self.visit(node.targets)
        type = self.visit(node.type)
        for target in targets:
            kiwiAnnotations.add(target, kiwiObject.Variable(type))

    # EXPRESSIONS
    # ===========

    def Expression(self, node: kiwi.Expression):
        if isinstance(node.value, kiwi.Name):
            return kiwiAnnotations.get(node.value)
        self.visitAST(node)


class KiwiAnalyzer:
    builder: Builder
    imported_files: Set[str] = set()
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

    def openModule(self, file: str) -> Optional[kiwi.Module]:
        file = self.getFileDir(file)
        if file in self.imported_files:
            return
        self.imported_files.add(file)
        with open(file) as kiwiFile:
            result: kiwi.Module = frontend.parse(
                        kiwiFile.read()
                    )
            KiwiVisitor().visit(result)
            alias: kiwi.Alias
            if result is not None:
                for alias in result.imports:
                    print(
                        frontend.dump(
                            self.openModule(
                                alias.name
                            )
                        )
                    )
            return result

    def __init__(self, builder: Builder):
        self.builder = builder
        self.directories_init()
        print(
            frontend.dump(
                self.openModule(
                    self.builder.project['entry_file']
                )
            )
        )
        print('\n')
        print(
            kiwiAnnotations.dump()
        )
        self.builder = builder

    def directories_init(self):
        if self.builder.options is not None:
            if (include_directories := self.builder.options['include_directories']) is not None:
                self.include_directories.extend(map(pathlib.Path, include_directories))
