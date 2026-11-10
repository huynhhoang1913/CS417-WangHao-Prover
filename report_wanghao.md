# BÁO CÁO ĐỒ ÁN MÔN HỌC: TRÍ TUỆ NHÂN TẠO (CS417)
**TRƯỜNG KHOA HỌC MÁY TÍNH (SCA) - ĐẠI HỌC DUY TÂN**

---

## ĐỀ TÀI:
### XÂY DỰNG HỆ THỐNG CHỨNG MINH ĐỊNH LÝ TỰ ĐỘNG BẰNG GIẢI THUẬT VƯƠNG HẠO (WANG HAO'S ALGORITHM)

* **Học phần:** Trí tuệ Nhân tạo (CS417)
* **Bộ môn:** Trí tuệ Nhân tạo & Khoa học Dữ liệu (SCA)
* **Sinh viên thực hiện:** [Họ và tên của bạn]
* **Mã số sinh viên:** [MSSV của bạn]
* **Lớp:** CS417 [...]

---

## MỤC LỤC BÁO CÁO
1. **CHƯƠNG 1: TỔNG QUAN VỀ CHỨNG MINH ĐỊNH LÝ TỰ ĐỘNG**
   * 1.1. Lịch sử hình thành và Giải thuật Vương Hạo (Hao Wang 1960)
   * 1.2. Vai trò của Suy luận tự động (Automated Reasoning) trong Trí tuệ Nhân tạo
   * 1.3. Mục tiêu và phạm vi của đề tài
2. **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & GIẢI THUẬT VƯƠNG HẠO**
   * 2.1. Ngữ nghĩa Logic mệnh đề và Biểu diễn dạng Dòng dẫn xuất (Sequent)
   * 2.2. Điều kiện Tiên đề dừng thành công (Axiom Condition)
   * 2.3. Hệ thống 10 Quy tắc khử phép toán logic của Vương Hạo
     * 2.3.1. Các quy tắc không phân nhánh (¬L, ¬R, ∧L, ∨R, →R)
     * 2.3.2. Các quy tắc phân nhánh (∧R, ∨L, →L, ↔L, ↔R)
   * 2.4. Cơ chế trích xuất Phản ví dụ (Counter-Model) khi chứng minh thất bại
3. **CHƯƠNG 3: THIẾT KẾ & CÀI ĐẶT HỆ THỐNG**
   * 3.1. Thiết kế Bộ phân tích cú pháp (Lexer & Recursive Descent Parser)
   * 3.2. Cấu trúc Cây cú pháp trừu tượng (Abstract Syntax Tree - AST)
   * 3.3. Thuật toán duyệt và sinh Cây chứng minh (Proof Tree Builder)
   * 3.4. Xây dựng giao diện Web tương tác và Công cụ dòng lệnh CLI
4. **CHƯƠNG 4: KỊCH BẢN THỰC NGHIỆM & ĐÁNH GIÁ**
   * 4.1. Bài toán thực tế 1: Điều kiện tiên quyết môn học ĐH Duy Tân (SCA - DTU)
   * 4.2. Bài toán thực tế 2: Vụ án ngoại phạm suy luận điều tra
   * 4.3. Bài toán thực tế 3: Phát hiện ngụy biện khẳng định hệ quả (Chẩn đoán mạng)
   * 4.4. Kiểm thử các định luật logic kinh điển (De Morgan, Modus Ponens, Bài trung)
5. **CHƯƠNG 5: KỊCH BẢN BẢO VỆ ĐỒ ÁN TRƯỚC GIẢNG VIÊN (ORAL DEFENSE SCRIPT)**
6. **CHƯƠNG 6: KẾT LUẬN & HƯỚNG PHÁT TRIỂN**
   * 6.1. Kết quả đạt được
   * 6.2. Hướng mở rộng sang Logic vị từ cấp một (First-Order Logic)
7. **TÀI LIỆU THAM KHẢO**

---

## NỘI DUNG CHI TIẾT CÁC CHƯƠNG TRỌNG TÂM

### CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI
Năm 1960, nhà logic học và toán học người Mỹ gốc Hoa - **Hao Wang (Vương Hạo)** đã công bố công trình lịch sử *"Toward Mechanical Mathematics"* trên tạp chí IBM Journal of Research and Development. Ông đã lập trình một hệ thống trên máy tính IBM 704 chứng minh thành công toàn bộ hơn 350 định lý logic mệnh đề trong bộ sách kinh điển *Principia Mathematica* của Russell và Whitehead chỉ trong vài phút.

