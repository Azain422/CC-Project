# VintageCalc - Retro Calculator Language

VintageCalc is a small compiler project that demonstrates the full compiler pipeline for a retro-style calculator language.

## Features

- Variables and assignments
- Arithmetic operators: `+`, `-`, `*`, `/`, `^`
- Postfix percentage operator: `%`
- Built-in `sqrt()` function
- `print` statements
- End-to-end compilation pipeline:
  - lexical analysis
  - syntax analysis
  - semantic analysis
  - intermediate code generation
  - optimization
  - interpretation

## Language Overview

### Tokens

- Keywords: `print`
- Identifiers: names such as `x`, `rate`, `amount`
- Numbers: integers and decimals
- Operators: `+ - * / ^ = %`
- Delimiters: `(` `)` `;`
- Comments: `//` to end of line

### Grammar Summary

```ebnf
program         ::= statement_list EOF
statement_list  ::= statement (";" statement)* ";"?
statement       ::= assignment | print_stmt | expression
assignment      ::= IDENTIFIER "=" expression
print_stmt      ::= "print" expression
expression      ::= additive
additive        ::= multiplicative (("+" | "-") multiplicative)*
multiplicative  ::= power (("*" | "/") power)*
power           ::= unary ("^" power)?
unary           ::= ("+" | "-") unary | postfix
postfix         ::= primary ("%")*
primary         ::= NUMBER | IDENTIFIER | function_call | "(" expression ")"
function_call   ::= "sqrt" "(" expression ")"
```

## Project Structure

- `compiler/lexer.py` - regex-based tokenizer
- `compiler/parser.py` - recursive descent parser
- `compiler/semantic.py` - symbol table and semantic checks
- `compiler/codegen.py` - AST to three-address code generator
- `compiler/optimizer.py` - constant folding and dead code elimination
- `compiler/execution.py` - TAC interpreter
- `main.py` - CLI entry point
- `tests/test_vintagecalc.py` - unittest suite

## CLI

Run the compiler with:

```bash
python compiler.py input.vc
python compiler.py input.vc --debug
python compiler.py --interactive
python compiler.py --gui
```

`main.py` remains available as the internal CLI implementation, but `compiler.py` is the supported command-line entry point.

### Debug Mode

`--debug` prints:

1. token stream
2. AST
3. generated IR
4. optimized IR
5. final output

### Interactive Mode

`--interactive` opens a simple prompt. Enter source lines and submit a blank line to execute.

### GUI Debug Studio

`--gui` opens a graphical debug viewer with separate tabs for source, tokens, AST, IR, optimized IR, output, and status. It is the easiest way to demonstrate the compiler phases during presentations.

## Examples

### Valid Program 1

```vc
x = 50 + 25;
print x;
```

### Valid Program 2

```vc
rate = 10%;
amount = 200 * (1 + rate);
print amount;
```

### Valid Program 3

```vc
a = 16;
b = sqrt(a);
c = (b + 4) ^ 2;
print c;
```

### Invalid Program 1

```vc
x = ;
print x;
```

### Invalid Program 2

```vc
print sqrt(9;
```

## Error Handling

- `LexicalError` for invalid characters
- `SyntaxError` for malformed expressions or statements
- `SemanticError` for undefined variables and invalid semantic conditions
- `ExecutionError` for runtime failures during interpretation

## Testing

Run the test suite with:

```bash
python -m unittest discover -s tests
```

The test suite includes five valid end-to-end programs and representative invalid cases.
