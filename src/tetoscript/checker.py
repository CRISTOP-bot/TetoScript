"""Static name and type checker for the implemented TetoScript subset."""
from __future__ import annotations
from dataclasses import dataclass
from .parser import Expr, Stmt, parse


class TetoCheckError(Exception):
    """A static diagnostic that prevents a program from running."""


@dataclass(frozen=True)
class FunctionType:
    parameters: tuple[str, ...]
    result: str


BUILTIN_TYPES = {"string", "number", "boolean", "bool"}


class Checker:
    def __init__(self) -> None:
        self.scopes: list[dict[str, str | FunctionType]] = [{"tetolog": FunctionType(("any",), "nose")}]
        self.return_type: str | None = None

    def error(self, line: int, message: str) -> None:
        raise TetoCheckError(f"línea {line}: {message}")

    def lookup(self, name: str, line: int) -> str | FunctionType:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.error(line, f"nombre no definido: {name}")
        raise AssertionError("unreachable")

    def define(self, name: str, value: str | FunctionType, line: int) -> None:
        scope = self.scopes[-1]
        if name in scope:
            self.error(line, f"nombre ya declarado en este ámbito: {name}")
        scope[name] = value

    def validate_type(self, name: str | None, line: int) -> str:
        if name is None:
            return "unknown"
        if name not in BUILTIN_TYPES:
            self.error(line, f"tipo desconocido: {name}")
        return "boolean" if name == "bool" else name

    @staticmethod
    def compatible(actual: str, expected: str) -> bool:
        return actual in ("unknown", "any") or expected in ("unknown", "any") or actual == expected

    def expect(self, actual: str, expected: str, line: int, where: str) -> None:
        if not self.compatible(actual, expected):
            self.error(line, f"{where}: se esperaba {expected}, se obtuvo {actual}")

    def expression(self, expr: Expr) -> str:
        if expr.kind == "literal":
            if expr.value is None: return "nose"
            if isinstance(expr.value, bool): return "boolean"
            if isinstance(expr.value, (int, float)): return "number"
            return "string"
        if expr.kind == "name":
            value = self.lookup(str(expr.value), expr.line)
            if isinstance(value, FunctionType): return "function"
            return value
        if expr.kind == "unary":
            operand = self.expression(expr.children[0])
            if expr.value == "not":
                self.expect(operand, "boolean", expr.line, "el operador not")
                return "boolean"
            self.expect(operand, "number", expr.line, "el operador unario -")
            return "number"
        if expr.kind == "binary":
            op = str(expr.value)
            left = self.expression(expr.children[0])
            right = self.expression(expr.children[1])
            if op in ("and", "or", "&&", "||"):
                self.expect(left, "boolean", expr.line, f"el operando izquierdo de {op}")
                self.expect(right, "boolean", expr.line, f"el operando derecho de {op}")
                return "boolean"
            if op in ("+", "-", "*", "/", "%"):
                if op == "+" and left == right == "string": return "string"
                self.expect(left, "number", expr.line, f"el operando izquierdo de {op}")
                self.expect(right, "number", expr.line, f"el operando derecho de {op}")
                return "number"
            if op in ("<", "<=", ">", ">="):
                if left != "unknown" and right != "unknown" and left != right:
                    self.error(expr.line, f"no se pueden comparar {left} y {right} con {op}")
                if left not in ("unknown", "number", "string"):
                    self.error(expr.line, f"el operador {op} no admite {left}")
                return "boolean"
            if op in ("==", "!="):
                if left != "unknown" and right != "unknown" and left != right:
                    self.error(expr.line, f"no se pueden comparar {left} y {right} con {op}")
                return "boolean"
        if expr.kind == "call":
            callee, args = expr.children
            if callee.kind == "name" and callee.value == "tetolog":
                if len(args) != 1:
                    self.error(expr.line, "tetolog espera exactamente un argumento")
                self.expression(args[0])
                return "nose"
            if callee.kind != "name":
                self.expression(callee)
                self.error(expr.line, "solo se pueden llamar funciones con nombre")
            function = self.lookup(str(callee.value), callee.line)
            if not isinstance(function, FunctionType):
                self.error(expr.line, f"{callee.value} no es una función")
            if len(args) != len(function.parameters):
                self.error(expr.line, f"{callee.value} espera {len(function.parameters)} argumentos, recibió {len(args)}")
            for index, (argument, expected) in enumerate(zip(args, function.parameters), start=1):
                actual = self.expression(argument)
                self.expect(actual, expected, argument.line, f"argumento {index} de {callee.value}")
            return function.result
        self.error(expr.line, "expresión no soportada por el analizador")
        raise AssertionError("unreachable")

    def statements(self, statements: tuple | list[Stmt]) -> None:
        for stmt in statements:
            if stmt.kind == "let":
                name, annotation = stmt.value
                actual = self.expression(stmt.children[0])
                expected = self.validate_type(annotation, stmt.line)
                if expected != "unknown": self.expect(actual, expected, stmt.line, f"inicialización de {name}")
                self.define(str(name), expected if expected != "unknown" else actual, stmt.line)
            elif stmt.kind == "function":
                name, parameters, declared_result = stmt.value
                parameter_types = tuple(self.validate_type(t, stmt.line) for _, t in parameters)
                result_type = self.validate_type(declared_result, stmt.line)
                signature = FunctionType(parameter_types, result_type)
                self.define(str(name), signature, stmt.line)
                self.scopes.append({})
                for (parameter, _), parameter_type in zip(parameters, parameter_types):
                    self.define(str(parameter), parameter_type, stmt.line)
                previous_return = self.return_type
                self.return_type = result_type
                self.statements(stmt.children)
                self.return_type = previous_return
                self.scopes.pop()
            elif stmt.kind == "if":
                condition, yes, no = stmt.children
                self.expect(self.expression(condition), "boolean", condition.line, "la condición de Teto")
                for branch in (yes, no):
                    self.scopes.append({})
                    self.statements(branch)
                    self.scopes.pop()
            elif stmt.kind == "return":
                if self.return_type is None:
                    self.error(stmt.line, "return solo se permite dentro de una función")
                actual = self.expression(stmt.children[0]) if stmt.children else "nose"
                self.expect(actual, self.return_type, stmt.line, "valor de retorno")
            elif stmt.kind == "expr":
                self.expression(stmt.children[0])


def check(source: str) -> None:
    """Parse and statically check names and types; raise on first diagnostic."""
    Checker().statements(parse(source))