Đề tài này tái hiện lại giải thuật kinh điển của Vương Hạo kết hợp công nghệ phần mềm hiện đại:
1. Cho phép người dùng nhập bài toán từ ngôn ngữ tự nhiên, ánh xạ sang biến mệnh đề.
2. Tự động thiết lập dòng suy kéo $\Gamma \vdash \Delta$.
3. Tự động sinh cây dẫn xuất từng bước, minh họa trực quan quy tắc biến đổi.
4. Tự động trích xuất phản ví dụ (Counter-example) nếu công thức không phải là hằng đúng.

---

### CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & GIẢI THUẬT VƯƠNG HẠO

#### 2.1. Dạng dòng dẫn xuất (Sequent Form)
Bài toán được đưa về dạng kiểm tra quan hệ suy kéo:
$$\Gamma \vdash \Delta \quad \iff \quad A_1, A_2, \dots, A_m \vdash B_1, B_2, \dots, B_n$$
*Ý nghĩa ngữ nghĩa:* Hội các tiền đề vế trái kéo theo Tuyển các kết luận vế phải:
$$(A_1 \land A_2 \land \dots \land A_m) \implies (B_1 \lor B_2 \lor \dots \lor B_n)$$

#### 2.2. Điều kiện Tiên đề (Axiom Check)
Một dòng dẫn xuất $\Gamma \vdash \Delta$ được xem là **Tiên đề (Đúng đắn hiển nhiên)** khi và chỉ khi:
$$\Gamma \cap \Delta \neq \emptyset$$
(Tồn tại ít nhất một công thức $X$ vừa thuộc $\Gamma$ vừa thuộc $\Delta$. Vì nếu $X$ đúng thì cả vế trái và vế phải đều đúng, kéo theo là chân lý).

#### 2.3. Hệ thống 10 Quy tắc rút gọn:
1. **$\neg L$ (Phủ định trái):** $\Gamma, \neg A \vdash \Delta \implies \Gamma \vdash \Delta, A$
2. **$\neg R$ (Phủ định phải):** $\Gamma \vdash \Delta, \neg A \implies \Gamma, A \vdash \Delta$
3. **$\land L$ (Hội trái):** $\Gamma, A \land B \vdash \Delta \implies \Gamma, A, B \vdash \Delta$
4. **$\land R$ (Hội phải - Tách 2 nhánh):** $\Gamma \vdash \Delta, A \land B \implies (\Gamma \vdash \Delta, A) \text{ VÀ } (\Gamma \vdash \Delta, B)$
5. **$\lor L$ (Tuyển trái - Tách 2 nhánh):** $\Gamma, A \lor B \vdash \Delta \implies (\Gamma, A \vdash \Delta) \text{ VÀ } (\Gamma, B \vdash \Delta)$
6. **$\lor R$ (Tuyển phải):** $\Gamma \vdash \Delta, A \lor B \implies \Gamma \vdash \Delta, A, B$
7. **$\rightarrow L$ (Kéo theo trái - Tách 2 nhánh):** $\Gamma, A \rightarrow B \vdash \Delta \implies (\Gamma \vdash \Delta, A) \text{ VÀ } (\Gamma, B \vdash \Delta)$
8. **$\rightarrow R$ (Kéo theo phải):** $\Gamma \vdash \Delta, A \rightarrow B \implies \Gamma, A \vdash \Delta, B$
9. **$\leftrightarrow L$ (Tương đương trái - Tách 2 nhánh):** $\Gamma, A \leftrightarrow B \vdash \Delta \implies (\Gamma, A, B \vdash \Delta) \text{ VÀ } (\Gamma \vdash \Delta, A, B)$
10. **$\leftrightarrow R$ (Tương đương phải - Tách 2 nhánh):** $\Gamma \vdash \Delta, A \leftrightarrow B \implies (\Gamma, A \vdash \Delta, B) \text{ VÀ } (\Gamma, B \vdash \Delta, A)$

#### 2.4. Cơ chế trích xuất Phản ví dụ (Counter-Model)
Khi một nhánh của cây dẫn xuất bị khử về dạng chỉ toàn các biến nguyên tử mà $\Gamma \cap \Delta = \emptyset$:
* Gán tất cả biến trong $\Gamma$ giá trị **TRUE**.
* Gán tất cả biến trong $\Delta$ giá trị **FALSE**.
Bộ giá trị này đảm bảo: $\bigwedge \Gamma = \text{True}$ và $\bigvee \Delta = \text{False}$, biến toàn bộ biểu thức suy kéo thành $\text{True} \to \text{False} = \text{False}$ (chứng minh phản chứng!).

---

### CHƯƠNG 4: THỰC NGHIỆM VÀ KẾT QUẢ ĐẠT ĐƯỢC

