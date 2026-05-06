from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .errors import LexicalError, SourcePosition
from .tokens import Token, TokenType


@dataclass(frozen=True)
class _TokenSpec:
    type: TokenType
    pattern: re.Pattern[str]


class Lexer:
    _token_specs: tuple[_TokenSpec, ...] = (
        _TokenSpec(TokenType.PRINT, re.compile(r"print\b")),
        _TokenSpec(TokenType.NUMBER, re.compile(r"\d+(?:\.\d+)?")),
        _TokenSpec(TokenType.IDENTIFIER, re.compile(r"[A-Za-z_][A-Za-z0-9_]*")),
        _TokenSpec(TokenType.PLUS, re.compile(r"\+")),
        _TokenSpec(TokenType.MINUS, re.compile(r"-")),
        _TokenSpec(TokenType.STAR, re.compile(r"\*")),
        _TokenSpec(TokenType.SLASH, re.compile(r"/")),
        _TokenSpec(TokenType.CARET, re.compile(r"\^")),
        _TokenSpec(TokenType.ASSIGN, re.compile(r"=")),
        _TokenSpec(TokenType.PERCENT, re.compile(r"%")),
        _TokenSpec(TokenType.LPAREN, re.compile(r"\(")),
        _TokenSpec(TokenType.RPAREN, re.compile(r"\)")),
        _TokenSpec(TokenType.SEMICOLON, re.compile(r";")),
    )

    def tokenize(self, source: str) -> List[Token]:
        tokens: list[Token] = []
        index = 0
        line = 1
        column = 1
        length = len(source)

        while index < length:
            character = source[index]

            if character in " \t\r":
                index += 1
                column += 1
                continue

            if character == "\n":
                index += 1
                line += 1
                column = 1
                continue

            if source.startswith("//", index):
                index = self._consume_comment(source, index)
                line, column = self._recompute_position(source, index)
                continue

            matched_token = self._match_token(source, index)
            if matched_token is None:
                raise LexicalError(
                    f"Invalid character {character!r}",
                    SourcePosition(line, column),
                )

            token_type, lexeme = matched_token
            tokens.append(Token(token_type, lexeme, line, column))
            index += len(lexeme)
            column += len(lexeme)

        tokens.append(Token(TokenType.EOF, "", line, column))
        return tokens

    def _match_token(self, source: str, index: int) -> tuple[TokenType, str] | None:
        best_type: TokenType | None = None
        best_lexeme = ""

        for spec in self._token_specs:
            match = spec.pattern.match(source, index)
            if match is None:
                continue
            lexeme = match.group(0)
            if len(lexeme) > len(best_lexeme):
                best_type = spec.type
                best_lexeme = lexeme

        if best_type is None:
            return None

        if best_type == TokenType.IDENTIFIER and best_lexeme == "sqrt":
            return TokenType.SQRT, best_lexeme

        return best_type, best_lexeme

    def _consume_comment(self, source: str, index: int) -> int:
        while index < len(source) and source[index] != "\n":
            index += 1
        return index

    def _recompute_position(self, source: str, index: int) -> tuple[int, int]:
        line = 1
        column = 1
        for character in source[:index]:
            if character == "\n":
                line += 1
                column = 1
            else:
                column += 1
        return line, column
