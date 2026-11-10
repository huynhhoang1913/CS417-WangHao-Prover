from abc import ABC, abstractmethod

class Formula(ABC):
    """Lớp cơ sở trừu tượng cho tất cả các biểu thức logic mệnh đề."""
    
    @abstractmethod
    def to_str(self, unicode_sym: bool = True) -> str:
        pass

    @abstractmethod
    def to_latex(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, assignment: dict) -> bool:
        pass

    @abstractmethod
    def get_atoms(self) -> set:
        pass

    @abstractmethod
    def is_atom(self) -> bool:
        pass

    def __str__(self):
        return self.to_str(unicode_sym=True)

    def __repr__(self):
        return self.to_str(unicode_sym=False)

class Atom(Formula):
    """Mệnh đề nguyên tử (biến mệnh đề như P, Q, R, A, B...)."""
    def __init__(self, name: str):
        self.name = name.strip()

    def to_str(self, unicode_sym: bool = True) -> str:
        return self.name

    def to_latex(self) -> str:
        return self.name

    def evaluate(self, assignment: dict) -> bool:
        return assignment.get(self.name, False)

    def get_atoms(self) -> set:
        return {self.name}

    def is_atom(self) -> bool:
        return True

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self):
        return hash(("Atom", self.name))

class Not(Formula):
    """Phép phủ định (¬A hoặc ~A)."""
    def __init__(self, operand: Formula):
        self.operand = operand

    def to_str(self, unicode_sym: bool = True) -> str:
        sym = "¬" if unicode_sym else "~"
        if self.operand.is_atom():
            return f"{sym}{self.operand.to_str(unicode_sym)}"
        return f"{sym}({self.operand.to_str(unicode_sym)})"

    def to_latex(self) -> str:
        if self.operand.is_atom():
            return f"\\neg {self.operand.to_latex()}"
        return f"\\neg ({self.operand.to_latex()})"

    def evaluate(self, assignment: dict) -> bool:
        return not self.operand.evaluate(assignment)

    def get_atoms(self) -> set:
        return self.operand.get_atoms()

    def is_atom(self) -> bool:
        return False

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("Not", self.operand))

class BinaryFormula(Formula, ABC):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def get_atoms(self) -> set:
        return self.left.get_atoms().union(self.right.get_atoms())

    def is_atom(self) -> bool:
        return False

    def _wrap(self, child: Formula, unicode_sym: bool) -> str:
        s = child.to_str(unicode_sym)
        if isinstance(child, (And, Or, Implies, Iff)):
            return f"({s})"
        return s

    def _wrap_latex(self, child: Formula) -> str:
        s = child.to_latex()
        if isinstance(child, (And, Or, Implies, Iff)):
            return f"({s})"
        return s

class And(BinaryFormula):
    """Phép hội (A ∧ B hoặc A & B)."""
    def to_str(self, unicode_sym: bool = True) -> str:
        sym = " ∧ " if unicode_sym else " & "
        return f"{self._wrap(self.left, unicode_sym)}{sym}{self._wrap(self.right, unicode_sym)}"

    def to_latex(self) -> str:
        return f"{self._wrap_latex(self.left)} \\land {self._wrap_latex(self.right)}"

    def evaluate(self, assignment: dict) -> bool:
        return self.left.evaluate(assignment) and self.right.evaluate(assignment)

    def __eq__(self, other):
        return isinstance(other, And) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("And", self.left, self.right))

class Or(BinaryFormula):
    """Phép tuyển (A ∨ B hoặc A | B)."""
    def to_str(self, unicode_sym: bool = True) -> str:
        sym = " ∨ " if unicode_sym else " | "
        return f"{self._wrap(self.left, unicode_sym)}{sym}{self._wrap(self.right, unicode_sym)}"

    def to_latex(self) -> str:
        return f"{self._wrap_latex(self.left)} \\lor {self._wrap_latex(self.right)}"

    def evaluate(self, assignment: dict) -> bool:
        return self.left.evaluate(assignment) or self.right.evaluate(assignment)

    def __eq__(self, other):
        return isinstance(other, Or) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("Or", self.left, self.right))

class Implies(BinaryFormula):
    """Phép kéo theo (A → B hoặc A -> B)."""
    def to_str(self, unicode_sym: bool = True) -> str:
        sym = " → " if unicode_sym else " -> "
        return f"{self._wrap(self.left, unicode_sym)}{sym}{self._wrap(self.right, unicode_sym)}"

    def to_latex(self) -> str:
        return f"{self._wrap_latex(self.left)} \\to {self._wrap_latex(self.right)}"

    def evaluate(self, assignment: dict) -> bool:
        # P -> Q tương đương not P or Q
        return (not self.left.evaluate(assignment)) or self.right.evaluate(assignment)

    def __eq__(self, other):
        return isinstance(other, Implies) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("Implies", self.left, self.right))

class Iff(BinaryFormula):
    """Phép tương đương (A ↔ B hoặc A <-> B)."""
    def to_str(self, unicode_sym: bool = True) -> str:
        sym = " ↔ " if unicode_sym else " <-> "
        return f"{self._wrap(self.left, unicode_sym)}{sym}{self._wrap(self.right, unicode_sym)}"

    def to_latex(self) -> str:
        return f"{self._wrap_latex(self.left)} \\leftrightarrow {self._wrap_latex(self.right)}"

    def evaluate(self, assignment: dict) -> bool:
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)

    def __eq__(self, other):
        return isinstance(other, Iff) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("Iff", self.left, self.right))
