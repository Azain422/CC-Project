from __future__ import annotations

from typing import List

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
    Statement,
    Unary,
)
from .errors import SourcePosition, SyntaxError
from .tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements: list[Statement] = []
        while not self._is_at_end():
            if self._match(TokenType.SEMICOLON):
                continue
            statements.append(self._statement())
            self._match(TokenType.SEMICOLON)
        return Program(statements)

    def _statement(self) -> Statement:
        if self._match(TokenType.PRINT):
            keyword = self._previous()
            value = self._expression()
            return PrintStatement(value, SourcePosition(keyword.line, keyword.column))

        if self._check(TokenType.IDENTIFIER) and self._check_next(TokenType.ASSIGN):
            name_token = self._advance()
            self._advance()
            value = self._expression()
            return Assignment(
                name_token.lexeme,
                value,
                SourcePosition(name_token.line, name_token.column),
            )

        value = self._expression()
        return ExpressionStatement(value, getattr(value, "position", None))

    def _expression(self) -> Expression:
        return self._additive()

    def _additive(self) -> Expression:
        expression = self._multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            token = self._previous()
            operator = token.lexeme
            right = self._multiplicative()
            expression = Binary(expression, operator, right, SourcePosition(token.line, token.column))
        return expression

    def _multiplicative(self) -> Expression:
        expression = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH):
            token = self._previous()
            operator = token.lexeme
            right = self._power()
            expression = Binary(expression, operator, right, SourcePosition(token.line, token.column))
        return expression

    def _power(self) -> Expression:
        expression = self._unary()
        if self._match(TokenType.CARET):
            token = self._previous()
            operator = token.lexeme
            right = self._power()
            expression = Binary(expression, operator, right, SourcePosition(token.line, token.column))
        return expression

    def _unary(self) -> Expression:
        if self._match(TokenType.PLUS, TokenType.MINUS):
            token = self._previous()
            operator = token.lexeme
            operand = self._unary()
            return Unary(operator, operand, SourcePosition(token.line, token.column))
        return self._postfix()

    def _postfix(self) -> Expression:
        expression = self._primary()
        while self._match(TokenType.PERCENT):
            token = self._previous()
            expression = Percent(expression, SourcePosition(token.line, token.column))
        return expression

    def _primary(self) -> Expression:
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return Number(float(token.lexeme), SourcePosition(token.line, token.column))

        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return Identifier(token.lexeme, SourcePosition(token.line, token.column))

        if self._match(TokenType.SQRT):
            token = self._previous()
            self._consume(TokenType.LPAREN, "Expected '(' after sqrt")
            argument = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after sqrt argument")
            return FunctionCall("sqrt", argument, SourcePosition(token.line, token.column))

        if self._match(TokenType.LPAREN):
            expression = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expression

        token = self._peek()
        raise SyntaxError(
            f"Unexpected token {token.lexeme!r}",
            SourcePosition(token.line, token.column),
        )

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        token = self._peek()
        raise SyntaxError(message, SourcePosition(token.line, token.column))

    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _check_next(self, token_type: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
