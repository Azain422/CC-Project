from __future__ import annotations

from dataclasses import dataclass
from pprint import pformat

from .ast_nodes import (
    Assignment,
    Binary,
    ExpressionStatement,
    FunctionCall,
    Identifier,
    Number,
    Percent,
    PrintStatement,
    Program,
    Unary,
)
from .codegen import IRGenerator
from .execution import IRInterpreter
from .ir import Assign, BinaryOp, Call, Label, LoadConst, LoadName, Print, UnaryOp
from .lexer import Lexer
from .optimizer import Optimizer
from .parser import Parser
from .semantic import SemanticAnalyzer


@dataclass(frozen=True)
class CompilationResult:
    source: str
    tokens: list
    ast: object
    ir_program: object
    optimized_ir_program: object
    outputs: list[float]


def compile_source(source: str) -> CompilationResult:
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    ir_program = IRGenerator().generate(ast)
    optimized_ir_program = Optimizer().optimize(ir_program)
    outputs = IRInterpreter().execute(optimized_ir_program)
    return CompilationResult(
        source=source,
        tokens=tokens,
        ast=ast,
        ir_program=ir_program,
        optimized_ir_program=optimized_ir_program,
        outputs=outputs,
    )


def format_token_stream(tokens: list) -> str:
    return "\n".join(pformat(token) for token in tokens)


def format_object(value: object) -> str:
    if isinstance(value, Program):
        return _format_ast(value)
    return pformat(value)


def format_instructions(instructions: list) -> str:
    if not instructions:
        return "<no instructions>"

    lines: list[str] = []
    lines.append("Idx | Instruction")
    lines.append("----+--------------------------------------------------------")
    for index, instruction in enumerate(instructions, start=1):
        lines.append(f"{index:>3} | {_format_instruction(instruction)}")
    return "\n".join(lines)


def format_outputs(outputs: list[float]) -> str:
    if not outputs:
        return "<no output>"
    return "\n".join(str(value) for value in outputs)


def _format_ast(program: Program) -> str:
    root_label, root_children = _ast_node(program)
    lines: list[str] = [root_label]
    for index, child in enumerate(root_children):
        _render_tree(child, lines, "", index == len(root_children) - 1)
    return "\n".join(lines)


def _render_tree(node: tuple[str, list], lines: list[str], prefix: str, is_last: bool) -> None:
    label, children = node
    connector = "\\- " if is_last else "+- "
    lines.append(f"{prefix}{connector}{label}")

    child_prefix = prefix + ("   " if is_last else "|  ")

    for index, child in enumerate(children):
        child_is_last = index == len(children) - 1
        _render_tree(child, lines, child_prefix, child_is_last)


def _ast_node(value: object) -> tuple[str, list]:
    if isinstance(value, Program):
        return (
            "Program",
            [_ast_node(statement) for statement in value.statements],
        )

    if isinstance(value, Assignment):
        return (f"Assignment({value.name})", [_ast_node(value.value)])

    if isinstance(value, PrintStatement):
        return ("Print", [_ast_node(value.value)])

    if isinstance(value, ExpressionStatement):
        return ("ExpressionStatement", [_ast_node(value.value)])

    if isinstance(value, Number):
        return (f"Number({value.value})", [])

    if isinstance(value, Identifier):
        return (f"Identifier({value.name})", [])

    if isinstance(value, Unary):
        return (f"Unary({value.operator})", [_ast_node(value.operand)])

    if isinstance(value, Binary):
        return (
            f"Binary({value.operator})",
            [_ast_node(value.left), _ast_node(value.right)],
        )

    if isinstance(value, Percent):
        return ("Percent", [_ast_node(value.value)])

    if isinstance(value, FunctionCall):
        return (f"Call({value.name})", [_ast_node(value.argument)])

    return (value.__class__.__name__, [])


def _format_instruction(instruction: object) -> str:
    if isinstance(instruction, Label):
        return f"label {instruction.name}:"
    if isinstance(instruction, LoadConst):
        return f"{instruction.target} = {instruction.value}"
    if isinstance(instruction, LoadName):
        return f"{instruction.target} = load {instruction.name}"
    if isinstance(instruction, Assign):
        return f"{instruction.target} = {instruction.value}"
    if isinstance(instruction, UnaryOp):
        return f"{instruction.target} = {instruction.operator}{instruction.operand}"
    if isinstance(instruction, BinaryOp):
        return f"{instruction.target} = {instruction.left} {instruction.operator} {instruction.right}"
    if isinstance(instruction, Call):
        return f"{instruction.target} = {instruction.name}({instruction.argument})"
    if isinstance(instruction, Print):
        return f"print {instruction.value}"
    return pformat(instruction)
