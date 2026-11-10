from .logic_ast import Formula, Atom, Not, And, Or, Implies, Iff

class Sequent:
    """Biểu diễn một dòng dẫn xuất trong giải thuật Vương Hạo: Γ ⊢ Δ"""
    def __init__(self, left: list, right: list):
        self.left = list(left)
        self.right = list(right)

    def to_str(self, unicode_sym: bool = True) -> str:
        turnstile = " ⊢ " if unicode_sym else " |- "
        left_str = ", ".join(f.to_str(unicode_sym) for f in self.left) or "∅"
        right_str = ", ".join(f.to_str(unicode_sym) for f in self.right) or "∅"
        return f"{left_str}{turnstile}{right_str}"

    def to_latex(self) -> str:
        left_str = ", ".join(f.to_latex() for f in self.left) or "\\emptyset"
        right_str = ", ".join(f.to_latex() for f in self.right) or "\\emptyset"
        return f"{left_str} \\vdash {right_str}"

    def is_axiom(self):
        """
        Kiểm tra điều kiện Tiên đề (Axiom Condition):
        Tồn tại ít nhất một công thức X xuất hiện đồng thời ở cả vế trái (Γ) và vế phải (Δ).
        Nếu có, trả về công thức X; nếu không trả về None.
        """
        for f_left in self.left:
            for f_right in self.right:
                if f_left == f_right:
                    return f_left
        return None

    def is_all_atoms(self) -> bool:
        """Kiểm tra xem cả 2 vế đã khử hoàn toàn về dạng biến nguyên tử (atoms) hay chưa."""
        return all(f.is_atom() for f in self.left) and all(f.is_atom() for f in self.right)

    def __str__(self):
        return self.to_str(unicode_sym=True)

class ProofNode:
    """Một nút trong cây chứng minh giải thuật Vương Hạo."""
    def __init__(self, node_id: int, sequent: Sequent, depth: int = 0):
        self.node_id = node_id
        self.sequent = sequent
        self.depth = depth
        self.status = "PENDING"  # PENDING | PROVEN_AXIOM | INVALID | EXPANDED
        self.axiom_formula = None
        self.rule_applied = None
        self.children = []
        self.counter_example = None

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def to_dict(self) -> dict:
        """Chuyển đổi cây chứng minh sang dạng JSON để hiển thị trực quan trên giao diện Web."""
        return {
            "node_id": self.node_id,
            "depth": self.depth,
            "sequent_str": self.sequent.to_str(unicode_sym=True),
            "sequent_latex": self.sequent.to_latex(),
            "left": [f.to_str(unicode_sym=True) for f in self.sequent.left],
            "right": [f.to_str(unicode_sym=True) for f in self.sequent.right],
            "status": self.status,
            "axiom_formula": self.axiom_formula.to_str(unicode_sym=True) if self.axiom_formula else None,
            "rule_applied": self.rule_applied,
            "counter_example": self.counter_example,
            "children": [child.to_dict() for child in self.children]
        }

