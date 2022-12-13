from __future__ import annotations

import LangCode

# Default libraries
# -----------------

...

# Custom libraries
# ----------------

from LangApi import *
from Kiwi.components.kiwiASO import Attr
from Kiwi.components.kiwiScope import CodeScope, NoCodeScope
import Kiwi.components.kiwiASO as kiwi


class Undefined(Formalizable):
    attr: Attr
    address: Attr

    def Formalize(self, attr: Attr) -> Undefined:
        assert isinstance(attr, Attr)
        self.address = attr
        self.attr = self.api.useLocalPrefix(attr)
        return self

    def AnnotationDeclare(self, parent: Variable, *args: Abstract):
        return self.api.analyzer.scope.write(
            self.address, parent.InitsType(self.attr, self.address, *args))


class Module(CodeScope, Abstract):
    attr: Attr
    address: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict(), name=self.api.config['entry_file'])

    def toPath(self, attribute: int = None) -> List[str]:
        name = convert_var_name(self.name)
        return [convert_var_name(self.api.config['project_name']), 'functions', f'{name}.mcfunction']


class IfElse(CodeScope, InitableType):
    if_attr: Attr
    else_attr: Attr
    predicate: Attr
    then: List[Abstract]
    or_else: List[Abstract]

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def InitsType(self, condition: kiwi.expression,
                  then: List[kiwi.statement], or_else: List[kiwi.statement]):
        self._set_files(3)

        self.if_attr = self.api.getIfEx()
        self.else_attr = self.api.getElseEx()
        self.predicate = self.api.getPredicateEx()

        condition = self.api.visit(
            self.api.analyzer.visit(condition)
        )
        assert isinstance(condition, LangCode.TransPredicate)

        self.api.analyzer.scope.newLocalSpace()
        self.api.enterScope(self, 0)
        then = self.api.analyzer.visit(then)
        self.api.leaveScope()
        self.api.analyzer.scope.leaveSpace()

        if or_else:
            self.api.analyzer.scope.newLocalSpace()
            self.api.enterScope(self, 1)
            or_else = self.api.analyzer.visit(or_else)
            self.api.leaveScope()
            self.api.analyzer.scope.leaveSpace()
        else:
            or_else = []

        return Construct(
            'Reference',
            self,
            [condition.transPredicate(), then, or_else],
            raw_args=True
        )

    def Reference(self, condition: NBTLiteral, then: List[Construct], or_else: List[Construct]):
        check = ...
        if or_else:
            check: LangCode.Score = self.api.LangCode.Score(self.api).InitsType(
                self.api.getCheckEx()
            ).Assign(self.api.LangCode.Number(self.api).Formalize("1"))

        self.api.enterScope(self, 2)
        self.api.system(RawJSON(
            condition
        ))
        self.api.leaveScope()

        self.api.system(Execute([
            StepIfPredicate(
                self.api.useDirPrefix(self.predicate, withFuse=True).toString()
            ),
            StepRun(
                FunctionDirectCall(
                    self.api.useDirPrefix(self.if_attr, withFuse=True).toString()
                )
            )
        ]))
        if or_else:
            self.api.system(Execute([
                StepIfScoreMatch(
                    check.attr.toString(), check.scoreboard.attr.toString(), '1'
                ),
                StepRun(
                    FunctionDirectCall(
                        self.api.useDirPrefix(self.else_attr, withFuse=True).toString()
                    )
                )
            ]))

            self.api.enterScope(self, 0)
            self.then = self.api.visit(then)
            check.Assign(self.api.LangCode.Number(self.api).Formalize("0"))
            self.api.leaveScope()

            self.api.enterScope(self, 1)
            self.or_else = self.api.visit(or_else)
            self.api.leaveScope()
        else:
            self.api.enterScope(self, 0)
            self.then = self.api.visit(then)
            self.api.leaveScope()
        return self

    def toPath(self, attribute: int = None) -> List[str]:
        match attribute:
            case 0:
                return [convert_var_name(self.api.config['project_name']),
                        'functions',
                        *Attr(map(convert_var_name, self.api.useDirPrefix(self.if_attr))).withPrefix('.mcfunction')]
            case 1:
                return [convert_var_name(self.api.config['project_name']),
                        'functions',
                        *Attr(map(convert_var_name, self.api.useDirPrefix(self.else_attr))).withPrefix('.mcfunction')]
            case 2:
                return [convert_var_name(self.api.config['project_name']),
                        'predicates',
                        *Attr(map(convert_var_name, self.api.useDirPrefix(self.predicate))).withPrefix('.json')]


