from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .errors import SourcePosition


@dataclass(frozen=True)
class Program:
    statements: List[Statement]


class Statement:
    pass


@dataclass(frozen=True)
class Assignment(Statement):
    name: str
    value: Expression
    position: SourcePosition | None = None


@dataclass(frozen=True)
class PrintStatement(Statement):
    value: Expression
    position: SourcePosition | None = None


@dataclass(frozen=True)
class ExpressionStatement(Statement):
    value: Expression
    position: SourcePosition | None = None


class Expression:
    pass


@dataclass(frozen=True)
class Number(Expression):
    value: float
    position: SourcePosition | None = None


@dataclass(frozen=True)
class Identifier(Expression):
    name: str
    position: SourcePosition | None = None


@dataclass(frozen=True)
class Unary(Expression):
    operator: str
    operand: Expression
    position: SourcePosition | None = None


@dataclass(frozen=True)
class Binary(Expression):
    left: Expression
    operator: str
    right: Expression
    position: SourcePosition | None = None


@dataclass(frozen=True)
class Percent(Expression):
    value: Expression
    position: SourcePosition | None = None


@dataclass(frozen=True)
class FunctionCall(Expression):
    name: str
    argument: Expression
    position: SourcePosition | None = None

