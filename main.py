from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import sys

from compiler.errors import CompilerError
from compiler.gui import launch_gui
from compiler.pipeline import compile_source, format_instructions, format_object, format_outputs, format_token_stream


def run_source(source: str, debug: bool = False) -> list[float]:
    result = compile_source(source)

    if debug:
        print("=== TOKENS ===")
        print(format_token_stream(result.tokens))
        print("=== AST ===")
        print(format_object(result.ast))
        print("=== IR ===")
        print(format_instructions(result.ir_program.instructions))
        print("=== OPTIMIZED IR ===")
        print(format_instructions(result.optimized_ir_program.instructions))
        print("=== OUTPUT ===")
        print(format_outputs(result.outputs))
    else:
        for value in result.outputs:
            print(value)

    return result.outputs


def read_interactive_source() -> str:
    print("VintageCalc interactive mode. Enter program lines; submit a blank line to run.")
    lines: list[str] = []
    while True:
        try:
            line = input("vc> ")
        except EOFError:
            break
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines) + ("\n" if lines else "")


def main() -> None:
    parser = ArgumentParser(description="VintageCalc compiler")
    parser.add_argument("input", nargs="?", help="Path to a .vc source file")
    parser.add_argument("--debug", action="store_true", help="Print tokens, AST, IR, and optimized IR")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--gui", action="store_true", help="Open the graphical debug studio")
    args = parser.parse_args()

    try:
        if args.gui:
            launch_gui()
            return

        if args.interactive:
            source = read_interactive_source()
            if not source.strip():
                return
            run_source(source, debug=args.debug)
            return

        if not args.input:
            parser.print_help()
            return

        source_path = Path(args.input)
        source = source_path.read_text(encoding="utf-8")
        run_source(source, debug=args.debug)
    except CompilerError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
    except FileNotFoundError:
        print(f"Source file not found: {args.input}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
