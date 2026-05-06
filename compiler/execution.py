from __future__ import annotations

import math

from .errors import ExecutionError
from .ir import Assign, BinaryOp, Call, IRProgram, LoadConst, LoadName, Print, UnaryOp


class IRInterpreter:
    def __init__(self) -> None:
        self.state: dict[str, float] = {}

    def execute(self, program: IRProgram) -> list[float]:
        outputs: list[float] = []
        for instruction in program.instructions:
            if isinstance(instruction, LoadConst):
                self.state[instruction.target] = self._normalize(instruction.value)
                continue

            if isinstance(instruction, LoadName):
                self.state[instruction.target] = self._resolve(instruction.name)
                continue

            if isinstance(instruction, UnaryOp):
                operand = self._resolve(instruction.operand)
                if instruction.operator == "+":
                    self.state[instruction.target] = self._normalize(operand)
                elif instruction.operator == "-":
                    self.state[instruction.target] = self._normalize(-operand)
                else:
                    raise ExecutionError(f"Unsupported unary operator '{instruction.operator}'")
                continue

            if isinstance(instruction, BinaryOp):
                left = self._resolve(instruction.left)
                right = self._resolve(instruction.right)
                self.state[instruction.target] = self._normalize(
                    self._apply_binary(instruction.operator, left, right)
                )
                continue

            if isinstance(instruction, Call):
                argument = self._resolve(instruction.argument)
                if instruction.name != "sqrt":
                    raise ExecutionError(f"Unknown function '{instruction.name}'")
                if argument < 0:
                    raise ExecutionError("sqrt() argument must be non-negative")
                self.state[instruction.target] = self._normalize(math.sqrt(argument))
                continue

            if isinstance(instruction, Assign):
                self.state[instruction.target] = self._normalize(self._resolve(instruction.value))
                continue

            if isinstance(instruction, Print):
                outputs.append(self._normalize(self._resolve(instruction.value)))
                continue

            raise ExecutionError(f"Unsupported instruction '{type(instruction).__name__}'")

        return outputs

    def _resolve(self, name: str) -> float:
        if name not in self.state:
            raise ExecutionError(f"Undefined value '{name}' at runtime")
        return self.state[name]

    def _apply_binary(self, operator: str, left: float, right: float) -> float:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise ExecutionError("Division by zero")
            return left / right
        if operator == "^":
            return left**right
        raise ExecutionError(f"Unsupported binary operator '{operator}'")

    def _normalize(self, value: float) -> float:
        return float(round(value, 10))