class WangHaoProver:
    """
    Động cơ chứng minh định lý tự động theo giải thuật Vương Hạo (Hao Wang 1960).
    Áp dụng chiến lược ưu tiên:
    1. Kiểm tra Tiên đề (Axiom) ngay lập tức nếu Γ ∩ Δ ≠ ∅.
    2. Ưu tiên các quy tắc KHÔNG PHÂN NHÁNH trước (¬L, ¬R, ∧L, ∨R, →R).
    3. Sau đó áp dụng các quy tắc PHÂN NHÁNH (∧R, ∨L, →L, ↔L, ↔R).
    4. Trích xuất phản ví dụ (Counter-example) nếu công thức không phải hằng đúng.
    """

    def __init__(self):
        self.node_counter = 0

    def prove(self, gamma: list, delta: list) -> dict:
        """
        Chứng minh suy kéo Vương Hạo: Γ ⊢ Δ
        Trả về kết quả chứng minh, cây dẫn xuất và phản ví dụ (nếu có).
        """
        self.node_counter = 0
        root_seq = Sequent(gamma, delta)
        self.node_counter += 1
        root_node = ProofNode(self.node_counter, root_seq, depth=0)

        all_leaves = []
        self._expand_node(root_node, all_leaves)

        is_theorem = all(leaf.status == "PROVEN_AXIOM" for leaf in all_leaves)
        
        counter_examples = []
        for leaf in all_leaves:
            if leaf.status == "INVALID" and leaf.counter_example:
                counter_examples.append(leaf.counter_example)

        return {
            "is_valid": is_theorem,
            "root_sequent": root_seq.to_str(unicode_sym=True),
            "root_latex": root_seq.to_latex(),
            "total_nodes": self.node_counter,
            "total_leaves": len(all_leaves),
            "proven_branches": sum(1 for l in all_leaves if l.status == "PROVEN_AXIOM"),
            "counter_examples": counter_examples,
            "proof_tree": root_node.to_dict(),
            "text_trace": self._generate_text_trace(root_node)
        }

    def _expand_node(self, node: ProofNode, all_leaves: list):
        seq = node.sequent

        # 1. KIỂM TRA ĐIỀU KIỆN TIÊN ĐỀ (AXIOM CHECK)
        axiom = seq.is_axiom()
        if axiom is not None:
            node.status = "PROVEN_AXIOM"
            node.axiom_formula = axiom
            node.rule_applied = f"TIÊN ĐỀ (AXIOM): Công thức '{axiom.to_str()}' xuất hiện ở cả vế trái và vế phải!"
            all_leaves.append(node)
            return

        # 2. KIỂM TRA ĐIỀU KIỆN DỪNG THẤT BẠI (CHỈ CÒN CÁC BIẾN NGUYÊN TỬ VÀ KHÔNG TRÙNG NHAU)
        if seq.is_all_atoms():
            node.status = "INVALID"
            # Trích xuất phản ví dụ: Gán True cho tất cả biến ở vế trái, False cho tất cả biến ở vế phải
            assignment = {}
            for f in seq.left:
                assignment[f.name] = True
            for f in seq.right:
                assignment[f.name] = False
            node.counter_example = assignment
            node.rule_applied = f"BẾ TẮC (INVALID): Cả hai vế chỉ còn biến đơn lẻ nhưng không có biến nào trùng nhau!"
            all_leaves.append(node)
            return

        # 3. CHIẾN LƯỢC: ÁP DỤNG QUY TẮC KHÔNG PHÂN NHÁNH TRƯỚC (NON-BRANCHING RULES)
        
        # Rule ¬L: Γ, ¬A ⊢ Δ  ==>  Γ ⊢ Δ, A
        for i, f in enumerate(seq.left):
            if isinstance(f, Not):
                new_left = seq.left[:i] + seq.left[i+1:]
                new_right = seq.right + [f.operand]
                self._apply_single_child(node, new_left, new_right, 
                                        f"Quy tắc (¬L): Chuyển phủ định '{f.to_str()}' ở vế trái sang vế phải thành '{f.operand.to_str()}'",
                                        all_leaves)
                return

        # Rule ¬R: Γ ⊢ Δ, ¬A  ==>  Γ, A ⊢ Δ
        for i, f in enumerate(seq.right):
            if isinstance(f, Not):
                new_left = seq.left + [f.operand]
                new_right = seq.right[:i] + seq.right[i+1:]
                self._apply_single_child(node, new_left, new_right,
                                        f"Quy tắc (¬R): Chuyển phủ định '{f.to_str()}' ở vế phải sang vế trái thành '{f.operand.to_str()}'",
                                        all_leaves)
                return

        # Rule ∧L: Γ, A ∧ B ⊢ Δ  ==>  Γ, A, B ⊢ Δ
        for i, f in enumerate(seq.left):
            if isinstance(f, And):
                new_left = seq.left[:i] + [f.left, f.right] + seq.left[i+1:]
                new_right = list(seq.right)
                self._apply_single_child(node, new_left, new_right,
                                        f"Quy tắc (∧L): Tách phép hội '{f.to_str()}' ở vế trái thành 2 sự thật độc lập: '{f.left.to_str()}', '{f.right.to_str()}'",
                                        all_leaves)
                return

        # Rule ∨R: Γ ⊢ Δ, A ∨ B  ==>  Γ ⊢ Δ, A, B
        for i, f in enumerate(seq.right):
            if isinstance(f, Or):
                new_left = list(seq.left)
                new_right = seq.right[:i] + [f.left, f.right] + seq.right[i+1:]
                self._apply_single_child(node, new_left, new_right,
                                        f"Quy tắc (∨R): Khử phép tuyển '{f.to_str()}' ở vế phải thành: '{f.left.to_str()}', '{f.right.to_str()}'",
                                        all_leaves)
                return

        # Rule →R: Γ ⊢ Δ, A → B  ==>  Γ, A ⊢ Δ, B
        for i, f in enumerate(seq.right):
            if isinstance(f, Implies):
                new_left = seq.left + [f.left]
                new_right = seq.right[:i] + [f.right] + seq.right[i+1:]
                self._apply_single_child(node, new_left, new_right,
                                        f"Quy tắc (→R): Khử phép kéo theo '{f.to_str()}' ở vế phải: chuyển tiền đề '{f.left.to_str()}' sang vế trái và giữ '{f.right.to_str()}' ở vế phải",
                                        all_leaves)
                return

        # 4. ÁP DỤNG QUY TẮC PHÂN NHÁNH (BRANCHING RULES)

        # Rule ∧R: Γ ⊢ Δ, A ∧ B  ==>  (Γ ⊢ Δ, A) VÀ (Γ ⊢ Δ, B)
        for i, f in enumerate(seq.right):
            if isinstance(f, And):
                # Nhánh 1
                left1 = list(seq.left)
                right1 = seq.right[:i] + [f.left] + seq.right[i+1:]
                # Nhánh 2
                left2 = list(seq.left)
                right2 = seq.right[:i] + [f.right] + seq.right[i+1:]

                self._apply_branching(node, left1, right1, left2, right2,
                                     f"Quy tắc (∧R): Tách phép hội '{f.to_str()}' ở vế phải thành 2 nhánh con (cả 2 phải đúng)",
                                     all_leaves)
                return

        # Rule ∨L: Γ, A ∨ B ⊢ Δ  ==>  (Γ, A ⊢ Δ) VÀ (Γ, B ⊢ Δ)
        for i, f in enumerate(seq.left):
            if isinstance(f, Or):
                # Nhánh 1
                left1 = seq.left[:i] + [f.left] + seq.left[i+1:]
                right1 = list(seq.right)
                # Nhánh 2
                left2 = seq.left[:i] + [f.right] + seq.left[i+1:]
                right2 = list(seq.right)

                self._apply_branching(node, left1, right1, left2, right2,
                                     f"Quy tắc (∨L): Tách phép tuyển '{f.to_str()}' ở vế trái thành 2 nhánh xét trường hợp",
                                     all_leaves)
                return

        # Rule →L: Γ, A → B ⊢ Δ  ==>  (Γ ⊢ Δ, A) VÀ (Γ, B ⊢ Δ)
        for i, f in enumerate(seq.left):
            if isinstance(f, Implies):
                # Nhánh 1: giả thiết tiền đề sai (A nằm ở vế phải)
                left1 = seq.left[:i] + seq.left[i+1:]
                right1 = seq.right + [f.left]
                # Nhánh 2: giả thiết kết luận đúng (B nằm ở vế trái)
                left2 = seq.left[:i] + [f.right] + seq.left[i+1:]
                right2 = list(seq.right)

                self._apply_branching(node, left1, right1, left2, right2,
                                     f"Quy tắc (→L): Khử phép kéo theo '{f.to_str()}' ở vế trái: Tách thành 2 nhánh (Γ ⊢ Δ, {f.left.to_str()}) và (Γ, {f.right.to_str()} ⊢ Δ)",
                                     all_leaves)
                return

        # Rule ↔L: Γ, A ↔ B ⊢ Δ  ==>  (Γ, A, B ⊢ Δ) VÀ (Γ ⊢ Δ, A, B)
        for i, f in enumerate(seq.left):
            if isinstance(f, Iff):
                # Nhánh 1: Cả A và B đều Đúng
                left1 = seq.left[:i] + [f.left, f.right] + seq.left[i+1:]
                right1 = list(seq.right)
                # Nhánh 2: Cả A và B đều Sai
                left2 = seq.left[:i] + seq.left[i+1:]
                right2 = seq.right + [f.left, f.right]

                self._apply_branching(node, left1, right1, left2, right2,
                                     f"Quy tắc (↔L): Tách phép tương đương '{f.to_str()}' ở vế trái thành 2 nhánh (A, B cùng Đúng hoặc cùng Sai)",
                                     all_leaves)
                return

        # Rule ↔R: Γ ⊢ Δ, A ↔ B  ==>  (Γ, A ⊢ Δ, B) VÀ (Γ, B ⊢ Δ, A)
        for i, f in enumerate(seq.right):
            if isinstance(f, Iff):
                # Nhánh 1: A -> B
                left1 = seq.left + [f.left]
                right1 = seq.right[:i] + [f.right] + seq.right[i+1:]
                # Nhánh 2: B -> A
                left2 = seq.left + [f.right]
                right2 = seq.right[:i] + [f.left] + seq.right[i+1:]

                self._apply_branching(node, left1, right1, left2, right2,
                                     f"Quy tắc (↔R): Tách phép tương đương '{f.to_str()}' ở vế phải thành 2 chiều (A → B và B → A)",
                                     all_leaves)
                return

    def _apply_single_child(self, node: ProofNode, new_left: list, new_right: list, rule_name: str, all_leaves: list):
        node.status = "EXPANDED"
        node.rule_applied = rule_name
        self.node_counter += 1
        child_seq = Sequent(new_left, new_right)
        child_node = ProofNode(self.node_counter, child_seq, depth=node.depth + 1)
        node.children.append(child_node)
        self._expand_node(child_node, all_leaves)

    def _apply_branching(self, node: ProofNode, left1: list, right1: list, left2: list, right2: list, rule_name: str, all_leaves: list):
        node.status = "EXPANDED"
        node.rule_applied = rule_name
        
        # Nhánh 1
        self.node_counter += 1
        child1_seq = Sequent(left1, right1)
        child1 = ProofNode(self.node_counter, child1_seq, depth=node.depth + 1)
        node.children.append(child1)

        # Nhánh 2
        self.node_counter += 1
        child2_seq = Sequent(left2, right2)
        child2 = ProofNode(self.node_counter, child2_seq, depth=node.depth + 1)
        node.children.append(child2)

        self._expand_node(child1, all_leaves)
        self._expand_node(child2, all_leaves)

    def _generate_text_trace(self, node: ProofNode, indent: str = "") -> list:
        """Sinh ra chuỗi nhật ký từng bước suy diễn dạng văn bản có thụt lề dễ đọc."""
        lines = []
        status_sym = ""
        if node.status == "PROVEN_AXIOM":
            status_sym = " [✓ TIÊN ĐỀ HỢP LỆ]"
        elif node.status == "INVALID":
            status_sym = " [✗ BẾ TẮC - KHÔNG THỂ CHỨNG MINH]"

        lines.append(f"{indent}• [{node.node_id}] {node.sequent.to_str()}{status_sym}")
        if node.rule_applied:
            lines.append(f"{indent}  ↳ {node.rule_applied}")
            
        for child in node.children:
            lines.extend(self._generate_text_trace(child, indent + "    "))
        return lines
