import sys
import os
import json

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.append(os.path.dirname(__file__))

from core.parser import LogicParser
from core.wang_hao import WangHaoProver
from core.counter_example import CounterExampleVerifier

LIB_PATH = os.path.join(os.path.dirname(__file__), "examples", "problem_library.json")

def load_library():
    with open(LIB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_prover_on_sequent(sequent_str: str, var_dict: dict = None):
    parser = LogicParser()
    prover = WangHaoProver()

    print("\n" + "=" * 75)
    print("      HỆ THỐNG CHỨNG MINH ĐỊNH LÝ TỰ ĐỘNG - GIẢI THUẬT VƯƠNG HẠO (HAO WANG)")
    print("=" * 75)

    if var_dict:
        print("\n[BƯỚC 1: BIỂU DIỄN MỆNH ĐỀ TỪ BÀI TOÁN THỰC TẾ]")
        for k, v in var_dict.items():
            print(f"  • Biến '{k}': \"{v}\"")

    try:
        gamma, delta = parser.parse_sequent(sequent_str)
    except Exception as e:
        print(f"\n❌ Lỗi phân tích cú pháp (Parser Error): {e}")
        return

    print(f"\n[BƯỚC 2: THIẾT LẬP DẠNG SUY KÉO VƯƠNG HẠO (Γ ⊢ Δ)]")
    left_str = ", ".join(f.to_str() for f in gamma) or "∅"
    right_str = ", ".join(f.to_str() for f in delta) or "∅"
    print(f"  Biểu thức đầu vào : {sequent_str}")
    print(f"  Dạng chuẩn tắc    : {left_str}  ⊢  {right_str}")

    print(f"\n[BƯỚC 3: QUÁ TRÌNH KHỬ PHÉP TOÁN VÀ XÂY DỰNG CÂY CHỨNG MINH]")
    print("-" * 75)
    result = prover.prove(gamma, delta)

    for line in result["text_trace"]:
        print(line)

    print("-" * 75)
    print("\n[BƯỚC 4: KẾT LUẬN CUỐI CÙNG]")
    if result["is_valid"]:
        print("  🎉 KẾT QUẢ: ĐỊNH LÝ ĐÃ ĐƯỢC CHỨNG MINH THÀNH CÔNG (HẰNG ĐÚNG / TAUTOLOGY)!")
        print(f"  • Tổng số nút trong cây dẫn xuất: {result['total_nodes']} nút.")
        print(f"  • Số nhánh con được kiểm chứng   : {result['proven_branches']} / {result['total_leaves']} nhánh đều là Tiên đề (Axiom).")
        print("  • Mọi trường hợp chân trị đều thỏa mãn. Suy luận logic là hoàn toàn vững chắc.")
    else:
        print("  ⚠️ KẾT QUẢ: KHÔNG PHẢI HẰNG ĐÚNG (CHỨNG MINH THẤT BẠI)!")
        print(f"  • Phát hiện {len(result['counter_examples'])} nhánh bế tắc không thể đưa về Tiên đề.")
        
        # In phản ví dụ
        if result["counter_examples"]:
            ce = result["counter_examples"][0]
            print("\n  🔍 [PHẢN VÍ DỤ / COUNTER-EXAMPLE LÀM SAI ĐỊNH LÝ]:")
            verify = CounterExampleVerifier.verify_counter_example(gamma, delta, ce)
            for var_name, bool_val in verify["assignment"].items():
                meaning = f" (tức là: {var_dict[var_name]})" if var_dict and var_name in var_dict else ""
                print(f"    • Gán {var_name} = {bool_val}{meaning}")
            print(f"    => {verify['explanation']}")

def main():
    library = load_library()

    while True:
        print("\n" + "=" * 70)
        print("  CS417 - TRÍ TUỆ NHÂN TẠO | ĐẠI HỌC DUY TÂN - TRƯỜNG KHMT (SCA)")
        print("     CHỨNG MINH ĐỊNH LÝ TỰ ĐỘNG BẰNG GIẢI THUẬT VƯƠNG HẠO")
        print("=" * 70)
        print("1. Chọn bài toán mẫu từ thư viện (ĐH Duy Tân, Conan, De Morgan, Modus Ponens...)")
        print("2. Nhập biểu thức suy kéo Vương Hạo tùy ý (VD: (P & Q) -> R, P & Q |- R)")
        print("3. Tự định nghĩa bài toán thực tế và chuyển đổi sang mệnh đề")
        print("4. Thoát")

        choice = input("\nNhập lựa chọn của bạn (1/2/3/4, mặc định 1): ").strip() or "1"

        if choice == "1":
            print("\n--- THƯ VIỆN BÀI TOÁN MẪU ---")
            for idx, item in enumerate(library):
                tag = "[Thực tế]" if item["category"] == "real_life" else "[Kinh điển]"
                print(f"{idx + 1}. {tag} {item['name']}")
                print(f"   Dạng logic: {item['sequent']}")

            p_choice = input(f"\nChọn bài toán (1-{len(library)}, mặc định 1): ").strip() or "1"
            selected = library[int(p_choice) - 1]

            print(f"\n📝 Đề bài phát biểu: \"{selected['natural_language']}\"")
            run_prover_on_sequent(selected["sequent"], selected.get("variables"))

        elif choice == "2":
            print("\nNhập công thức logic theo cú pháp:")
            print("  • Phủ định: ~ hoặc ! hoặc ¬ (VD: ~P)")
            print("  • Phép hội: & hoặc ∧ (VD: P & Q)")
            print("  • Phép tuyển: | hoặc ∨ (VD: P | Q)")
            print("  • Kéo theo: -> hoặc → (VD: P -> Q)")
            print("  • Tương đương: <-> hoặc ↔ (VD: P <-> Q)")
            print("  • Vế trái và Vế phải ngăn cách bằng: |- hoặc ⊢ (VD: P, P -> Q |- Q)")
            seq_input = input("\nNhập biểu thức Vương Hạo: ").strip()
            if seq_input:
                run_prover_on_sequent(seq_input)

        elif choice == "3":
            print("\n--- TỰ ĐỊNH NGHĨA BÀI TOÁN THỰC TẾ ---")
            print("Nhập các biến mệnh đề đại diện cho các sự kiện thực tế:")
            vars_map = {}
            while True:
                var = input("Tên ký hiệu biến (VD: P, Q, Enter để kết thúc): ").strip().upper()
                if not var:
                    break
                meaning = input(f"Ý nghĩa của biến '{var}': ").strip()
                vars_map[var] = meaning

            premises = input("\nNhập các tiền đề (ngăn cách bởi dấu phẩy, VD: P -> Q, P): ").strip()
            conclusion = input("Nhập kết luận cần chứng minh (VD: Q): ").strip()

            full_seq = f"{premises} |- {conclusion}" if premises else f"|- {conclusion}"
            run_prover_on_sequent(full_seq, vars_map)

        else:
            print("Tạm biệt bạn!")
            break

if __name__ == "__main__":
    main()