class While(CodeScope, InitableType):
    body_attr: Attr
    predicate: Attr
    body: List[Abstract]

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def InitsType(self, condition: kiwi.expression,
                  body: List[kiwi.statement]):
        self._set_files(2)

        self.body_attr = self.api.getWhileEx()
        self.predicate = self.api.getPredicateEx()

        condition = self.api.visit(
            self.api.analyzer.visit(condition)
        )
        assert isinstance(condition, LangCode.TransPredicate)

        self.api.analyzer.scope.newLocalSpace()
        self.api.enterScope(self, 0)
        body = self.api.analyzer.visit(body)
        self.api.leaveScope()
        self.api.analyzer.scope.leaveSpace()

        return Construct(
            'Reference',
            self,
            [condition, body],
            raw_args=True
        )

    def Reference(self, condition: LangCode.AnyCompareObject, body: List[Construct]):
        # Predicate space
        # ---------------

        self.api.enterScope(self, 1)
        self.api.system(RawJSON(
            condition.predicate
        ))
        self.api.leaveScope()

        # Global space
        # ------------

        self.api.system(Execute([
            StepIfPredicate(
                self.api.useDirPrefix(self.predicate, withFuse=True).toString()
            ),
            StepRun(
                FunctionDirectCall(
                    self.api.useDirPrefix(self.body_attr, withFuse=True).toString()
                )
            )
        ]))

        # Body space
        # ----------

        self.api.enterScope(self, 0)
        self.body = self.api.visit(body)
        self.api.system(Execute([
            StepIfPredicate(
                self.api.useDirPrefix(self.predicate, withFuse=True).toString()
            ),
            StepRun(
                FunctionDirectCall(
                    self.api.useDirPrefix(self.body_attr, withFuse=True).toString()
                )
            )
        ]))
        self.api.leaveScope()

        return self

    def toPath(self, attribute: int = None) -> List[str]:
        match attribute:
            case 0:
                return [convert_var_name(self.api.config['project_name']),
                        'functions',
                        *Attr(map(convert_var_name, self.api.useDirPrefix(self.body_attr))).withPrefix('.mcfunction')]
            case 1:
                return [convert_var_name(self.api.config['project_name']),
                        'predicates',
                        *Attr(map(convert_var_name, self.api.useDirPrefix(self.predicate))).withPrefix('.json')]


class Function(CodeScope, InitableType, Callable):
    attr: Attr
    address: Attr
    params: List[Abstract]
    returns: Abstract

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def InitsType(self, attr: Attr, address: Attr, body: List[kiwi.statement],
                  params: List[kiwi.Parameter], returns: kiwi.ReturnParameter):
        assert isinstance(address, Attr)
        self.address = address
        self.attr = attr

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toName(), self, hideMode=True
        )
        self.api.enterScope(self)
        params = self.api.analyzer.visit(params)
        returns = self.api.analyzer.visit(returns)
        body = self.api.analyzer.visit(body)
        self.api.leaveScope()
        self.api.analyzer.scope.leaveSpace()

        return Construct(
            'Reference',
            self,
            [body, params, returns],
            raw_args=True
        )

    def Reference(self, body: Construct, params: Any, returns: Any):
        self.api.enterScope(self)
        self.params = self.api.visit(params)
        self.returns = self.api.visit(returns)
        self.api.visit(body)
        self.api.leaveScope()
        return self

    def Call(self, *args: Abstract):
        for param, arg in zip(self.params, args):
            self.api.visit(
                Construct(
                    'Assign',
                    param,
                    [arg]
                ))
        self.api.system(FunctionDirectCall(
            self.api.useDirPrefix(self.attr, withFuse=True).toString()
        ))
        return self.returns

    def Return(self, value: Abstract):
        self.api.visit(
            Construct(
                'Assign',
                self.returns,
                [value]
            )
        )

    def toPath(self, attribute: int = None) -> List[str]:
        return [convert_var_name(self.api.config['project_name']),
                'functions', *Attr(map(convert_var_name, self.api.useDirPrefix(self.attr))).withPrefix('.mcfunction')]


class Namespace(NoCodeScope, InitableType):
    attr: Attr
    address: Attr

    def __init__(self, apiObject: API):
        self.api = apiObject
        super().__init__(dict())

    def InitsType(self, attr: Attr, blocks: List[kiwi.PrivateBlock | kiwi.PublicBlock | kiwi.DefaultBlock]):
        assert isinstance(attr, Attr)
        self.address = attr
        self.attr = self.api.useLocalPrefix(attr)

        result = list()

        self.api.analyzer.scope.useCustomSpace(
            self.attr.toName(), self
        )
        self.api.enterScope(self)
        for block in blocks:
            if isinstance(block, kiwi.PrivateBlock):
                self.private_mode = True
            elif isinstance(block, kiwi.PublicBlock):
                self.private_mode = False
            else:
                self.private_mode = self.api.config['default_scope'] == 'private'
            result.append(self.api.analyzer.visit(block))
        self.api.leaveScope()
        self.api.analyzer.scope.leaveSpace()

        return Construct(
            'Reference',
            self,
            result,
            raw_args=True
        )

    def Reference(self, *blocks: kiwi.PrivateBlock | kiwi.PublicBlock | kiwi.DefaultBlock):
        self.api.enterScope(self)
        for block in blocks:
            self.api.visit(block.body)
        self.api.leaveScope()
        return self
