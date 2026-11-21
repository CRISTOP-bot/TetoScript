"""Recursive-descent parser and Pratt expression parser."""
from __future__ import annotations
from dataclasses import dataclass
from .lexer import Token, TetoSyntaxError, tokenize

@dataclass
class Expr:
    kind: str
    value: object = None
    children: tuple = ()
    line: int = 1

@dataclass
class Stmt:
    kind: str
    value: object = None
    children: tuple = ()
    line: int = 1

class Parser:
    def __init__(self, tokens: list[Token]): self.tokens, self.i = tokens, 0
    @property
    def current(self) -> Token: return self.tokens[self.i]
    def advance(self) -> Token:
        token = self.current
        if token.kind != "EOF": self.i += 1
        return token
    def accept(self, kind: str, value: object = None) -> Token | None:
        if self.current.kind == kind and (value is None or self.current.value == value): return self.advance()
        return None
    def expect(self, kind: str, value: object = None) -> Token:
        token = self.accept(kind, value)
        if token: return token
        want = repr(value) if value is not None else kind
        raise TetoSyntaxError(f"línea {self.current.line}:{self.current.column}: se esperaba {want}, llegó {self.current.value!r}")
    def keyword(self, word: str) -> bool: return self.current.kind == "IDENT" and self.current.value == word
    def expect_keyword(self, word: str) -> Token:
        if self.keyword(word): return self.advance()
        raise TetoSyntaxError(f"línea {self.current.line}:{self.current.column}: se esperaba {word}")
    def parse(self) -> list[Stmt]:
        body=[]
        while self.current.kind != "EOF":
            if self.accept(";"): continue
            body.append(self.statement())
        return body
    def statement(self) -> Stmt:
        if self.keyword("teto"):
            start=self.advance()
            if self.keyword("fn"): return self.function(start)
            name=self.expect("IDENT")
            annotation=None
            if self.accept(":"): annotation=self.expect("IDENT").value
            self.expect("=")
            value=self.expression()
            self.accept(";")
            return Stmt("let", (name.value, annotation), (value,), start.line)
        if self.keyword("Teto"):
            start=self.advance()
            self.expect("("); condition=self.expression(); self.expect(")")
            yes=self.block(); no=[]
            if self.keyword("else"):
                self.advance(); no=self.block()
            return Stmt("if", None, (condition, tuple(yes), tuple(no)), start.line)
        if self.keyword("return"):
            start=self.advance()
            value=None if self.current.kind in (";", "}", "EOF") else self.expression()
            self.accept(";")
            return Stmt("return", None, (() if value is None else (value,)), start.line)
        expr=self.expression(); self.accept(";")
        return Stmt("expr", None, (expr,), expr.line)
    def function(self, start: Token) -> Stmt:
        self.expect_keyword("fn"); name=self.expect("IDENT"); self.expect("(")
        params=[]
        if self.current.kind != ")":
            while True:
                p=self.expect("IDENT"); self.expect(":"); t=self.expect("IDENT")
                params.append((p.value,t.value))
                if not self.accept(","): break
        self.expect(")")
        return_type=None
        if self.accept("->"): return_type=self.expect("IDENT").value
        body=self.block()
        return Stmt("function", (name.value, tuple(params), return_type), tuple(body), start.line)
    def block(self) -> list[Stmt]:
        self.expect("{"); body=[]
        while self.current.kind not in ("}", "EOF"):
            if self.accept(";"): continue
            body.append(self.statement())
        self.expect("}")
        return body
    PRECEDENCE={"||":1,"or":1,"&&":2,"and":2,"==":3,"!=":3,"<":4,"<=":4,">":4,">=":4,"+":5,"-":5,"*":6,"/":6,"%":6}
    def expression(self, min_prec: int=0) -> Expr:
        left=self.prefix()
        while True:
            op=str(self.current.value)
            prec=self.PRECEDENCE.get(op, -1)
            if prec < min_prec: break
            token=self.advance(); right=self.expression(prec+1)
            left=Expr("binary",op,(left,right),token.line)
        return left
    def prefix(self) -> Expr:
        token=self.advance()
        if token.kind in ("NUMBER","STRING"): node=Expr("literal",token.value,(),token.line)
        elif token.kind == "IDENT" and token.value in ("true","false","nose","null"):
            values={"true":True,"false":False,"nose":None,"null":None}; node=Expr("literal",values[token.value],(),token.line)
        elif token.kind == "IDENT" and token.value in ("not",): node=Expr("unary","not",(self.expression(7),),token.line)
        elif token.kind in ("!","-"): node=Expr("unary","not" if token.kind=="!" else "-",(self.expression(7),),token.line)
        elif token.kind == "(":
            node=self.expression(); self.expect(")")
        elif token.kind == "IDENT": node=Expr("name",token.value,(),token.line)
        else: raise TetoSyntaxError(f"línea {token.line}:{token.column}: se esperaba una expresión")
        while self.accept("("):
            args=[]
            if self.current.kind != ")":
                while True:
                    args.append(self.expression())
                    if not self.accept(","): break
            self.expect(")"); node=Expr("call",None,(node,tuple(args)),node.line)
        return node

def parse(source: str) -> list[Stmt]:
    return Parser(tokenize(source)).parse()
