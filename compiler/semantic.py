from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import (
    Assignment,
    Binary,
    Expression,
    ExpressionStatement,
    FunctionCall,
    Identifier,
    Number,
    Percent,
    PrintStatement,
    Program,
    Unary,
)
from .errors import SemanticError, SourcePosition


@dataclass
class SymbolTable:
    symbols: dict[str, float] = field(default_factory=dict)

    def define(self, name: str, value: float) -> None:
        self.symbols[name] = value

    def is_defined(self, name: str) -> bool:
        return name in self.symbols

    def get(self, name: str) -> float:
        return self.symbols[name]


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()

    def analyze(self, program: Program) -> None:
        for statement in program.statements:
            self._statement(statement)

    def _statement(self, statement) -> None:
        if isinstance(statement, Assignment):
            value = self._expression(statement.value)
            self.symbol_table.define(statement.name, value)
            return

        if isinstance(statement, PrintStatement):
            self._expression(statement.value)
            return

        if isinstance(statement, ExpressionStatement):
            self._expression(statement.value)
            return

        raise SemanticError("Unsupported statement")

    def _expression(self, expression: Expression) -> float:
        if isinstance(expression, Number):
            return expression.value

        if isinstance(expression, Identifier):
            if not self.symbol_table.is_defined(expression.name):
                raise SemanticError(
                    f"Undefined variable '{expression.name}'",
                    expression.position,
                )
            return self.symbol_table.get(expression.name)

        if isinstance(expression, Unary):
            operand = self._expression(expression.operand)
            if expression.operator == "+":
                return operand
            if expression.operator == "-":
                return -operand
            raise SemanticError(
                f"Unsupported unary operator '{expression.operator}'",
                expression.position,
            )

        if isinstance(expression, Binary):
            left = self._expression(expression.left)
            right = self._expression(expression.right)
            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right
            if expression.operator == "/":
                if right == 0:
                    raise SemanticError("Division by zero", expression.position)
                return left / right
            if expression.operator == "^":
                return left**right
            raise SemanticError(
                f"Unsupported binary operator '{expression.operator}'",
                expression.position,
            )

        if isinstance(expression, Percent):
            return self._expression(expression.value) / 100.0

        if isinstance(expression, FunctionCall):
            if expression.name != "sqrt":
                raise SemanticError(f"Unknown function '{expression.name}'", expression.position)
            value = self._expression(expression.argument)
            if value < 0:
                raise SemanticError("sqrt() argument must be non-negative", expression.position)
            return value**0.5

        raise SemanticError("Unsupported expression", getattr(expression, "position", None))
