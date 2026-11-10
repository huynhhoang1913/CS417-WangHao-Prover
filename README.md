# CS417 - ĐỒ ÁN TRÍ TUỆ NHÂN TẠO (TRƯỜNG KHOA HỌC MÁY TÍNH - ĐH DUY TÂN)
## Đề tài: Hệ thống Chứng minh Định lý Tự động bằng Giải thuật Vương Hạo (Wang Hao's Sequent Calculus Prover)

---

### 1. Giới thiệu tổng quan
Hệ thống chứng minh tự động các định lý trong logic mệnh đề dựa trên phương pháp **Dòng dẫn xuất (Sequent Calculus)** của nhà logic học **Hao Wang (Vương Hạo - 1960)**.
Phần mềm hỗ trợ:
1. **Phân tích cú pháp biểu thức logic (Parser & Lexer):** Hỗ trợ đầy đủ độ ưu tiên: $\neg > \land > \lor > \rightarrow > \leftrightarrow$ và các ký tự bàn phím (`~`, `&`, `|`, `->`, `<->`, `|-`).
2. **Cơ chế dẫn xuất Vương Hạo:** Áp dụng hệ thống 10 quy tắc biến đổi rút gọn vế trái ($\Gamma$) và vế phải ($\Delta$) của dòng suy kéo $\Gamma \vdash \Delta$.
3. **Kiểm tra Tiên đề (Axiom Check):** Tự động phát hiện khi nào một nhánh đã được chứng minh ($\Gamma \cap \Delta \neq \emptyset$).
4. **Trích xuất Phản ví dụ (Counter-Model):** Nếu công thức KHÔNG PHẢI là hằng đúng, hệ thống lập tức tìm ra bảng giá trị chân lý làm cho tiền đề Đúng mà kết luận Sai.
5. **Giao diện trực quan hóa:** Web Dashboard với cây chứng minh tương tác (Visual Proof Tree), xuất mã LaTeX và Bàn phím ký hiệu toán học ảo.

---

### 2. Cấu trúc thư mục mã nguồn
```
d:\CS417\
│
├── core/
│   ├── logic_ast.py           # Cây cú pháp trừu tượng (AST) cho các toán tử logic
│   ├── parser.py              # Bộ phân tích từ vựng và cú pháp (Recursive Descent)
│   ├── wang_hao.py            # Động cơ giải thuật Vương Hạo & Cây dẫn xuất
│   └── counter_example.py     # Module trích xuất và kiểm chứng Phản ví dụ
│
├── examples/
│   └── problem_library.json   # Thư viện bài toán thực tế (ĐH Duy Tân, Conan, Ngụy biện...)
│
├── templates/
│   └── index.html             # Giao diện Web Dashboard trực quan
├── static/
│   ├── css/style.css          # CSS giao diện sắc nét
│   └── js/app.js              # Xử lý render cây chứng minh, bàn phím ký hiệu, tiến trình
│
├── app.py                     # Máy chủ Web (Flask)
├── cli_wanghao.py             # Công cụ chạy dòng lệnh Terminal tương tác
├── report_wanghao.md          # Đề cương & Báo cáo học thuật chi tiết nộp giảng viên
└── README.md                  # Hướng dẫn cài đặt và sử dụng
```

---

### 3. Hướng dẫn sử dụng

#### Cách 1: Khởi chạy Giao diện Web (Khuyên dùng khi báo cáo & demo)
Mở PowerShell tại thư mục `d:\CS417` và chạy:
```powershell
python app.py
```
Sau đó mở trình duyệt (Chrome/Edge) truy cập: **`http://127.0.0.1:5000`**

* Chọn bài toán mẫu từ menu thả xuống (Bài toán ĐH Duy Tân, Vụ án Conan, Ngụy biện logic...).
* Bấm **"CHỨNG MINH ĐỊNH LÝ"**: Cây chứng minh trực quan sẽ xuất hiện với các nhánh Tiên đề (màu xanh lá) hoặc nhánh Bế tắc (màu đỏ).
* Nếu định lý sai: Bảng phân tích Phản ví dụ sẽ hiện ra chỉ rõ giá trị gán cho các biến.
* Có thể xuất biểu thức LaTeX bằng nút **"Sao chép LaTeX"**.

---

#### Cách 2: Khởi chạy Giao diện Dòng lệnh CLI (Dành cho kiểm tra nhanh)
```powershell
python cli_wanghao.py
```
Có menu chọn:
1. *Chọn bài toán mẫu từ thư viện.*
2. *Nhập biểu thức Vương Hạo tùy ý (VD: `(P & Q) -> R, P & Q |- R`).*
3. *Tự nhập đề bài toán thực tế và gán nhãn biến.*

---

### 4. Báo cáo học thuật & Script thuyết trình
Xem chi tiết file: [report_wanghao.md](file:///d:/CS417/report_wanghao.md) để lấy toàn bộ nội dung thuyết minh và lời thoại mẫu 3 bước khoa học khi trình bày trước hội đồng giảng viên.
