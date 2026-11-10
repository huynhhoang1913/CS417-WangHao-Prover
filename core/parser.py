import re
from .logic_ast import Formula, Atom, Not, And, Or, Implies, Iff

class LogicParser:
    """
    Bộ phân tích cú pháp (Lexer & Parser) cho biểu thức logic mệnh đề.
    Hỗ trợ độ ưu tiên chuẩn:
    ¬ (NOT) > ∧ (AND) > ∨ (OR) > → (IMPLIES - kết hợp phải) > ↔ (IFF).
    Hỗ trợ cả ký hiệu toán học (¬, ∧, ∨, →, ↔) và ký hiệu bàn phím (~, &, |, ->, <->).
    """

    TOKEN_SPEC = [
        ("IFF", r"<->|<=>|↔|\biff\b"),
        ("IMPLIES", r"->|=>|→|\bimplies\b"),
        ("OR", r"\||∨|\bor\b|\+"),
        ("AND", r"&|∧|\band\b|\*"),
        ("NOT", r"~|!|¬|\bnot\b"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("TURNSTILE", r"\|-|\b⊢\b|\|="),
        ("COMMA", r","),
        ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("SKIP", r"[ \t\n\r]+"),
        ("MISMATCH", r"."),
    ]

    TOKEN_REGEX = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in TOKEN_SPEC)

    def tokenize(self, text: str):
        tokens = []
        for mo in re.finditer(self.TOKEN_REGEX, text, re.IGNORECASE):
            kind = mo.lastgroup
            val = mo.group()
            if kind == "SKIP" or kind in ("LBRACE", "RBRACE"):
                continue
            elif kind == "MISMATCH":
                raise ValueError(f"Ký tự không hợp lệ trong biểu thức logic: '{val}'")
            else:
                tokens.append((kind, val))
        tokens.append(("EOF", ""))
        return tokens

    def parse_formula(self, text: str) -> Formula:
        """Phân tích một công thức logic duy nhất."""
        tokens = self.tokenize(text)
        parser = _FormulaParser(tokens)
        formula = parser.parse_iff()
        if parser.current_token()[0] != "EOF":
            raise ValueError(f"Dư thừa cú pháp ở cuối biểu thức: '{parser.current_token()[1]}'")
        return formula

    def parse_formula_list(self, text: str) -> list:
        """Phân tích danh sách công thức ngăn cách bởi dấu phẩy (ví dụ: 'P, Q, P -> R')."""
        if not text.strip():
            return []
        tokens = self.tokenize(text)
        parser = _FormulaParser(tokens)
        formulas = []
        while parser.current_token()[0] != "EOF":
            f = parser.parse_iff()
            formulas.append(f)
            if parser.current_token()[0] == "COMMA":
                parser.advance()
            elif parser.current_token()[0] == "EOF":
                break
            else:
                raise ValueError(f"Kỳ vọng dấu phẩy ',' nhưng gặp '{parser.current_token()[1]}'")
        return formulas

    def parse_sequent(self, text: str) -> tuple:
        """
        Phân tích biểu thức Vương Hạo dạng: Gamma |- Delta
        Ví dụ: 'P, P -> Q |- Q'
        Hoặc nếu không có dấu '|-' thì hiểu là kiểm tra tính hằng đúng của một công thức: |- Formula
        """
        raw = text.strip()
        # Tìm dấu turnstile |- hoặc ⊢
        match = re.search(r"(\|-|⊢|\|=)", raw)
        if match:
            sep = match.group(0)
            left_part, right_part = raw.split(sep, 1)
            gamma = self.parse_formula_list(left_part)
            delta = self.parse_formula_list(right_part)
            return gamma, delta
        else:
            # Nếu người dùng chỉ nhập một công thức duy nhất, bài toán trở thành chứng minh hằng đúng: |- F
            f = self.parse_formula(raw)
            return [], [f]

class _FormulaParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.tokens[self.pos]
        if token[0] != "EOF":
            self.pos += 1
        return token

    def match(self, token_type):
        if self.current_token()[0] == token_type:
            return self.advance()
        return None

    # Precedence: Iff < Implies < Or < And < Not < Primary

    def parse_iff(self) -> Formula:
        expr = self.parse_implies()
        while self.match("IFF"):
            right = self.parse_implies()
            expr = Iff(expr, right)
        return expr

    def parse_implies(self) -> Formula:
        expr = self.parse_or()
        # Implies là kết hợp phải (right-associative): A -> B -> C <=> A -> (B -> C)
        if self.match("IMPLIES"):
            right = self.parse_implies()
            expr = Implies(expr, right)
        return expr

    def parse_or(self) -> Formula:
        expr = self.parse_and()
        while self.match("OR"):
            right = self.parse_and()
            expr = Or(expr, right)
        return expr

    def parse_and(self) -> Formula:
        expr = self.parse_not()
        while self.match("AND"):
            right = self.parse_not()
            expr = And(expr, right)
        return expr

    def parse_not(self) -> Formula:
        if self.match("NOT"):
            operand = self.parse_not()
            return Not(operand)
        return self.parse_primary()

    def parse_primary(self) -> Formula:
        token = self.current_token()
        if token[0] == "IDENT":
            self.advance()
            return Atom(token[1])
        elif self.match("LPAREN"):
            expr = self.parse_iff()
            if not self.match("RPAREN"):
                raise ValueError("Thiếu dấu ngoặc đóng ')' tương ứng!")
            return expr
        else:
            raise ValueError(f"Cú pháp biểu thức không hợp lệ tại vị trí '{token[1]}'")
