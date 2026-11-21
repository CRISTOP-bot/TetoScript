from __future__ import annotations
import argparse
from pathlib import Path
import sys
from .lexer import TetoSyntaxError
from .runtime import TetoRuntimeError, run

def main(argv: list[str] | None=None) -> int:
    cli=argparse.ArgumentParser(prog="teto",description="Intérprete experimental de TetoScript")
    cli.add_argument("archivo", help="archivo fuente .teto")
    args=cli.parse_args(argv)
    try:
        output=run(Path(args.archivo).read_text(encoding="utf-8"))
    except (OSError,TetoSyntaxError,TetoRuntimeError) as exc:
        print(f"TetoScript: {exc}",file=sys.stderr); return 1
    for line in output: print(line)
    return 0

if __name__=="__main__": raise SystemExit(main())
