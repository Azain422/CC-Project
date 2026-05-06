from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePosition:
    line: int
    column: int


class CompilerError(Exception):
    def __init__(self, message: str, position: SourcePosition | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self) -> str:
        if self.position is None:
            return self.message
        return f"{self.message} at line {self.position.line}, column {self.position.column}"


class LexicalError(CompilerError):
    pass


class SyntaxError(CompilerError):
    pass


class SemanticError(CompilerError):
    pass


class ExecutionError(CompilerError):
    pass



