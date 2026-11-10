from .logic_ast import Formula

class CounterExampleVerifier:
    """
    Module phân tích và kiểm chứng phản ví dụ (Counter-Model / Falsifying Assignment).
    Khi giải thuật Vương Hạo kết luận một định lý KHÔNG ĐÚNG (không phải hằng đúng),
    module này sẽ chứng minh bằng bảng giá trị chân lý cụ thể:
    Làm cho toàn bộ tiền đề (Vế trái) = TRUE và toàn bộ kết luận (Vế phải) = FALSE.
    """

    @staticmethod
    def verify_counter_example(gamma: list, delta: list, assignment: dict) -> dict:
        # Đảm bảo tất cả các biến xuất hiện đều có giá trị (nếu chưa gán thì mặc định False)
        all_atoms = set()
        for f in gamma + delta:
            all_atoms.update(f.get_atoms())

        full_assignment = {}
        for a in all_atoms:
            full_assignment[a] = assignment.get(a, False)

        left_evaluations = []
        left_all_true = True
        for f in gamma:
            val = f.evaluate(full_assignment)
            left_evaluations.append({
                "formula": f.to_str(),
                "value": val
            })
            if not val:
                left_all_true = False

        right_evaluations = []
        right_any_true = False
        for f in delta:
            val = f.evaluate(full_assignment)
            right_evaluations.append({
                "formula": f.to_str(),
                "value": val
            })
            if val:
                right_any_true = True

        # Trạng thái suy kéo: Left_Conjunction -> Right_Disjunction
        # Bị làm sai khi Left_Conjunction = True VÀ Right_Disjunction = False
        is_falsified = left_all_true and (not right_any_true)

        return {
            "assignment": full_assignment,
            "left_evaluations": left_evaluations,
            "right_evaluations": right_evaluations,
            "premises_conjunction": left_all_true,
            "conclusions_disjunction": right_any_true,
            "is_counter_example_valid": is_falsified,
            "explanation": (
                f"Với phép gán: {full_assignment}, ta có: "
                f"Vế trái (tiền đề) = {left_all_true}, Vế phải (kết luận) = {right_any_true}. "
                f"Suy kéo {left_all_true} → {right_any_true} nhận giá trị FALSE (Sai)!"
            )
        }
