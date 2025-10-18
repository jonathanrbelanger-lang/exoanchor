import ast
import tokenize
from io import BytesIO
from collections import namedtuple

# A simple structure to hold error information
LintError = namedtuple('LintError', ['line', 'col', 'code', 'message'])

class ASTVisitor(ast.NodeVisitor):
    """A visitor to find specific patterns in the AST."""
    def __init__(self):
        self.errors = []

    def visit_If(self, node: ast.If):
        # EXA401: Check for assignment in an if statement
        if isinstance(node.test, ast.Assign):
            error = LintError(
                node.test.lineno,
                node.test.col_offset,
                'EXA401',
                "Assignment (=) used in a conditional context, did you mean comparison (==)?"
            )
            self.errors.append(error)
        self.generic_visit(node)

class SyntaxChecker:
    """Orchestrates the syntax checking process for a given Python file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.source_bytes = b""
        self.errors = []

    def check(self) -> list[LintError]:
        """Runs the full two-pass check and returns a list of errors."""
        try:
            with open(self.file_path, 'rb') as f:
                self.source_bytes = f.read()
        except IOError as e:
            self.errors.append(LintError(0, 0, 'EXA001', f"Cannot read file: {e}"))
            return self.errors

        # Pass 1: Lexical analysis using the tokenize module
        token_errors = self._run_token_checks()
        self.errors.extend(token_errors)

        # Proceed to Pass 2 only if no fatal lexical errors were found
        if not self.errors:
            try:
                tree = ast.parse(self.source_bytes, filename=self.file_path)
                ast_errors = self._run_ast_checks(tree)
                self.errors.extend(ast_errors)
            except (SyntaxError, IndentationError, TabError) as e:
                error = self._format_syntax_error(e)
                self.errors.append(error)
        
        self.errors.sort(key=lambda err: err.line)
        return self.errors

    def _run_token_checks(self) -> list[LintError]:
        """Checks for lexical errors like unbalanced brackets."""
        errors = []
        bracket_stack = []
        try:
            # THE FIX: Use `tokenize.tokenize`, the modern, byte-based tokenizer.
            # This function is designed to work directly with a byte stream,
            # which is exactly what we get from reading the file in 'rb' mode.
            tokens = tokenize.tokenize(BytesIO(self.source_bytes).readline)
            for token in tokens:
                if token.type == tokenize.OP:
                    if token.string in '([{':
                        bracket_stack.append(token)
                    elif token.string in ')]}':
                        if not bracket_stack:
                            errors.append(LintError(token.start[0], token.start[1], 'EXA102', f"Unmatched closing bracket '{token.string}'"))
                        else:
                            opening_bracket = bracket_stack.pop()
                            match_map = {'(': ')', '[': ']', '{': '}'}
                            if match_map[opening_bracket.string] != token.string:
                                errors.append(LintError(token.start[0], token.start[1], 'EXA102', f"Mismatched closing bracket '{token.string}', expected '{match_map[opening_bracket.string]}' to close bracket at line {opening_bracket.start[0]}"))
        except tokenize.TokenError as e:
            # EXA201: Catches unterminated strings
            errors.append(LintError(e.args[1][0], e.args[1][1], 'EXA201', e.args[0]))
        
        # EXA101: Check for any unclosed brackets left on the stack
        for bracket in bracket_stack:
            errors.append(LintError(bracket.start[0], bracket.start[1], 'EXA101', f"Unclosed opening bracket '{bracket.string}'"))
            
        return errors

    def _run_ast_checks(self, tree: ast.AST) -> list[LintError]:
        """Runs AST-based checks for contextual errors."""
        visitor = ASTVisitor()
        visitor.visit(tree)
        return visitor.errors

    def _format_syntax_error(self, e: SyntaxError) -> LintError:
        """Maps Python's SyntaxError to a custom LintError."""
        line, col = e.lineno or 1, e.offset or 1
        message = e.msg
        code = 'EXA000' # Default code
        
        if isinstance(e, IndentationError):
            code = 'EXA402' if 'unexpected indent' in message else 'EXA403'
        elif isinstance(e, TabError):
            code = 'EXA303'
        
        return LintError(line, col, code, message)