#### Kịch bản 1: Điều kiện môn học ĐH Duy Tân (SCA - DTU)
* **Phát biểu:** "Nếu hoàn thành Lập trình cơ bản ($P$) và Toán rời rạc ($Q$) thì đủ điều kiện học Cấu trúc dữ liệu ($R$). Sinh viên đã học xong cả $P$ và $Q$. Hỏi có chắc chắn được học $R$ không?"
* **Biểu diễn:** $\{(P \land Q) \rightarrow R, \; P \land Q\} \vdash R$
* **Kết quả cây dẫn xuất:**
  * Bước 1: Khử $\land L$ trên $P \land Q$ ở vế trái $\implies (P \land Q) \rightarrow R, P, Q \vdash R$
  * Bước 2: Khử $\rightarrow L$ trên vế trái, tách làm 2 nhánh:
    * Nhánh 1: $P, Q \vdash R, P \land Q$
      * Khử $\land R$ tách thành:
        * $P, Q \vdash R, P$ $\to$ **Tiên đề (trùng $P$)** [✓]
        * $P, Q \vdash R, Q$ $\to$ **Tiên đề (trùng $Q$)** [✓]
    * Nhánh 2: $R, P, Q \vdash R$ $\to$ **Tiên đề (trùng $R$)** [✓]
* **Kết luận:** Hằng đúng 100%! Cả 3 nhánh con đều hợp lệ.

#### Kịch bản 2: Bẫy ngụy biện logic (Chẩn đoán sự cố mạng)
* **Biểu diễn:** $(D \lor C) \rightarrow L, L, \neg C \vdash D$
* **Kết quả:** **CHỨNG MINH THẤT BẠI!**
* **Phản ví dụ tìm được:** $D = \text{False}, C = \text{False}, L = \text{True}$.
* **Ý nghĩa:** Mạng có thể bị mất kết nối do nguyên nhân thứ ba (như cúp điện), không thể suy diễn khẳng định chắc chắn là do bị tấn công DDoS ($D$).

---

### CHƯƠNG 5: KỊCH BẢN THUYẾT TRÌNH BẢO VỆ TRƯỚC GIẢNG VIÊN (SCRIPT NÓI MẪU)

Khi đứng trước thầy cô, bạn có thể tự tin trình bày theo đúng kịch bản 3 bước sau:

> *"Kính thưa Thầy/Cô, em xin phép trình bày đề tài: **Hệ thống Chứng minh Định lý Tự động bằng Giải thuật Vương Hạo**.*
>
> *Đề tài của em được tiến hành theo **3 bước chuẩn hóa khoa học**:*
>
> 1. ***Bước 1: Tiếp nhận và mô hình hóa bài toán thực tế:***
>    *Hệ thống nhận vào các phát biểu ngôn ngữ tự nhiên (ví dụ như bài toán kiểm tra điều kiện học phần Cấu trúc dữ liệu tại ĐH Duy Tân từ các môn Lập trình cơ bản và Toán rời rạc), bóc tách thành các biến mệnh đề $P, Q, R$ và đưa về dạng dòng dẫn xuất chuẩn tắc của Vương Hạo: $\Gamma \vdash \Delta$.*
>
> 2. ***Bước 2: Xây dựng Bộ phân tích cú pháp (Parser):***
>    *Em đã tự lập trình bộ Lexer và Recursive Descent Parser hỗ trợ đầy đủ độ ưu tiên toán học của các phép toán $\neg, \land, \lor, \rightarrow, \leftrightarrow$ cùng bàn phím ký hiệu logic ảo, chuyển đổi biểu thức chuỗi thành Cây cú pháp trừu tượng (AST).*
>
> 3. ***Bước 3: Thực thi giải thuật Vương Hạo và trực quan hóa cây chứng minh:***
>    *Hệ thống áp dụng chiến lược ưu tiên các luật không phân nhánh trước, sau đó mới phân nhánh xét trường hợp. Khi tất cả các lá đều đạt điều kiện Tiên đề ($\Gamma \cap \Delta \neq \emptyset$), chương trình khẳng định biểu thức là **Hằng đúng (Tautology)**. Đặc biệt, nếu định lý không đúng (như trường hợp bẫy ngụy biện logic), hệ thống sẽ lập tức **trích xuất một Phản ví dụ (Counter-Model)** chỉ rõ bộ giá trị chân trị cụ thể làm cho tiền đề Đúng nhưng kết luận Sai.*
>
> *Sau đây em xin phép demo trực tiếp hệ thống trên Web và Terminal dòng lệnh ạ!"*
