"""Interpreter runtime with lexical scopes and basic runtime type checks."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from .parser import Expr, Stmt, parse

class TetoRuntimeError(Exception): pass

class Environment:
    def __init__(self, parent: Environment | None=None): self.values: dict[str,Any]={}; self.parent=parent
    def get(self,name: str):
        if name in self.values: return self.values[name]
        if self.parent: return self.parent.get(name)
        raise TetoRuntimeError(f"variable no definida: {name}")
    def define(self,name: str,value: Any):
        if name in self.values: raise TetoRuntimeError(f"variable ya declarada: {name}")
        self.values[name]=value
    def assign(self,name: str,value: Any):
        if name in self.values:
            self.values[name]=value; return
        if self.parent:
            self.parent.assign(name,value); return
        raise TetoRuntimeError(f"variable no definida: {name}")
    def contains(self,name: str) -> bool:
        return name in self.values or (self.parent.contains(name) if self.parent else False)
    def declared_type(self,name: str):
        if name in self.values: return getattr(self,"types",{}).get(name)
        if self.parent: return self.parent.declared_type(name)
        return None
    @staticmethod
    def runtime_type(value: Any) -> str:
        if value is None: return "nose"
        if isinstance(value,bool): return "boolean"
        if isinstance(value,(int,float)): return "number"
        if isinstance(value,str): return "string"
        if isinstance(value,Function): return "function"
        return "unknown"
    def set_type(self,name: str,type_name: str | None):
        if not hasattr(self,"types"): self.types={}
        self.types[name]=type_name

@dataclass
class Function:
    name: str
    params: tuple
    return_type: str | None
    body: tuple
    closure: Environment

@dataclass
class ReturnSignal:
    value: Any

TYPE_CHECKS={"string":lambda x:isinstance(x,str),"number":lambda x:isinstance(x,(int,float)) and not isinstance(x,bool),"boolean":lambda x:isinstance(x,bool),"bool":lambda x:isinstance(x,bool)}
def check_type(value: Any, type_name: str | None, line: int):
    if type_name is None: return
    if type_name not in TYPE_CHECKS: raise TetoRuntimeError(f"línea {line}: tipo desconocido: {type_name}")
    if not TYPE_CHECKS[type_name](value): raise TetoRuntimeError(f"línea {line}: se esperaba {type_name}, se obtuvo {type(value).__name__}")

class Interpreter:
    def __init__(self):
        self.output: list[str]=[]
        self.global_env=Environment()
        self.global_env.define("tetolog", lambda *args:self._log(*args))
    def _log(self,*args):
        if len(args)!=1: raise TetoRuntimeError("tetolog espera exactamente un argumento")
        self.output.append(self.stringify(args[0])); return None
    def stringify(self,value):
        if value is None: return "nose"
        if value is True: return "true"
        if value is False: return "false"
        return str(value)
    def evaluate(self,expr: Expr,env: Environment):
        if expr.kind=="literal": return expr.value
        if expr.kind=="name": return env.get(str(expr.value))
        if expr.kind=="unary":
            value=self.evaluate(expr.children[0],env)
            if expr.value=="not": return not self.truthy(value)
            if isinstance(value,bool) or not isinstance(value,(int,float)): raise TetoRuntimeError(f"línea {expr.line}: '-' requiere un número")
            return -value
        if expr.kind=="binary":
            left=self.evaluate(expr.children[0],env); op=expr.value
            if op in ("and","&&"):
                return self.evaluate(expr.children[1],env) if self.truthy(left) else left
            if op in ("or","||"):
                return left if self.truthy(left) else self.evaluate(expr.children[1],env)
            right=self.evaluate(expr.children[1],env)
            try:
                if op=="+": return left+right
                if op=="-": return left-right
                if op=="*": return left*right
                if op=="/": return left/right
                if op=="%": return left%right
                if op=="==": return left==right
                if op=="!=": return left!=right
                if op=="<": return left<right
                if op=="<=": return left<=right
                if op==">": return left>right
                if op==">=": return left>=right
            except (TypeError,ZeroDivisionError) as exc: raise TetoRuntimeError(f"línea {expr.line}: operación inválida: {exc}") from exc
        if expr.kind=="call":
            callee=self.evaluate(expr.children[0],env)
            args=[self.evaluate(arg,env) for arg in expr.children[1]]
            if isinstance(callee,Function): return self.call(callee,args,expr.line)
            if callable(callee): return callee(*args)
            raise TetoRuntimeError(f"línea {expr.line}: el valor no se puede llamar")
        raise TetoRuntimeError(f"línea {expr.line}: expresión no soportada")
    @staticmethod
    def truthy(value): return value is not None and value is not False and value != 0 and value != ""
    def execute(self,statements: tuple | list,env: Environment):
        for stmt in statements:
            if stmt.kind=="let":
                (name,annotation)=stmt.value; value=self.evaluate(stmt.children[0],env); check_type(value,annotation,stmt.line); env.define(name,value); env.set_type(name,annotation or Environment.runtime_type(value))
            elif stmt.kind=="assign":
                name=str(stmt.value); value=self.evaluate(stmt.children[0],env)
                if not env.contains(name): raise TetoRuntimeError(f"línea {stmt.line}: variable no definida: {name}")
                check_type(value,env.declared_type(name),stmt.line); env.assign(name,value)
            elif stmt.kind=="function":
                name,params,return_type=stmt.value; env.define(name,Function(name,params,return_type,stmt.children,env)); env.set_type(name,"function")
            elif stmt.kind=="if":
                cond,yes,no=stmt.children; branch=yes if self.truthy(self.evaluate(cond,env)) else no
                signal=self.execute(branch,Environment(env))
                if signal: return signal
            elif stmt.kind=="while":
                condition,body=stmt.children; iterations=0
                while self.truthy(self.evaluate(condition,env)):
                    iterations += 1
                    if iterations > 100000: raise TetoRuntimeError(f"línea {stmt.line}: se superó el límite de 100000 iteraciones")
                    signal=self.execute(body,Environment(env))
                    if signal: return signal
            elif stmt.kind=="return":
                value=self.evaluate(stmt.children[0],env) if stmt.children else None
                return ReturnSignal(value)
            elif stmt.kind=="expr": self.evaluate(stmt.children[0],env)
        return None
    def call(self,fn: Function,args: list[Any],line: int):
        if len(args)!=len(fn.params): raise TetoRuntimeError(f"línea {line}: {fn.name} espera {len(fn.params)} argumentos, recibió {len(args)}")
        scope=Environment(fn.closure)
        for (name,type_name),value in zip(fn.params,args): check_type(value,type_name,line); scope.define(name,value); scope.set_type(name,type_name or Environment.runtime_type(value))
        signal=self.execute(fn.body,scope)
        value=signal.value if signal else None
        check_type(value,fn.return_type,line)
        return value

def run(source: str) -> list[str]:
    interpreter=Interpreter()
    try:
        interpreter.execute(parse(source),interpreter.global_env)
    except RecursionError as exc: raise TetoRuntimeError("profundidad máxima de llamadas excedida") from exc
    return interpreter.output
