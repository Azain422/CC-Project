from __future__ import annotations

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
from .ir import Assign, BinaryOp, Call, IRProgram, LoadConst, LoadName, Print, UnaryOp


class IRGenerator:
    def __init__(self) -> None:
        self.instructions: list = []
        self.temp_index = 0

    def generate(self, program: Program) -> IRProgram:
        self.instructions.clear()
        self.temp_index = 0
        for statement in program.statements:
            self._statement(statement)
        return IRProgram(list(self.instructions))

    def _statement(self, statement) -> None:
        if isinstance(statement, Assignment):
            value = self._expression(statement.value)
            self.instructions.append(Assign(statement.name, value))
            return

        if isinstance(statement, PrintStatement):
            value = self._expression(statement.value)
            self.instructions.append(Print(value))
            return

        if isinstance(statement, ExpressionStatement):
            self._expression(statement.value)
            return

        raise TypeError(f"Unsupported statement type: {type(statement)!r}")

    def _expression(self, expression: Expression) -> str:
        if isinstance(expression, Number):
            temp = self._new_temp()
            self.instructions.append(LoadConst(temp, expression.value))
            return temp

        if isinstance(expression, Identifier):
            temp = self._new_temp()
            self.instructions.append(LoadName(temp, expression.name))
            return temp

        if isinstance(expression, Unary):
            operand = self._expression(expression.operand)
            temp = self._new_temp()
            self.instructions.append(UnaryOp(temp, expression.operator, operand))
            return temp

        if isinstance(expression, Binary):
            left = self._expression(expression.left)
            right = self._expression(expression.right)
            temp = self._new_temp()
            self.instructions.append(BinaryOp(temp, left, expression.operator, right))
            return temp

        if isinstance(expression, Percent):
            operand = self._expression(expression.value)
            temp = self._new_temp()
            self.instructions.append(BinaryOp(temp, operand, "/", self._const_name(100.0)))
            return temp

        if isinstance(expression, FunctionCall):
            argument = self._expression(expression.argument)
            temp = self._new_temp()
            self.instructions.append(Call(temp, expression.name, argument))
            return temp

        raise TypeError(f"Unsupported expression type: {type(expression)!r}")

    def _new_temp(self) -> str:
        self.temp_index += 1
        return f"t{self.temp_index}"

    def _const_name(self, value: float) -> str:
        temp = self._new_temp()
        self.instructions.append(LoadConst(temp, value))
        return temp
