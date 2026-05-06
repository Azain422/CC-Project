from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    PRINT = auto()
    SQRT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    ASSIGN = auto()
    PERCENT = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
