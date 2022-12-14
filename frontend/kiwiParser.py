"""
This module represents the second step of compiler frontend.
It compiles lexer tokens into an Abstract Syntax Tree.
It can be used to preprocess some macros for example.
"""

from __future__ import annotations

# Default libraries
# -----------------

from typing import Any, Optional
from itertools import chain

# Custom libraries
# ----------------

from pegen.parser import memoize, memoize_left_rec, Parser
from pegen.tokenizer import Tokenizer
from typing import List as _List
import components.kiwiASO as kiwi


class AST:
    """
    This class represents the second step of compiler frontend.
    """

    parser: KiwiParser
    module: kiwi.Module

    def __init__(self, tokenizer: Tokenizer):
        self.parser = KiwiParser(tokenizer)
        self.module = self.parser.start()

    def eval(self, tokenizer: Tokenizer) -> kiwi.expression:
        return KiwiParser(tokenizer).expression()

    def exec(self, tokenizer: Tokenizer) -> _List[kiwi.statement]:
        return KiwiParser(tokenizer).start().body


#
# Keywords and soft keywords are listed at the end of the parser definition.
class KiwiParser(Parser):

    @memoize
    def start(self) -> Optional[kiwi . Module]:
        # start: import_stmts statements $ | import_stmts $ | statements $ | $
        mark = self._mark()
        if (
            (i := self.import_stmts())
            and
            (v := self.statements())
            and
            (_endmarker := self.expect('ENDMARKER'))
        ):
            return i [0] . start , v [- 1] . end , kiwi . Module ( i , v )
        self._reset(mark)
        if (
            (i := self.import_stmts())
            and
            (_endmarker := self.expect('ENDMARKER'))
        ):
            return kiwi . Module ( i [0] . start , i [- 1] . end , i , [] )
        self._reset(mark)
        if (
            (v := self.statements())
            and
            (_endmarker := self.expect('ENDMARKER'))
        ):
            return kiwi . Module ( v [0] . start , v [- 1] . end , [] , v )
        self._reset(mark)
        if (
            (_endmarker := self.expect('ENDMARKER'))
        ):
            return kiwi . Module ( ... , ... , [] , [] )
        self._reset(mark)
        return None

    @memoize
    def import_stmts(self) -> Optional[Any]:
        # import_stmts: ((import_stmt | from_import_stmt))+
        mark = self._mark()
        if (
            (v := self._loop1_1())
        ):
            return list ( chain . from_iterable ( v ) )
        self._reset(mark)
        return None

    @memoize
    def import_stmt(self) -> Optional[Any]:
        # import_stmt: 'import' &&(dotted_as_names) ((NEWLINE | ';'))+
        mark = self._mark()
        if (
            (literal := self.expect('import'))
            and
            (forced := self.expect_forced(self.dotted_as_names(), '''(dotted_as_names)'''))
            and
            (_loop1_2 := self._loop1_2())
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def from_import_stmt(self) -> Optional[Any]:
        # from_import_stmt: "from" dotted_name import_stmt
        mark = self._mark()
        if (
            (s := self.expect("from"))
            and
            (v := self.dotted_name())
            and
            (a := self.import_stmt())
        ):
            return [s . start , a [- 1] . end , kiwi . Alias ( '' . join ( v ) , a )]
        self._reset(mark)
        return None

    @memoize
    def dotted_as_names(self) -> Optional[Any]:
        # dotted_as_names: ','.dotted_as_name+
        mark = self._mark()
        if (
            (_gather_3 := self._gather_3())
        ):
            return _gather_3
        self._reset(mark)
        return None

    @memoize
    def dotted_as_name(self) -> Optional[Any]:
        # dotted_as_name: dotted_name "as" &&(NAME_) | dotted_name
        mark = self._mark()
        if (
            (v := self.dotted_name())
            and
            (literal := self.expect("as"))
            and
            (forced := self.expect_forced(self.NAME_(), '''(NAME_)'''))
        ):
            return kiwi . Alias ( v [0] . start , a . end , '' . join ( v ) , a )
        self._reset(mark)
        if (
            (v := self.dotted_name())
        ):
            return kiwi . Alias ( v [0] . start , v [- 1] . end , '' . join ( v ) , v [- 1] )
        self._reset(mark)
        return None

    @memoize_left_rec
    def dotted_name(self) -> Optional[Any]:
        # dotted_name: dotted_name '.' &&(NAME_) | NAME_
        mark = self._mark()
        if (
            (v := self.dotted_name())
            and
            (literal := self.expect('.'))
            and
            (forced := self.expect_forced(self.NAME_(), '''(NAME_)'''))
        ):
            return [* v , a]
        self._reset(mark)
        if (
            (v := self.NAME_())
        ):
            return [v]
        self._reset(mark)
        return None

    @memoize
    def statements(self) -> Optional[Any]:
        # statements: statement+
        mark = self._mark()
        if (
            (_loop1_5 := self._loop1_5())
        ):
            return _loop1_5
        self._reset(mark)
        return None

    @memoize
    def statement(self) -> Optional[Any]:
        # statement: simple_stmt ((NEWLINE | ';'))+ | compound_stmt
        mark = self._mark()
        if (
            (v := self.simple_stmt())
            and
            (_loop1_6 := self._loop1_6())
        ):
            return v
        self._reset(mark)
        if (
            (v := self.compound_stmt())
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def statement_newline(self) -> Optional[Any]:
        # statement_newline: simple_stmt (NEWLINE)+
        mark = self._mark()
        if (
            (v := self.simple_stmt())
            and
            (_loop1_7 := self._loop1_7())
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def simple_stmt(self) -> Optional[Any]:
        # simple_stmt: assignment | expression | return_stmt | 'pass' | 'break' | 'continue'
        mark = self._mark()
        if (
            (assignment := self.assignment())
        ):
            return assignment
        self._reset(mark)
        if (
            (expression := self.expression())
        ):
            return expression
        self._reset(mark)
        if (
            (return_stmt := self.return_stmt())
        ):
            return return_stmt
        self._reset(mark)
        if (
            (s := self.expect('pass'))
        ):
            return kiwi . Pass ( s . start , s . end )
        self._reset(mark)
        if (
            (s := self.expect('break'))
        ):
            return kiwi . Break ( s . start , s . end )
        self._reset(mark)
        if (
            (s := self.expect('continue'))
        ):
            return kiwi . Continue ( s . start , s . end )
        self._reset(mark)
        return None

    @memoize
    def compound_stmt(self) -> Optional[Any]:
        # compound_stmt: function_def | namespace_def | if_stmt | for_classic_stmt | for_iterator_stmt | while_stmt | match_stmt
        mark = self._mark()
        if (
            (function_def := self.function_def())
        ):
            return function_def
        self._reset(mark)
        if (
            (namespace_def := self.namespace_def())
        ):
            return namespace_def
        self._reset(mark)
        if (
            (if_stmt := self.if_stmt())
        ):
            return if_stmt
        self._reset(mark)
        if (
            (for_classic_stmt := self.for_classic_stmt())
        ):
            return for_classic_stmt
        self._reset(mark)
        if (
            (for_iterator_stmt := self.for_iterator_stmt())
        ):
            return for_iterator_stmt
        self._reset(mark)
        if (
            (while_stmt := self.while_stmt())
        ):
            return while_stmt
        self._reset(mark)
        if (
            (match_stmt := self.match_stmt())
        ):
            return match_stmt
        self._reset(mark)
        return None

    @memoize
    def assignment(self) -> Optional[Any]:
        # assignment: annotations '=' &&(','.expression+) | ','.expression+ '=' &&(','.expression+) | ','.expression+ augassign &&(','.expression+) | annotations
        mark = self._mark()
        if (
            (a := self.annotations())
            and
            (literal := self.expect('='))
            and
            (forced := self.expect_forced(self._gather_8(), '''(','.expression+)'''))
        ):
            return kiwi . AnnAssignment ( a [0] [0] . start , v [- 1] . end , * a , v )
        self._reset(mark)
        if (
            (i := self._gather_10())
            and
            (literal := self.expect('='))
            and
            (forced := self.expect_forced(self._gather_12(), '''(','.expression+)'''))
        ):
            return kiwi . Assignment ( i [0] . start , v [- 1] . end , i , v )
        self._reset(mark)
        if (
            (i := self._gather_14())
            and
            (o := self.augassign())
            and
            (forced := self.expect_forced(self._gather_16(), '''(','.expression+)'''))
        ):
            return kiwi . AugAssignment ( i [0] . start , v [- 1] . end , i , o , v )
        self._reset(mark)
        if (
            (a := self.annotations())
        ):
            return kiwi . Annotation ( a [0] [0] . start , a [2] [- 1] . end if a [2] else a [1] . end , * a )
        self._reset(mark)
        return None

    @memoize
    def annotations(self) -> Optional[Any]:
        # annotations: expression ':' &&(expression+) | ','.expression+ '->' &&(expression+)
        mark = self._mark()
        if (
            (i := self.expression())
            and
            (literal := self.expect(':'))
            and
            (forced := self.expect_forced(self._loop1_18(), '''(expression+)'''))
        ):
            return [i] , a [0] , a [1 :]
        self._reset(mark)
        if (
            (i := self._gather_19())
            and
            (literal := self.expect('->'))
            and
            (forced := self.expect_forced(self._loop1_21(), '''(expression+)'''))
        ):
            return i , a [0] , a [1 :]
        self._reset(mark)
        return None

    @memoize
    def augassign(self) -> Optional[Any]:
        # augassign: '+=' | '-=' | '*=' | '/=' | '%='
        mark = self._mark()
        if (
            (s := self.expect('+='))
        ):
            return kiwi . Token ( s . start , s . end , '+=' )
        self._reset(mark)
        if (
            (s := self.expect('-='))
        ):
            return kiwi . Token ( s . start , s . end , '-=' )
        self._reset(mark)
        if (
            (s := self.expect('*='))
        ):
            return kiwi . Token ( s . start , s . end , '*=' )
        self._reset(mark)
        if (
            (s := self.expect('/='))
        ):
            return kiwi . Token ( s . start , s . end , '/=' )
        self._reset(mark)
        if (
            (s := self.expect('%='))
        ):
            return kiwi . Token ( s . start , s . end , '%=' )
        self._reset(mark)
        return None

    @memoize
    def return_stmt(self) -> Optional[Any]:
        # return_stmt: 'return' expression | 'return'
        mark = self._mark()
        if (
            (s := self.expect('return'))
            and
            (v := self.expression())
        ):
            return kiwi . Return ( s . start , v . end , v )
        self._reset(mark)
        if (
            (s := self.expect('return'))
        ):
            return kiwi . Return ( s . start , s . end , None )
        self._reset(mark)
        return None

    @memoize
    def block(self) -> Optional[Any]:
        # block: NEWLINE INDENT statements DEDENT NEWLINE | statement_newline
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (v := self.statements())
            and
            (_dedent := self.expect('DEDENT'))
            and
            (_newline_1 := self.expect('NEWLINE'))
        ):
            return v
        self._reset(mark)
        if (
            (v := self.statement_newline())
        ):
            return [v]
        self._reset(mark)
        return None

    @memoize
    def hiding_block(self) -> Optional[Any]:
        # hiding_block: NEWLINE INDENT blocks DEDENT NEWLINE
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (v := self.blocks())
            and
            (_dedent := self.expect('DEDENT'))
            and
            (_newline_1 := self.expect('NEWLINE'))
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def blocks(self) -> Optional[Any]:
        # blocks: ((private_block | public_block | default_block))+
        mark = self._mark()
        if (
            (_loop1_22 := self._loop1_22())
        ):
            return _loop1_22
        self._reset(mark)
        return None

    @memoize
    def private_block(self) -> Optional[Any]:
        # private_block: 'private' &&(':' block)
        mark = self._mark()
        if (
            (s := self.expect('private'))
            and
            (forced := self.expect_forced(self._tmp_23(), '''(':' block)'''))
        ):
            return kiwi . PrivateBlock ( s . start , v [- 1] . end , v )
        self._reset(mark)
        return None

    @memoize
    def public_block(self) -> Optional[Any]:
        # public_block: 'public' &&(':' block)
        mark = self._mark()
        if (
            (s := self.expect('public'))
            and
            (forced := self.expect_forced(self._tmp_24(), '''(':' block)'''))
        ):
            return kiwi . PublicBlock ( s . start , v [- 1] . end , v )
        self._reset(mark)
        return None

    @memoize
    def default_block(self) -> Optional[Any]:
        # default_block: statements
        mark = self._mark()
        if (
            (v := self.statements())
        ):
            return kiwi . DefaultBlock ( v [0] . start , v [- 1] . end , v )
        self._reset(mark)
        return None

    @memoize
    def namespace_def(self) -> Optional[Any]:
        # namespace_def: 'namespace' &&(NAME_) &&(':' hiding_block)
        mark = self._mark()
        if (
            (s := self.expect('namespace'))
            and
            (forced := self.expect_forced(self.NAME_(), '''(NAME_)'''))
            and
            (forced_1 := self.expect_forced(self._tmp_25(), '''(':' hiding_block)'''))
        ):
            return kiwi . NamespaceDef ( s . start , b [- 1] . end , i , b )
        self._reset(mark)
        return None

    @memoize
    def function_def(self) -> Optional[Any]:
        # function_def: 'function' (&&(NAME_)) &&'(' parameters &&')' '->' (&&(return_param)) '<' '-' (&&(expression)) &&':' (&&(block)) | 'function' NAME_ '(' parameters ')' '<' '-' (&&(expression)) &&':' (&&(block)) | 'function' NAME_ '(' parameters ')' '->' (&&(return_param)) &&':' (&&(block)) | 'function' NAME_ '(' parameters ')' &&':' (&&(block))
        mark = self._mark()
        if (
            (s := self.expect('function'))
            and
            (i := self.expect_forced(self.NAME_(), '''(NAME_)'''))
            and
            (forced := self.expect_forced(self.expect('('), "'('"))
            and
            (p := self.parameters())
            and
            (forced_1 := self.expect_forced(self.expect(')'), "')'"))
            and
            (literal := self.expect('->'))
            and
            (r := self.expect_forced(self.return_param(), '''(return_param)'''))
            and
            (literal_1 := self.expect('<'))
            and
            (literal_2 := self.expect('-'))
            and
            (pr := self.expect_forced(self.expression(), '''(expression)'''))
            and
            (forced_2 := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.expect_forced(self.block(), '''(block)'''))
        ):
            return kiwi . FuncDef ( s . start , b [- 1] . end , i , p [0] , p [1] , r , pr , b )
        self._reset(mark)
        if (
            (s := self.expect('function'))
            and
            (i := self.NAME_())
            and
            (literal := self.expect('('))
            and
            (p := self.parameters())
            and
            (literal_1 := self.expect(')'))
            and
            (literal_2 := self.expect('<'))
            and
            (literal_3 := self.expect('-'))
            and
            (pr := self.expect_forced(self.expression(), '''(expression)'''))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.expect_forced(self.block(), '''(block)'''))
        ):
            return kiwi . FuncDef ( s . start , b [- 1] . end , i , p [0] , p [1] , None , pr , b )
        self._reset(mark)
        if (
            (s := self.expect('function'))
            and
            (i := self.NAME_())
            and
            (literal := self.expect('('))
            and
            (p := self.parameters())
            and
            (literal_1 := self.expect(')'))
            and
            (literal_2 := self.expect('->'))
            and
            (r := self.expect_forced(self.return_param(), '''(return_param)'''))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.expect_forced(self.block(), '''(block)'''))
        ):
            return kiwi . FuncDef ( s . start , b [- 1] . end , i , p [0] , p [1] , r , None , b )
        self._reset(mark)
        if (
            (s := self.expect('function'))
            and
            (i := self.NAME_())
            and
            (literal := self.expect('('))
            and
            (p := self.parameters())
            and
            (literal_1 := self.expect(')'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.expect_forced(self.block(), '''(block)'''))
        ):
            return kiwi . FuncDef ( s . start , b [- 1] . end , i , p [0] , p [1] , None , None , b )
        self._reset(mark)
        return None

    @memoize
    def parameters(self) -> Optional[Any]:
        # parameters: param_no_default* param_with_default*
        # nullable=True
        mark = self._mark()
        if (
            (p := self._loop0_26(),)
            and
            (d := self._loop0_27(),)
        ):
            return [* p , * map ( lambda x : x [0] , d )] , list ( map ( lambda x : x [1] , d ) )
        self._reset(mark)
        return None

    @memoize
    def param_no_default(self) -> Optional[Any]:
        # param_no_default: annotations ',' | annotations &')' | '=' NAME_ ',' | '=' NAME_ &')'
        mark = self._mark()
        if (
            (v := self.annotations())
            and
            (literal := self.expect(','))
        ):
            return kiwi . Parameter ( v [0] [0] . start , v [2] [- 1] . end if v [- 1] else v [1] . end , v [0] , v [1] , v [2] )
        self._reset(mark)
        if (
            (v := self.annotations())
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return kiwi . Parameter ( v [0] [0] . start , v [2] [- 1] . end if v [- 1] else v [1] . end , v [0] , v [1] , v [2] )
        self._reset(mark)
        if (
            (s := self.expect('='))
            and
            (i := self.NAME_())
            and
            (literal := self.expect(','))
        ):
            return kiwi . RefParameter ( s . start , i . end , i )
        self._reset(mark)
        if (
            (s := self.expect('='))
            and
            (i := self.NAME_())
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return kiwi . RefParameter ( s . start , i . end , i )
        self._reset(mark)
        return None

    @memoize
    def param_with_default(self) -> Optional[Any]:
        # param_with_default: annotations '=' expression ',' | annotations '=' expression &')' | '=' NAME_ '=' expression ',' | '=' NAME_ '=' expression &')'
        mark = self._mark()
        if (
            (a := self.annotations())
            and
            (literal := self.expect('='))
            and
            (v := self.expression())
            and
            (e := self.expect(','))
        ):
            return kiwi . Parameter ( a [0] [0] . start , v . end , a [0] , a [1] , a [2] ) , v
        self._reset(mark)
        if (
            (a := self.annotations())
            and
            (literal := self.expect('='))
            and
            (v := self.expression())
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return kiwi . Parameter ( a [0] [0] . start , v . end , a [0] , a [1] , a [2] ) , v
        self._reset(mark)
        if (
            (s := self.expect('='))
            and
            (i := self.NAME_())
            and
            (literal := self.expect('='))
            and
            (v := self.expression())
            and
            (literal_1 := self.expect(','))
        ):
            return kiwi . RefParameter ( s . start , v . end , i ) , v
        self._reset(mark)
        if (
            (s := self.expect('='))
            and
            (i := self.NAME_())
            and
            (literal := self.expect('='))
            and
            (v := self.expression())
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return kiwi . RefParameter ( s . start , v . end , i ) , v
        self._reset(mark)
        return None

    @memoize
    def return_param(self) -> Optional[Any]:
        # return_param: expression expression* | '=' NAME_
        mark = self._mark()
        if (
            (s := self.expression())
            and
            (a := self._loop0_28(),)
        ):
            return kiwi . ReturnParameter ( s . start , a [- 1] . end if a else s . end , s , a )
        self._reset(mark)
        if (
            (s := self.expect('='))
            and
            (i := self.NAME_())
        ):
            return kiwi . ReturnRefParameter ( s . start , i . end , i )
        self._reset(mark)
        return None

    @memoize
    def if_stmt(self) -> Optional[Any]:
        # if_stmt: 'if' expression ':' block 'else' if_stmt | 'if' expression ':' block 'else' ':' block | 'if' expression ':' block
        mark = self._mark()
        if (
            (s := self.expect('if'))
            and
            (c := self.expression())
            and
            (literal := self.expect(':'))
            and
            (t := self.block())
            and
            (literal_1 := self.expect('else'))
            and
            (e := self.if_stmt())
        ):
            return kiwi . IfElse ( s . start , e . end , c , t , e )
        self._reset(mark)
        if (
            (s := self.expect('if'))
            and
            (c := self.expression())
            and
            (literal := self.expect(':'))
            and
            (t := self.block())
            and
            (literal_1 := self.expect('else'))
            and
            (literal_2 := self.expect(':'))
            and
            (e := self.block())
        ):
            return kiwi . IfElse ( s . start , e [- 1] . end , c , t , e )
        self._reset(mark)
        if (
            (s := self.expect('if'))
            and
            (c := self.expression())
            and
            (literal := self.expect(':'))
            and
            (t := self.block())
        ):
            return kiwi . IfElse ( s . start , t [- 1] . end , c , t , [] )
        self._reset(mark)
        return None

    @memoize
    def for_classic_stmt(self) -> Optional[Any]:
        # for_classic_stmt: 'for' simple_stmt ';' expression ';' simple_stmt ':' block
        mark = self._mark()
        if (
            (s := self.expect('for'))
            and
            (a := self.simple_stmt())
            and
            (literal := self.expect(';'))
            and
            (b := self.expression())
            and
            (literal_1 := self.expect(';'))
            and
            (c := self.simple_stmt())
            and
            (literal_2 := self.expect(':'))
            and
            (e := self.block())
        ):
            return kiwi . ForClassic ( s . start , e [- 1] . end , a , b , c , e )
        self._reset(mark)
        return None

    @memoize
    def for_iterator_stmt(self) -> Optional[Any]:
        # for_iterator_stmt: 'for' for_iterator_param 'in' expression ':' block
        mark = self._mark()
        if (
            (s := self.expect('for'))
            and
            (t := self.for_iterator_param())
            and
            (literal := self.expect('in'))
            and
            (i := self.expression())
            and
            (literal_1 := self.expect(':'))
            and
            (e := self.block())
        ):
            return kiwi . ForIterator ( s . start , e [- 1] . end , * t , i , e )
        self._reset(mark)
        return None

    @memoize
    def for_iterator_param(self) -> Optional[Any]:
        # for_iterator_param: expression ':' expression expression+ | expression ':' expression
        mark = self._mark()
        if (
            (t := self.expression())
            and
            (literal := self.expect(':'))
            and
            (p := self.expression())
            and
            (a := self._loop1_29())
        ):
            return [t] , p , a
        self._reset(mark)
        if (
            (t := self.expression())
            and
            (literal := self.expect(':'))
            and
            (p := self.expression())
        ):
            return [t] , p , []
        self._reset(mark)
        return None

    @memoize
    def while_stmt(self) -> Optional[Any]:
        # while_stmt: 'while' expression ':' block
        mark = self._mark()
        if (
            (s := self.expect('while'))
            and
            (c := self.expression())
            and
            (literal := self.expect(':'))
            and
            (b := self.block())
        ):
            return kiwi . While ( s . start , b [- 1] . end , c , b )
        self._reset(mark)
        return None

    @memoize
    def match_stmt(self) -> Optional[Any]:
        # match_stmt: "match" expression ':' case_block
        mark = self._mark()
        if (
            (s := self.expect("match"))
            and
            (v := self.expression())
            and
            (literal := self.expect(':'))
            and
            (c := self.case_block())
        ):
            return kiwi . MatchCase ( s . start , c [- 1] . end , v , c )
        self._reset(mark)
        return None

    @memoize
    def case_block(self) -> Optional[Any]:
        # case_block: NEWLINE INDENT cases DEDENT NEWLINE
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (v := self.cases())
            and
            (_dedent := self.expect('DEDENT'))
            and
            (_newline_1 := self.expect('NEWLINE'))
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def cases(self) -> Optional[Any]:
        # cases: (',' NEWLINE*).case+
        mark = self._mark()
        if (
            (_gather_30 := self._gather_30())
        ):
            return _gather_30
        self._reset(mark)
        return None

    @memoize
    def case(self) -> Optional[Any]:
        # case: "case" expression ':' block
        mark = self._mark()
        if (
            (s := self.expect("case"))
            and
            (k := self.expression())
            and
            (literal := self.expect(':'))
            and
            (b := self.block())
        ):
            return kiwi . Case ( s . start , b [- 1] . end , k , b )
        self._reset(mark)
        return None

    @memoize
    def expression(self) -> Optional[Any]:
        # expression: lambda_def | disjunctions '?' disjunctions ':' disjunctions | disjunctions
        mark = self._mark()
        if (
            (lambda_def := self.lambda_def())
        ):
            return lambda_def
        self._reset(mark)
        if (
            (c := self.disjunctions())
            and
            (literal := self.expect('?'))
            and
            (t := self.disjunctions())
            and
            (literal_1 := self.expect(':'))
            and
            (e := self.disjunctions())
        ):
            return kiwi . IfExpression ( c . start , e . end , c , t , e )
        self._reset(mark)
        if (
            (v := self.disjunctions())
        ):
            return kiwi . Expression ( v . start , v . end , v )
        self._reset(mark)
        return None

    @memoize
    def lambda_def(self) -> Optional[Any]:
        # lambda_def: "lambda" lambda_parameters ':' expression
        mark = self._mark()
        if (
            (s := self.expect("lambda"))
            and
            (p := self.lambda_parameters())
            and
            (literal := self.expect(':'))
            and
            (r := self.expression())
        ):
            return kiwi . LambdaDef ( s . start , r . end , p , r )
        self._reset(mark)
        return None

    @memoize
    def lambda_parameters(self) -> Optional[Any]:
        # lambda_parameters: ','.lambda_param+ | lambda_param?
        # nullable=True
        mark = self._mark()
        if (
            (v := self._gather_32())
        ):
            return v
        self._reset(mark)
        if (
            (opt := self.lambda_param(),)
        ):
            return []
        self._reset(mark)
        return None

    @memoize
    def lambda_param(self) -> Optional[Any]:
        # lambda_param: NAME_
        mark = self._mark()
        if (
            (v := self.NAME_())
        ):
            return kiwi . LambdaParameter ( v . start , v . end , v )
        self._reset(mark)
        return None

    @memoize
    def disjunctions(self) -> Optional[Any]:
        # disjunctions: conjunctions disjunction+ | conjunctions
        mark = self._mark()
        if (
            (s := self.conjunctions())
            and
            (a := self._loop1_34())
        ):
            return kiwi . Disjunctions ( s . start , a [- 1] . end , [s , * a] )
        self._reset(mark)
        if (
            (conjunctions := self.conjunctions())
        ):
            return conjunctions
        self._reset(mark)
        return None

    @memoize
    def disjunction(self) -> Optional[Any]:
        # disjunction: 'or' conjunctions
        mark = self._mark()
        if (
            (literal := self.expect('or'))
            and
            (v := self.conjunctions())
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def conjunctions(self) -> Optional[Any]:
        # conjunctions: inversion conjunction+ | inversion
        mark = self._mark()
        if (
            (s := self.inversion())
            and
            (a := self._loop1_35())
        ):
            return kiwi . Conjunctions ( s . start , a [- 1] . end , [s , * a] )
        self._reset(mark)
        if (
            (inversion := self.inversion())
        ):
            return inversion
        self._reset(mark)
        return None

    @memoize
    def conjunction(self) -> Optional[Any]:
        # conjunction: 'and' inversion
        mark = self._mark()
        if (
            (literal := self.expect('and'))
            and
            (v := self.inversion())
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def inversion(self) -> Optional[Any]:
        # inversion: 'not' inversion | comparisons
        mark = self._mark()
        if (
            (s := self.expect('not'))
            and
            (x := self.inversion())
        ):
            return kiwi . UnaryOp ( s . start , x . end , x , 'not' )
        self._reset(mark)
        if (
            (comparisons := self.comparisons())
        ):
            return comparisons
        self._reset(mark)
        return None

    @memoize
    def comparisons(self) -> Optional[Any]:
        # comparisons: range compare_op_sum_pair+ | range
        mark = self._mark()
        if (
            (f := self.range())
            and
            (v := self._loop1_36())
        ):
            return kiwi . Comparisons ( f . start , v [- 1] [1] . end , [f , * list ( map ( lambda x : x [1] , v ) )] , list ( map ( lambda x : x [0] , v ) ) )
        self._reset(mark)
        if (
            (range := self.range())
        ):
            return range
        self._reset(mark)
        return None

    @memoize
    def compare_op_sum_pair(self) -> Optional[Any]:
        # compare_op_sum_pair: eq_sum | noteq_sum | lte_sum | lt_sum | gte_sum | gt_sum
        mark = self._mark()
        if (
            (eq_sum := self.eq_sum())
        ):
            return eq_sum
        self._reset(mark)
        if (
            (noteq_sum := self.noteq_sum())
        ):
            return noteq_sum
        self._reset(mark)
        if (
            (lte_sum := self.lte_sum())
        ):
            return lte_sum
        self._reset(mark)
        if (
            (lt_sum := self.lt_sum())
        ):
            return lt_sum
        self._reset(mark)
        if (
            (gte_sum := self.gte_sum())
        ):
            return gte_sum
        self._reset(mark)
        if (
            (gt_sum := self.gt_sum())
        ):
            return gt_sum
        self._reset(mark)
        return None

    @memoize
    def eq_sum(self) -> Optional[Any]:
        # eq_sum: '==' range
        mark = self._mark()
        if (
            (s := self.expect('=='))
            and
            (v := self.range())
        ):
            return kiwi . Token ( s . start , s . end , '==' ) , v
        self._reset(mark)
        return None

    @memoize
    def noteq_sum(self) -> Optional[Any]:
        # noteq_sum: '!=' range
        mark = self._mark()
        if (
            (s := self.expect('!='))
            and
            (v := self.range())
        ):
            return kiwi . Token ( s . start , s . end , '!=' ) , v
        self._reset(mark)
        return None

    @memoize
    def lte_sum(self) -> Optional[Any]:
        # lte_sum: '<=' range
        mark = self._mark()
        if (
            (s := self.expect('<='))
            and
            (v := self.range())
        ):
            return kiwi . Token ( s . start , s . end , '<=' ) , v
        self._reset(mark)
        return None

    @memoize
    def lt_sum(self) -> Optional[Any]:
        # lt_sum: '<' range
        mark = self._mark()
        if (
            (s := self.expect('<'))
            and
            (v := self.range())
        ):
            return kiwi . Token ( s . start , s . end , '<' ) , v
        self._reset(mark)
        return None

    @memoize
    def gte_sum(self) -> Optional[Any]:
        # gte_sum: '>=' range
        mark = self._mark()
        if (
            (s := self.expect('>='))
            and
            (v := self.range())
        ):
            return kiwi . Token ( s . start , s . end , '>=' ) , v
        self._reset(mark)
        return None

    @memoize
    def gt_sum(self) -> Optional[Any]:
        # gt_sum: '>' range
        mark = self._mark()
        if (
            (s := self.expect('>'))
            and
            (v := self.range())
        ):
            return kiwi . Token ( s . start , s . end , '>' ) , v
        self._reset(mark)
        return None

    @memoize
    def range(self) -> Optional[Any]:
        # range: sum '.' '.' sum | sum
        mark = self._mark()
        if (
            (x := self.sum())
            and
            (literal := self.expect('.'))
            and
            (literal_1 := self.expect('.'))
            and
            (y := self.sum())
        ):
            return kiwi . Range ( x . start , y . end , x , y )
        self._reset(mark)
        if (
            (sum := self.sum())
        ):
            return sum
        self._reset(mark)
        return None

    @memoize_left_rec
    def sum(self) -> Optional[Any]:
        # sum: sum '+' term | sum '-' term | term
        mark = self._mark()
        if (
            (x := self.sum())
            and
            (s := self.expect('+'))
            and
            (y := self.term())
        ):
            return kiwi . BinaryOp ( x . start , y . end , x , y , kiwi . Token ( s . start , s . end , '+' ) )
        self._reset(mark)
        if (
            (x := self.sum())
            and
            (s := self.expect('-'))
            and
            (y := self.term())
        ):
            return kiwi . BinaryOp ( x . start , y . end , x , y , kiwi . Token ( s . start , s . end , '-' ) )
        self._reset(mark)
        if (
            (term := self.term())
        ):
            return term
        self._reset(mark)
        return None

    @memoize_left_rec
    def term(self) -> Optional[Any]:
        # term: term '*' factor | term '/' factor | term '%' factor | factor
        mark = self._mark()
        if (
            (x := self.term())
            and
            (s := self.expect('*'))
            and
            (y := self.factor())
        ):
            return kiwi . BinaryOp ( x . start , y . end , x , y , kiwi . Token ( s . start , s . end , '*' ) )
        self._reset(mark)
        if (
            (x := self.term())
            and
            (s := self.expect('/'))
            and
            (y := self.factor())
        ):
            return kiwi . BinaryOp ( x . start , y . end , x , y , kiwi . Token ( s . start , s . end , '/' ) )
        self._reset(mark)
        if (
            (x := self.term())
            and
            (s := self.expect('%'))
            and
            (y := self.factor())
        ):
            return kiwi . BinaryOp ( x . start , y . end , x , y , kiwi . Token ( s . start , s . end , '%' ) )
        self._reset(mark)
        if (
            (factor := self.factor())
        ):
            return factor
        self._reset(mark)
        return None

    @memoize
    def factor(self) -> Optional[Any]:
        # factor: '+' factor | '-' factor | power
        mark = self._mark()
        if (
            (s := self.expect('+'))
            and
            (x := self.factor())
        ):
            return kiwi . UnaryOp ( s . start , x . end , x , kiwi . Token ( s . start , s . end , '+' ) )
        self._reset(mark)
        if (
            (s := self.expect('-'))
            and
            (x := self.factor())
        ):
            return kiwi . UnaryOp ( s . start , x . end , x , kiwi . Token ( s . start , s . end , '-' ) )
        self._reset(mark)
        if (
            (power := self.power())
        ):
            return power
        self._reset(mark)
        return None

    @memoize
    def power(self) -> Optional[Any]:
        # power: primary '**' factor | primary
        mark = self._mark()
        if (
            (x := self.primary())
            and
            (s := self.expect('**'))
            and
            (y := self.factor())
        ):
            return kiwi . BinaryOp ( x . start , y . end , x , y , kiwi . Token ( s . start , s . end , '**' ) )
        self._reset(mark)
        if (
            (primary := self.primary())
        ):
            return primary
        self._reset(mark)
        return None

    @memoize_left_rec
    def primary(self) -> Optional[Any]:
        # primary: "match" expression ':' key_block | primary '.' NAME_ | primary '(' arguments ')' | primary '(' ')' | atom
        mark = self._mark()
        if (
            (s := self.expect("match"))
            and
            (k := self.expression())
            and
            (literal := self.expect(':'))
            and
            (c := self.key_block())
        ):
            return kiwi . MatchExpr ( s . start , c [- 1] . end , k , c )
        self._reset(mark)
        if (
            (v := self.primary())
            and
            (literal := self.expect('.'))
            and
            (a := self.NAME_())
        ):
            return kiwi . Attribute ( v . start , a . end , v , a )
        self._reset(mark)
        if (
            (i := self.primary())
            and
            (literal := self.expect('('))
            and
            (v := self.arguments())
            and
            (e := self.expect(')'))
        ):
            return kiwi . Call ( i . start , e . end , i , v )
        self._reset(mark)
        if (
            (i := self.primary())
            and
            (literal := self.expect('('))
            and
            (e := self.expect(')'))
        ):
            return kiwi . Call ( i . start , e . end , i , [] )
        self._reset(mark)
        if (
            (atom := self.atom())
        ):
            return atom
        self._reset(mark)
        return None

    @memoize
    def atom(self) -> Optional[Any]:
        # atom: NAME_ | 'true' | 'false' | 'none' | 'promise' | selector | STRING_ | NUMBER_ | group
        mark = self._mark()
        if (
            (NAME_ := self.NAME_())
        ):
            return NAME_
        self._reset(mark)
        if (
            (s := self.expect('true'))
        ):
            return kiwi . Token ( s . start , s . end , 'true' )
        self._reset(mark)
        if (
            (s := self.expect('false'))
        ):
            return kiwi . Token ( s . start , s . end , 'false' )
        self._reset(mark)
        if (
            (s := self.expect('none'))
        ):
            return kiwi . Token ( s . start , s . end , 'none' )
        self._reset(mark)
        if (
            (s := self.expect('promise'))
        ):
            return kiwi . Token ( s . start , s . end , 'promise' )
        self._reset(mark)
        if (
            (selector := self.selector())
        ):
            return selector
        self._reset(mark)
        if (
            (STRING_ := self.STRING_())
        ):
            return STRING_
        self._reset(mark)
        if (
            (NUMBER_ := self.NUMBER_())
        ):
            return NUMBER_
        self._reset(mark)
        if (
            (group := self.group())
        ):
            return group
        self._reset(mark)
        return None

    @memoize
    def group(self) -> Optional[Any]:
        # group: '(' expression ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (v := self.expression())
            and
            (literal_1 := self.expect(')'))
        ):
            return v . setGroup ( True )
        self._reset(mark)
        return None

    @memoize
    def arguments(self) -> Optional[Any]:
        # arguments: args ','? &')'
        mark = self._mark()
        if (
            (v := self.args())
            and
            (opt := self.expect(','),)
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def args(self) -> Optional[Any]:
        # args: ','.expression+
        mark = self._mark()
        if (
            (v := self._gather_37())
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def key_block(self) -> Optional[Any]:
        # key_block: NEWLINE INDENT match_keys NEWLINE DEDENT
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (v := self.match_keys())
            and
            (_newline_1 := self.expect('NEWLINE'))
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return v
        self._reset(mark)
        return None

    @memoize
    def match_keys(self) -> Optional[Any]:
        # match_keys: (',' NEWLINE*).match_key+
        mark = self._mark()
        if (
            (_gather_39 := self._gather_39())
        ):
            return _gather_39
        self._reset(mark)
        return None

    @memoize
    def match_key(self) -> Optional[Any]:
        # match_key: "default" '->' expression | expression "to" expression '->' expression | expression '->' expression
        mark = self._mark()
        if (
            (literal := self.expect("default"))
            and
            (literal_1 := self.expect('->'))
            and
            (v := self.expression())
        ):
            return kiwi . MatchKey ( None , None , v )
        self._reset(mark)
        if (
            (f := self.expression())
            and
            (literal := self.expect("to"))
            and
            (t := self.expression())
            and
            (literal_1 := self.expect('->'))
            and
            (v := self.expression())
        ):
            return kiwi . MatchKey ( f , t , v )
        self._reset(mark)
        if (
            (f := self.expression())
            and
            (literal := self.expect('->'))
            and
            (v := self.expression())
        ):
            return kiwi . MatchKey ( f , f , v )
        self._reset(mark)
        return None

    @memoize
    def NUMBER_(self) -> Optional[Any]:
        # NUMBER_: NUMBER
        mark = self._mark()
        if (
            (v := self.number())
        ):
            return kiwi . Number ( v . start , v . end , v . string )
        self._reset(mark)
        return None

    @memoize
    def NAME_(self) -> Optional[Any]:
        # NAME_: NAME
        mark = self._mark()
        if (
            (v := self.name())
        ):
            return kiwi . Name ( v . start , v . end , v . string )
        self._reset(mark)
        return None

    @memoize
    def WORD_(self) -> Optional[Any]:
        # WORD_: ((NUMBER | NAME))+
        mark = self._mark()
        if (
            (v := self._loop1_41())
        ):
            return kiwi . Word ( v [0] . start , v [- 1] . end , '' . join ( list ( map ( str , v ) ) ) )
        self._reset(mark)
        return None

    @memoize
    def STRING_(self) -> Optional[Any]:
        # STRING_: STRING
        mark = self._mark()
        if (
            (v := self.string())
        ):
            return kiwi . String ( v . start , v . end , v . string )
        self._reset(mark)
        return None

    @memoize
    def selector(self) -> Optional[Any]:
        # selector: '@' WORD_
        mark = self._mark()
        if (
            (literal := self.expect('@'))
            and
            (v := self.WORD_())
        ):
            return kiwi . Selector ( v . start , v . end , v . value )
        self._reset(mark)
        return None

    @memoize
    def states(self) -> Optional[Any]:
        # states: '[' state_key '=' state_value ']'
        mark = self._mark()
        if (
            (literal := self.expect('['))
            and
            (state_key := self.state_key())
            and
            (literal_1 := self.expect('='))
            and
            (state_value := self.state_value())
            and
            (literal_2 := self.expect(']'))
        ):
            return [literal, state_key, literal_1, state_value, literal_2]
        self._reset(mark)
        return None

    @memoize
    def state_key(self) -> Optional[Any]:
        # state_key: NAME_
        mark = self._mark()
        if (
            (NAME_ := self.NAME_())
        ):
            return NAME_
        self._reset(mark)
        return None

    @memoize
    def state_value(self) -> Optional[Any]:
        # state_value: nbt
        mark = self._mark()
        if (
            (nbt := self.nbt())
        ):
            return nbt
        self._reset(mark)
        return None

    @memoize
    def nbt(self) -> Optional[Any]:
        # nbt: nbt_dict | nbt_list | nbt_string
        mark = self._mark()
        if (
            (nbt_dict := self.nbt_dict())
        ):
            return nbt_dict
        self._reset(mark)
        if (
            (nbt_list := self.nbt_list())
        ):
            return nbt_list
        self._reset(mark)
        if (
            (nbt_string := self.nbt_string())
        ):
            return nbt_string
        self._reset(mark)
        return None

    @memoize
    def nbt_dict(self) -> Optional[Any]:
        # nbt_dict: '{' '}'
        mark = self._mark()
        if (
            (literal := self.expect('{'))
            and
            (literal_1 := self.expect('}'))
        ):
            return [literal, literal_1]
        self._reset(mark)
        return None

    @memoize
    def nbt_list(self) -> Optional[Any]:
        # nbt_list: '[' ']'
        mark = self._mark()
        if (
            (literal := self.expect('['))
            and
            (literal_1 := self.expect(']'))
        ):
            return [literal, literal_1]
        self._reset(mark)
        return None

    @memoize
    def nbt_string(self) -> Optional[Any]:
        # nbt_string: STRING_
        mark = self._mark()
        if (
            (STRING_ := self.STRING_())
        ):
            return STRING_
        self._reset(mark)
        return None

    @memoize
    def _loop1_1(self) -> Optional[Any]:
        # _loop1_1: (import_stmt | from_import_stmt)
        mark = self._mark()
        children = []
        while (
            (_tmp_42 := self._tmp_42())
        ):
            children.append(_tmp_42)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_2(self) -> Optional[Any]:
        # _loop1_2: (NEWLINE | ';')
        mark = self._mark()
        children = []
        while (
            (_tmp_43 := self._tmp_43())
        ):
            children.append(_tmp_43)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_4(self) -> Optional[Any]:
        # _loop0_4: ',' dotted_as_name
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.dotted_as_name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_3(self) -> Optional[Any]:
        # _gather_3: dotted_as_name _loop0_4
        mark = self._mark()
        if (
            (elem := self.dotted_as_name())
            is not None
            and
            (seq := self._loop0_4())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_5(self) -> Optional[Any]:
        # _loop1_5: statement
        mark = self._mark()
        children = []
        while (
            (statement := self.statement())
        ):
            children.append(statement)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_6(self) -> Optional[Any]:
        # _loop1_6: (NEWLINE | ';')
        mark = self._mark()
        children = []
        while (
            (_tmp_44 := self._tmp_44())
        ):
            children.append(_tmp_44)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_7(self) -> Optional[Any]:
        # _loop1_7: (NEWLINE)
        mark = self._mark()
        children = []
        while (
            (_newline := self.expect('NEWLINE'))
        ):
            children.append(_newline)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_9(self) -> Optional[Any]:
        # _loop0_9: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_8(self) -> Optional[Any]:
        # _gather_8: expression _loop0_9
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_9())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_11(self) -> Optional[Any]:
        # _loop0_11: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_10(self) -> Optional[Any]:
        # _gather_10: expression _loop0_11
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_11())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_13(self) -> Optional[Any]:
        # _loop0_13: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_12(self) -> Optional[Any]:
        # _gather_12: expression _loop0_13
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_13())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_15(self) -> Optional[Any]:
        # _loop0_15: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_14(self) -> Optional[Any]:
        # _gather_14: expression _loop0_15
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_15())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_17(self) -> Optional[Any]:
        # _loop0_17: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_16(self) -> Optional[Any]:
        # _gather_16: expression _loop0_17
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_17())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_18(self) -> Optional[Any]:
        # _loop1_18: expression
        mark = self._mark()
        children = []
        while (
            (expression := self.expression())
        ):
            children.append(expression)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_20(self) -> Optional[Any]:
        # _loop0_20: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_19(self) -> Optional[Any]:
        # _gather_19: expression _loop0_20
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_20())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_21(self) -> Optional[Any]:
        # _loop1_21: expression
        mark = self._mark()
        children = []
        while (
            (expression := self.expression())
        ):
            children.append(expression)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_22(self) -> Optional[Any]:
        # _loop1_22: (private_block | public_block | default_block)
        mark = self._mark()
        children = []
        while (
            (_tmp_45 := self._tmp_45())
        ):
            children.append(_tmp_45)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_23(self) -> Optional[Any]:
        # _tmp_23: ':' block
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (v := self.block())
        ):
            return [literal, v]
        self._reset(mark)
        return None

    @memoize
    def _tmp_24(self) -> Optional[Any]:
        # _tmp_24: ':' block
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (v := self.block())
        ):
            return [literal, v]
        self._reset(mark)
        return None

    @memoize
    def _tmp_25(self) -> Optional[Any]:
        # _tmp_25: ':' hiding_block
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (b := self.hiding_block())
        ):
            return [literal, b]
        self._reset(mark)
        return None

    @memoize
    def _loop0_26(self) -> Optional[Any]:
        # _loop0_26: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_27(self) -> Optional[Any]:
        # _loop0_27: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_28(self) -> Optional[Any]:
        # _loop0_28: expression
        mark = self._mark()
        children = []
        while (
            (expression := self.expression())
        ):
            children.append(expression)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_29(self) -> Optional[Any]:
        # _loop1_29: expression
        mark = self._mark()
        children = []
        while (
            (expression := self.expression())
        ):
            children.append(expression)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_31(self) -> Optional[Any]:
        # _loop0_31: (',' NEWLINE*) case
        mark = self._mark()
        children = []
        while (
            (_tmp_46 := self._tmp_46())
            and
            (elem := self.case())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_30(self) -> Optional[Any]:
        # _gather_30: case _loop0_31
        mark = self._mark()
        if (
            (elem := self.case())
            is not None
            and
            (seq := self._loop0_31())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_33(self) -> Optional[Any]:
        # _loop0_33: ',' lambda_param
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.lambda_param())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_32(self) -> Optional[Any]:
        # _gather_32: lambda_param _loop0_33
        mark = self._mark()
        if (
            (elem := self.lambda_param())
            is not None
            and
            (seq := self._loop0_33())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_34(self) -> Optional[Any]:
        # _loop1_34: disjunction
        mark = self._mark()
        children = []
        while (
            (disjunction := self.disjunction())
        ):
            children.append(disjunction)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_35(self) -> Optional[Any]:
        # _loop1_35: conjunction
        mark = self._mark()
        children = []
        while (
            (conjunction := self.conjunction())
        ):
            children.append(conjunction)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_36(self) -> Optional[Any]:
        # _loop1_36: compare_op_sum_pair
        mark = self._mark()
        children = []
        while (
            (compare_op_sum_pair := self.compare_op_sum_pair())
        ):
            children.append(compare_op_sum_pair)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_38(self) -> Optional[Any]:
        # _loop0_38: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_37(self) -> Optional[Any]:
        # _gather_37: expression _loop0_38
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_38())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_40(self) -> Optional[Any]:
        # _loop0_40: (',' NEWLINE*) match_key
        mark = self._mark()
        children = []
        while (
            (_tmp_47 := self._tmp_47())
            and
            (elem := self.match_key())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_39(self) -> Optional[Any]:
        # _gather_39: match_key _loop0_40
        mark = self._mark()
        if (
            (elem := self.match_key())
            is not None
            and
            (seq := self._loop0_40())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_41(self) -> Optional[Any]:
        # _loop1_41: (NUMBER | NAME)
        mark = self._mark()
        children = []
        while (
            (_tmp_48 := self._tmp_48())
        ):
            children.append(_tmp_48)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_42(self) -> Optional[Any]:
        # _tmp_42: import_stmt | from_import_stmt
        mark = self._mark()
        if (
            (import_stmt := self.import_stmt())
        ):
            return import_stmt
        self._reset(mark)
        if (
            (from_import_stmt := self.from_import_stmt())
        ):
            return from_import_stmt
        self._reset(mark)
        return None

    @memoize
    def _tmp_43(self) -> Optional[Any]:
        # _tmp_43: NEWLINE | ';'
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
        ):
            return _newline
        self._reset(mark)
        if (
            (literal := self.expect(';'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_44(self) -> Optional[Any]:
        # _tmp_44: NEWLINE | ';'
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
        ):
            return _newline
        self._reset(mark)
        if (
            (literal := self.expect(';'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_45(self) -> Optional[Any]:
        # _tmp_45: private_block | public_block | default_block
        mark = self._mark()
        if (
            (private_block := self.private_block())
        ):
            return private_block
        self._reset(mark)
        if (
            (public_block := self.public_block())
        ):
            return public_block
        self._reset(mark)
        if (
            (default_block := self.default_block())
        ):
            return default_block
        self._reset(mark)
        return None

    @memoize
    def _tmp_46(self) -> Optional[Any]:
        # _tmp_46: ',' NEWLINE*
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (_loop0_49 := self._loop0_49(),)
        ):
            return [literal, _loop0_49]
        self._reset(mark)
        return None

    @memoize
    def _tmp_47(self) -> Optional[Any]:
        # _tmp_47: ',' NEWLINE*
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (_loop0_50 := self._loop0_50(),)
        ):
            return [literal, _loop0_50]
        self._reset(mark)
        return None

    @memoize
    def _tmp_48(self) -> Optional[Any]:
        # _tmp_48: NUMBER | NAME
        mark = self._mark()
        if (
            (number := self.number())
        ):
            return number
        self._reset(mark)
        if (
            (name := self.name())
        ):
            return name
        self._reset(mark)
        return None

    @memoize
    def _loop0_49(self) -> Optional[Any]:
        # _loop0_49: NEWLINE
        mark = self._mark()
        children = []
        while (
            (_newline := self.expect('NEWLINE'))
        ):
            children.append(_newline)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_50(self) -> Optional[Any]:
        # _loop0_50: NEWLINE
        mark = self._mark()
        children = []
        while (
            (_newline := self.expect('NEWLINE'))
        ):
            children.append(_newline)
            mark = self._mark()
        self._reset(mark)
        return children

    KEYWORDS = ('import', 'promise', 'private', 'or', 'return', 'namespace', 'false', 'public', 'pass', 'and', 'break', 'true', 'for', 'while', 'continue', 'none', 'function', 'in', 'not', 'if', 'else')
    SOFT_KEYWORDS = ('default', 'lambda', 'case', 'as', 'match', 'to', 'from')


if __name__ == '__main__':
    from pegen.parser import simple_parser_main
    simple_parser_main(KiwiParser)
