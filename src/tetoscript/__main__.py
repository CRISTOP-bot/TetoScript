from __future__ import annotations
import argparse
from pathlib import Path
import sys
from .lexer import TetoSyntaxError
from .runtime import TetoRuntimeError, run
from .parser import parse
from .checker import TetoCheckError, check

def main(argv: list[str] | None=None) -> int:
    args=list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "check":
        if len(args) != 2:
            print("Uso: teto check archivo.teto", file=sys.stderr)
            return 2
        path=Path(args[1])
        try:
            check(path.read_text(encoding="utf-8"))
        except (OSError,TetoSyntaxError,TetoCheckError) as exc:
            print(f"TetoScript: {exc}",file=sys.stderr); return 1
        print(f"Análisis correcto: {path}")
        return 0
    cli=argparse.ArgumentParser(prog="teto",description="Intérprete experimental de TetoScript")
    cli.add_argument("archivo", help="archivo fuente .teto")
    parsed=cli.parse_args(args)
    try:
        output=run(Path(parsed.archivo).read_text(encoding="utf-8"))
    except (OSError,TetoSyntaxError,TetoRuntimeError) as exc:
        print(f"TetoScript: {exc}",file=sys.stderr); return 1
    for line in output: print(line)
    return 0

if __name__=="__main__": raise SystemExit(main())
