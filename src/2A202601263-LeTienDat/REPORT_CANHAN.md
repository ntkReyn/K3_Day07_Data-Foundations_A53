# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Tiến Đạt
**Nhóm:** K3 - A53
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao có nghĩa là hai vector chỉ về cùng một hướng, nên ý nghĩa của hai câu/đoạn văn gần nhau về mặt biểu diễn embedding.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên cần đạt chuẩn tiếng Anh để tốt nghiệp."
- Câu B: "Để tốt nghiệp, sinh viên phải có chứng chỉ tiếng Anh."
- Tại sao tương đồng: Cả hai nói về cùng một quy định về chuẩn đầu ra tiếng Anh.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên cần đạt chuẩn tiếng Anh để tốt nghiệp."
- Câu B: "Học bổng nhập học sẽ bị hạ cấp nếu học lực không đạt."
- Tại sao khác: Hai câu nói về hai chủ đề khác nhau: tiếng Anh và học bổng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chú trọng vào hướng của vector, phù hợp hơn với ý nghĩa ngữ cảnh, trong khi khoảng cách Euclid bị ảnh hưởng nhiều bởi độ lớn của vector và ít phản ánh sự tương đồng về ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: bước nhảy = 500 - 50 = 450. Số chunk = floor((10000 - 500) / 450) + 1 = 22.
>
> **Đáp án:** 22 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm còn 400, nên cần nhiều chunk hơn để phủ kín cùng một đoạn văn bản. Độ chồng chéo nhiều hơn giúp giữ ngữ cảnh liên tục giữa các chunk, nhưng làm tăng số lượng chunk và độ dư thừa.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex để tách câu dựa trên dấu kết thúc câu như `.`, `!`, `?` rồi gom các câu thành từng chunk theo số câu tối đa. Trường hợp văn bản rỗng hoặc không có dấu câu rõ ràng thì trả về danh sách rỗng hoặc một chunk duy nhất để tránh lỗi.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán chia theo thứ tự separator ưu tiên như `\n\n`, `\n`, `. `, ` `, rồi đệ quy tiếp nếu đoạn vẫn quá dài. Base case là khi chiều dài đoạn nhỏ hơn hoặc bằng `chunk_size` hoặc không còn separator để dùng, lúc đó sẽ chia theo kích thước cố định.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi tài liệu được chuyển thành record gồm `content`, `metadata`, `embedding` và `doc_id`. Khi tìm kiếm, hệ thống tạo embedding cho câu hỏi, tính cosine similarity với từng record rồi sắp xếp giảm dần theo score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi thực hiện lọc metadata trước khi tính similarity để giảm không gian tìm kiếm và giữ kết quả đúng đối tượng. Khi xóa, hệ thống loại bỏ tất cả chunk có `metadata['doc_id']` trùng với doc_id cần xoá.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent tạo prompt có hai phần: context từ các chunk được truy xuất và câu hỏi của người dùng. Cách này giúp model trả lời dựa trên ngữ cảnh cụ thể thay vì đoán suy diễn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
python -m unittest tests.test_solution -v
...
Ran 42 tests in 0.038s

OK
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên cần đạt chuẩn tiếng Anh để tốt nghiệp | Để tốt nghiệp, sinh viên phải có chứng chỉ tiếng Anh | thấp | 0.1104 | Đúng |
| 2 | Học bổng nhập học được duy trì nếu đạt điểm trung bình | Học bổng sẽ bị hạ cấp khi học lực không đạt chuẩn | thấp | 0.0091 | Đúng |
| 3 | Nghỉ học tạm thời có thể xin lại sau khi nghỉ | Đăng ký môn học cần đúng thời hạn từng học kỳ | thấp | 0.0568 | Đúng |
| 4 | Tín chỉ tối thiểu mỗi học kỳ là 12 | Mỗi học kỳ cần đăng ký tối thiểu 12 tín chỉ | thấp | -0.1600 | Đúng |
| 5 | Trao đổi sinh viên ở nước ngoài là chương trình du học | Điều lệ học tập tại trường trong nước | thấp | 0.1333 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là nhiều cặp có ý nghĩa tương tự vẫn cho điểm similarity khá thấp khi dùng mock embeddings. Điều này cho thấy embeddings không chỉ phụ thuộc vào từ khóa mà còn phụ thuộc vào cách biểu diễn và chất lượng mô hình.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Yêu cầu tiếng Anh để tốt nghiệp là gì? | Chunk từ tài liệu quy định học thuật, không trực tiếp trả lời chuẩn tiếng Anh | 0.3981 | Không | Agent trả lời mang tính tổng quát hơn về quy định học tập |
| 2 | Điều kiện duy trì học bổng nhập học là gì? | Chunk từ tài liệu quy chế đào tạo, không phải tài liệu học bổng | 0.3009 | Không | Agent thiếu chi tiết về học bổng nhập học |
| 3 | Cách xin nghỉ học tạm thời và trở lại? | Chunk liên quan đến quy định học vụ, nhưng không phải chính là thủ tục nghỉ học | 0.4148 | Phần nào | Agent chỉ đưa được ngữ cảnh chung về học vụ |
| 4 | Số tín chỉ tối thiểu để đăng ký mỗi học kỳ là bao nhiêu? | Chunk từ tài liệu trao đổi sinh viên nước ngoài, không đúng chủ đề | 0.3810 | Không | Agent không trả lời đúng câu hỏi về tín chỉ |
| 5 | Quy trình trao đổi sinh viên nước ngoài như thế nào? | Chunk từ quy định học thuật, không phải tài liệu exchange | 0.3105 | Không | Agent chưa thể trả lời đúng và đầy đủ |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng metadata filter và lựa chọn tài liệu chất lượng có tác động rất lớn đến chất lượng retrieval. Khi cùng một câu hỏi nhưng dữ liệu tốt hơn và metadata rõ ràng, kết quả trả về sẽ chính xác hơn nhiều.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
