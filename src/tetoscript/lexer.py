"""Tokenizer for the TetoScript language."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int

class TetoSyntaxError(Exception):
    pass


def tokenize(source: str) -> list[Token]:
    result: list[Token] = []
    i = 0
    line = 1
    col = 1
    while i < len(source):
        ch = source[i]
        if ch in " \t\r":
            i += 1; col += 1; continue
        if ch == "\n":
            i += 1; line += 1; col = 1; continue
        if ch == "#":
            while i < len(source) and source[i] != "\n":
                i += 1; col += 1
            continue
        start_line, start_col = line, col
        if ch in "\"'":
            quote = ch
            i += 1; col += 1
            chars: list[str] = []
            while i < len(source) and source[i] != quote:
                if source[i] == "\\":
                    i += 1; col += 1
                    if i >= len(source):
                        raise TetoSyntaxError(f"línea {line}:{col}: escape sin terminar")
                    escapes = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "\"": "\"", "'": "'"}
                    chars.append(escapes.get(source[i], source[i]))
                else:
                    if source[i] == "\n":
                        line += 1; col = 0
                    chars.append(source[i])
                i += 1; col += 1
            if i >= len(source):
                raise TetoSyntaxError(f"línea {start_line}:{start_col}: texto sin cerrar")
            i += 1; col += 1
            result.append(Token("STRING", "".join(chars), start_line, start_col)); continue
        if ch.isdigit():
            start = i
            while i < len(source) and source[i].isdigit(): i += 1; col += 1
            if i < len(source) and source[i] == "." and i + 1 < len(source) and source[i+1].isdigit():
                i += 1; col += 1
                while i < len(source) and source[i].isdigit(): i += 1; col += 1
            text = source[start:i]
            result.append(Token("NUMBER", float(text) if "." in text else int(text), start_line, start_col)); continue
        if ch.isalpha() or ch == "_":
            start = i
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1; col += 1
            result.append(Token("IDENT", source[start:i], start_line, start_col)); continue
        matched = next((op for op in ("==", "!=", "<=", ">=", "->", "&&", "||") if source.startswith(op, i)), None)
        if matched:
            result.append(Token(matched, matched, line, col)); i += len(matched); col += len(matched); continue
        if ch in "+-*/%<>=!(){}:,;":
            result.append(Token(ch, ch, line, col)); i += 1; col += 1; continue
        raise TetoSyntaxError(f"línea {line}:{col}: carácter no válido {ch!r}")
    result.append(Token("EOF", None, line, col))
    return result
