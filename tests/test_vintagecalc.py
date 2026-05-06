from __future__ import annotations

import unittest

from compiler.codegen import IRGenerator
from compiler.errors import LexicalError, SemanticError, SyntaxError
from compiler.execution import IRInterpreter
from compiler.lexer import Lexer
from compiler.optimizer import Optimizer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer


def run_program(source: str) -> list[float]:
    program = Parser(Lexer().tokenize(source)).parse()
    SemanticAnalyzer().analyze(program)
    ir = IRGenerator().generate(program)
    optimized = Optimizer().optimize(ir)
    return IRInterpreter().execute(optimized)


class VintageCalcPipelineTests(unittest.TestCase):
    def test_program_1_basic_arithmetic(self) -> None:
        self.assertEqual(run_program("x = 50 + 25;\nprint x;\n"), [75.0])

    def test_program_2_percentage(self) -> None:
        self.assertEqual(run_program("rate = 10%;\namount = 200 * (1 + rate);\nprint amount;\n"), [220.0])

    def test_program_3_sqrt_and_power(self) -> None:
        self.assertEqual(run_program("a = 16;\nb = sqrt(a);\nc = (b + 4) ^ 2;\nprint c;\n"), [64.0])

    def test_program_4_constant_folding(self) -> None:
        self.assertEqual(run_program("x = (2 + 3) * 4;\nprint x;\n"), [20.0])

    def test_program_5_nested_expression(self) -> None:
        self.assertEqual(run_program("n = 9;\nprint sqrt(n) + 1;\n"), [4.0])

    def test_lexical_error(self) -> None:
        with self.assertRaises(LexicalError):
            Lexer().tokenize("x = @;")

    def test_syntax_error(self) -> None:
        with self.assertRaises(SyntaxError):
            Parser(Lexer().tokenize("print sqrt(9;")).parse()

    def test_semantic_error(self) -> None:
        program = Parser(Lexer().tokenize("print x;\n")).parse()
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(program)


if __name__ == "__main__":
    unittest.main()
