"""
This code is unlicensed
By ButterSus

Project compiler
"""

from __future__ import annotations

import json
from typing import Optional, Any, Callable, List, TYPE_CHECKING, Literal
from frontend.KiwiAnalyzer import ScopeSystem, Module
from pathlib import Path
import frontend.KiwiAST as kiwi

if TYPE_CHECKING:
    from build import Builder


class KiwiVisitor:
    scope: ScopeSystem
    compiler: KiwiCompiler

    def __init__(self, globalScope: ScopeSystem, compiler: KiwiCompiler):
        self.compiler = compiler
        self.scope = globalScope

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

    # SIMPLE STATEMENTS
    # =================

    def FuncDef(self, node: kiwi.FuncDef):

        return


class KiwiCompiler:
    builder: Builder

    # Build options
    # -------------

    project_name: str
    mc_version: str
    entry_function: str
    output_directory: str
    default_scope: Literal['private', 'public']

    # Path directories
    # ----------------

    dir_bin: Path
    dir_data: Path
    dir_project: Path
    dir_functions: Path

    def __init__(self, builder: Builder):
        self.builder = builder
        self.project_name = builder.project['project_name']
        self.mc_version = builder.project['mc_version']

        if builder.options is not None:
            self.entry_function = builder.options['entry_function'] \
                if 'entry_function' in builder.options.keys() else 'main'
            self.output_directory = builder.options['output_directory'] \
                if 'output_directory' in builder.options.keys() else 'bin'
            self.default_scope = builder.options['default_scope'] \
                if 'default_scope' in builder.options.keys() else 'public'

    def build(self, module: Module):

        # Folder initialization
        # ---------------------

        self.dir_bin = Path(self.output_directory)
        self.dir_bin.mkdir(exist_ok=True)

        self.dir_data = Path(self.output_directory) / 'data'
        self.dir_data.mkdir(exist_ok=True)

        self.dir_project = Path(self.dir_data) / self.project_name
        self.dir_project.mkdir(exist_ok=True)

        self.dir_functions = Path(self.dir_project) / 'functions'
        self.dir_functions.mkdir(exist_ok=True)

        # File initialization
        # -------------------

        with (self.dir_bin / 'pack.mcmeta').open('w+') as file:
            file.write(json.dumps({
                "pack": {
                    "pack_format": self.version_to_pack_format(self.mc_version),
                    "description": "pack"
                }
            }, indent=4))

        # Visitor compiler
        # ----------------

        visitor = KiwiVisitor(module.scope, self)
        visitor.visit(module.AST)

    def version_to_pack_format(self, version: str) -> int:
        return 3
