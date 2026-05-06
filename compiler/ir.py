from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class IRInstruction:
    pass


@dataclass(frozen=True)
class Label(IRInstruction):
    name: str


@dataclass(frozen=True)
class LoadConst(IRInstruction):
    target: str
    value: float


@dataclass(frozen=True)
class LoadName(IRInstruction):
    target: str
    name: str


@dataclass(frozen=True)
class Assign(IRInstruction):
    target: str
    value: str


@dataclass(frozen=True)
class UnaryOp(IRInstruction):
    target: str
    operator: str
    operand: str


@dataclass(frozen=True)
class BinaryOp(IRInstruction):
    target: str
    left: str
    operator: str
    right: str


@dataclass(frozen=True)
class Call(IRInstruction):
    target: str
    name: str
    argument: str


@dataclass(frozen=True)
class Print(IRInstruction):
    value: str


@dataclass
class IRProgram:
    instructions: List[IRInstruction] = field(default_factory=list)
