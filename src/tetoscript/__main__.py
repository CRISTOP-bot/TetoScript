from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any


class TetoScriptError(Exception):
    """Error de sintaxis o ejecución de TetoScript."""


def evaluate(expression: str, variables: dict[str, Any]) -> Any:
    """Evalúa expresiones seguras con literales, variables y operadores básicos."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise TetoScriptError(f"expresión inválida: {expression}") from exc

    def visit(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool, type(None))):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in variables:
                raise TetoScriptError(f"variable no definida: {node.id}")
            return variables[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            return left / right
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left, right = visit(node.left), visit(node.comparators[0])
            op = node.ops[0]
            if isinstance(op, ast.Eq): return left == right
            if isinstance(op, ast.NotEq): return left != right
            if isinstance(op, ast.Lt): return left < right
            if isinstance(op, ast.LtE): return left <= right
            if isinstance(op, ast.Gt): return left > right
            if isinstance(op, ast.GtE): return left >= right
        if isinstance(node, ast.BoolOp):
            values = [bool(visit(value)) for value in node.values]
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not visit(node.operand)
        raise TetoScriptError("operación no permitida en una expresión")

    return visit(tree.body)


def run(source: str, variables: dict[str, Any] | None = None) -> list[str]:
    """Ejecuta el subconjunto inicial y devuelve las líneas impresas."""
    lines = source.splitlines()
    if variables is None:
        variables = {}
    output: list[str] = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1
        if not stripped or stripped.startswith("#"):
            continue
        if raw[:1].isspace():
            raise TetoScriptError(f"línea {i}: indentación inesperada")

        if stripped.startswith("teto "):
            declaration = stripped[5:]
            if "=" not in declaration:
                raise TetoScriptError(f"línea {i}: se esperaba 'teto nombre = expresión'")
            name, expression = declaration.split("=", 1)
            name = name.strip()
            if not name.isidentifier():
                raise TetoScriptError(f"línea {i}: nombre de variable inválido")
            variables[name] = evaluate(expression.strip(), variables)
            continue

        if stripped.startswith("tetolog"):
            if not (stripped.startswith("tetolog (") and stripped.endswith(")")):
                raise TetoScriptError(f"línea {i}: usa tetolog (expresión)")
            output.append(str(evaluate(stripped[len("tetolog ("):-1], variables)))
            continue

        if stripped.startswith("Teto ") and stripped.endswith(":"):
            condition = bool(evaluate(stripped[5:-1].strip(), variables))
            true_block, false_block = [], []
            current = true_block
            saw_else = False
            while i < len(lines):
                candidate = lines[i]
                token = candidate.strip()
                if not token or token.startswith("#"):
                    i += 1
                    continue
                if not candidate[:1].isspace():
                    if token == "else:":
                        if saw_else:
                            raise TetoScriptError(f"línea {i + 1}: else duplicado")
                        saw_else = True
                        current = false_block
                        i += 1
                        continue
                    break
                current.append(candidate.lstrip())
                i += 1
            selected = true_block if condition else false_block
            if selected:
                output.extend(run("\n".join(selected), variables))
            continue

        raise TetoScriptError(f"línea {i}: instrucción no reconocida: {stripped}")
    return output


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Uso: python -m tetoscript archivo.teto", file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        result = run(path.read_text(encoding="utf-8"))
    except (OSError, TetoScriptError, TypeError, ValueError, ZeroDivisionError) as exc:
        print(f"TetoScript: {exc}", file=sys.stderr)
        return 1
    for line in result:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
