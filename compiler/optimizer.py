from __future__ import annotations

import math

from .ir import (
    Assign,
    BinaryOp,
    Call,
    IRInstruction,
    IRProgram,
    LoadConst,
    LoadName,
    Print,
    UnaryOp,
)


class Optimizer:
    def optimize(self, program: IRProgram) -> IRProgram:
        folded = self._constant_fold(program)
        return self._dead_code_eliminate(folded)

    def _constant_fold(self, program: IRProgram) -> IRProgram:
        known_constants: dict[str, float] = {}
        optimized: list[IRInstruction] = []

        for instruction in program.instructions:
            if isinstance(instruction, LoadConst):
                known_constants[instruction.target] = instruction.value
                optimized.append(instruction)
                continue

            if isinstance(instruction, LoadName):
                if instruction.name in known_constants:
                    value = known_constants[instruction.name]
                    known_constants[instruction.target] = value
                    optimized.append(LoadConst(instruction.target, value))
                else:
                    known_constants.pop(instruction.target, None)
                    optimized.append(instruction)
                continue

            if isinstance(instruction, UnaryOp):
                operand = known_constants.get(instruction.operand)
                if operand is not None and instruction.operator in {"+", "-"}:
                    value = operand if instruction.operator == "+" else -operand
                    known_constants[instruction.target] = value
                    optimized.append(LoadConst(instruction.target, value))
                else:
                    known_constants.pop(instruction.target, None)
                    optimized.append(instruction)
                continue

            if isinstance(instruction, BinaryOp):
                left = known_constants.get(instruction.left)
                right = known_constants.get(instruction.right)
                if left is not None and right is not None:
                    value = self._apply_binary(instruction.operator, left, right)
                    known_constants[instruction.target] = value
                    optimized.append(LoadConst(instruction.target, value))
                else:
                    known_constants.pop(instruction.target, None)
                    optimized.append(instruction)
                continue

            if isinstance(instruction, Call):
                argument = known_constants.get(instruction.argument)
                if argument is not None and instruction.name == "sqrt" and argument >= 0:
                    value = math.sqrt(argument)
                    known_constants[instruction.target] = value
                    optimized.append(LoadConst(instruction.target, value))
                else:
                    known_constants.pop(instruction.target, None)
                    optimized.append(instruction)
                continue

            if isinstance(instruction, Assign):
                value = known_constants.get(instruction.value)
                if value is not None:
                    known_constants[instruction.target] = value
                else:
                    known_constants.pop(instruction.target, None)
                optimized.append(instruction)
                continue

            if isinstance(instruction, Print):
                optimized.append(instruction)
                continue

            optimized.append(instruction)

        return IRProgram(optimized)

    def _dead_code_eliminate(self, program: IRProgram) -> IRProgram:
        live: set[str] = set()
        kept_reversed: list[IRInstruction] = []

        for instruction in reversed(program.instructions):
            if isinstance(instruction, Print):
                live.add(instruction.value)
                kept_reversed.append(instruction)
                continue

            if isinstance(instruction, Assign):
                live.add(instruction.value)
                kept_reversed.append(instruction)
                continue

            used_names = self._used_names(instruction)
            if self._defines_temp(instruction):
                target = self._target_name(instruction)
                if target in live:
                    live.discard(target)
                    live.update(used_names)
                    kept_reversed.append(instruction)
                else:
                    continue
            else:
                live.update(used_names)
                kept_reversed.append(instruction)

        kept_reversed.reverse()
        return IRProgram(kept_reversed)

    def _apply_binary(self, operator: str, left: float, right: float) -> float:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            return left / right
        if operator == "^":
            return left**right
        raise ValueError(f"Unsupported operator: {operator}")

    def _used_names(self, instruction: IRInstruction) -> set[str]:
        if isinstance(instruction, LoadConst):
            return set()
        if isinstance(instruction, LoadName):
            return {instruction.name}
        if isinstance(instruction, UnaryOp):
            return {instruction.operand}
        if isinstance(instruction, BinaryOp):
            return {instruction.left, instruction.right}
        if isinstance(instruction, Call):
            return {instruction.argument}
        return set()

    def _defines_temp(self, instruction: IRInstruction) -> bool:
        return isinstance(instruction, (LoadConst, LoadName, UnaryOp, BinaryOp, Call))

    def _target_name(self, instruction: IRInstruction) -> str:
        if isinstance(instruction, LoadConst):
            return instruction.target
        if isinstance(instruction, LoadName):
            return instruction.target
        if isinstance(instruction, UnaryOp):
            return instruction.target
        if isinstance(instruction, BinaryOp):
            return instruction.target
        if isinstance(instruction, Call):
            return instruction.target
        raise TypeError(f"Instruction has no target: {instruction!r}")
