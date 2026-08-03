# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thế Khôi — MSSV: 2A202601439
**Nhóm:** A53
**Ngày:** 03/08/2026


**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Hai vector embedding có hướng gần nhau, nên hai câu thường có nội dung hoặc ý nghĩa tương tự. Điểm càng gần 1 thì mức tương đồng ngữ nghĩa càng cao.

**Ví dụ có độ tương tự CAO:**

- Câu A: Điều kiện tiếng Anh để được xét tốt nghiệp là gì?
- Câu B: Sinh viên phải đáp ứng yêu cầu năng lực tiếng Anh nào trước khi tốt nghiệp?
- Tại sao tương đồng: Cả hai đều hỏi cùng một điều kiện tốt nghiệp, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Điều kiện tham gia chương trình trao đổi OSEP là gì?
- Câu B: Thư viện mở cửa đến mấy giờ?
- Tại sao khác: Hai câu đề cập hai dịch vụ độc lập: trao đổi sinh viên và thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

Cosine so sánh hướng của vector, vì vậy tập trung vào ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn vector hoặc độ dài văn bản. Điều này phù hợp hơn khi embedding được chuẩn hoá để tìm các câu cùng ý.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunks?**

Phép tính: `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11) = 23`.

**Đáp án:** 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

`ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400) = 25`, nên số chunk tăng từ 23 lên 25. Overlap lớn hơn giữ được ngữ cảnh ở ranh giới chunk, nhưng làm tăng số vector, chi phí lưu trữ và thời gian tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk` — hướng tiếp cận:**

Hàm dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết thúc câu, đồng thời giữ dấu câu ở câu trước. Văn bản rỗng/chỉ có khoảng trắng trả về danh sách rỗng; câu cuối không có dấu kết thúc vẫn được giữ. Các câu sau đó được ghép theo `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split` — hướng tiếp cận:**

Thuật toán thử lần lượt `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là chuỗi rỗng để ưu tiên giữ nguyên đoạn, dòng rồi đến câu. Nếu một phần vượt `chunk_size`, hàm đệ quy với các dấu phân cách còn lại; trường hợp cơ sở là đoạn rỗng, đoạn đã đủ ngắn, hoặc không còn dấu phân cách hữu ích thì cắt theo ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search` — hướng tiếp cận:**

Mỗi `Document` được chuyển thành record gồm `id`, `content`, metadata và embedding; store ưu tiên ChromaDB nếu dùng được, nếu không lưu danh sách record trong bộ nhớ. Khi tìm kiếm, query cũng được embedding, sau đó các record được xếp hạng giảm dần theo tích vô hướng; với embedding đã chuẩn hoá, đây chính là cosine similarity.

**`search_with_filter` + `delete_document` — hướng tiếp cận:**

`search_with_filter` lọc metadata trước rồi mới tính/xếp hạng độ tương tự, giúp không để tài liệu sai đối tượng chiếm top-k. `delete_document` xóa mọi record có `metadata["doc_id"]` khớp; hàm trả về `True` khi thực sự xóa được ít nhất một chunk.

### Tác tử KnowledgeBaseAgent

**`answer` — hướng tiếp cận:**

Tác tử lấy tối đa `top_k` chunk, ghép chúng thành phần Ngữ cảnh và ghi nhãn từng nguồn bằng `doc_id`. Prompt yêu cầu mô hình chỉ sử dụng ngữ cảnh và nói rõ khi thiếu thông tin, sau đó thêm câu hỏi của người dùng và gọi `llm_fn` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết quả kiểm thử (Test Results)

```text
pytest tests/ -v
======================== 42 passed, 1 warning in 0.13s ========================
```

**Số lượng bài test vượt qua (pass):** 42 / 42.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Các điểm dưới đây được tính bằng `compute_similarity()` trên embedding của mô hình đa ngữ cục bộ; dự đoán được đưa ra trước khi chạy.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Điều kiện tiếng Anh để được xét tốt nghiệp là gì? | Sinh viên phải đáp ứng yêu cầu năng lực tiếng Anh nào trước khi tốt nghiệp? | cao | 0,8237 | Có |
| 2 | Học bổng Full cần GPA bao nhiêu để gia hạn? | Điều kiện duy trì học bổng 100% gồm GPA và kỷ luật là gì? | cao | 0,8451 | Có |
| 3 | Điều kiện tham gia chương trình trao đổi OSEP là gì? | Thư viện mở cửa đến mấy giờ? | thấp | 0,1669 | Có |
| 4 | Khi học lại môn, lần nào được tính CGPA? | CGPA có tính điểm của lần học lại gần nhất không? | cao | 0,8776 | Có |
| 5 | Hạn nộp chứng chỉ tiếng Anh của thí sinh MD là khi nào? | Quy trình xin nghỉ học tạm thời gồm những bước nào? | thấp | 0,3990 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Cặp 5 vẫn đạt 0,3990 dù hai câu hỏi thuộc hai quy trình khác nhau. Điều này cho thấy embedding còn nhận diện các từ/cấu trúc chung như sinh viên, yêu cầu và quy định; vì vậy cần kết hợp metadata và kiểm tra ngữ cảnh, không chỉ dựa vào một ngưỡng score.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Thiết lập chạy:** `RecursiveChunker(chunk_size=700)`, 269 chunks, local multilingual embedder. Câu 1 gọi `search_with_filter(..., {"audience": "student"})`; bốn câu còn lại gọi `search(..., top_k=3)`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời đối chiếu từ ngữ cảnh |
|---|---|---|---:|---|---|
| 1 | Theo quy định dành cho sinh viên đang học, cần đáp ứng yêu cầu tiếng Anh nào để được xét tốt nghiệp? | `english-language-graduation-requirements::4`: trường hợp miễn chứng minh tiếng Anh cho công dân/thường trú nhân nước nói tiếng Anh. Chunk `::2` ở top-3 chứa đầy đủ mục 4.1–4.2. | 0,7445 | Có, nhưng top-1 chỉ một phần | Phải chứng minh năng lực tiếng Anh theo phương thức được chấp nhận; với bậc đại học, hoàn thành các học phần tiếng Anh bắt buộc/Pathway (nếu có) cũng đáp ứng yêu cầu. |
| 2 | Điều kiện để duy trì học bổng đầu vào Full hoặc 100% là gì? | `entry-scholarship-financial-aid-guidelines::8`: điều kiện gia hạn học bổng 50%–90%, GPA từ 2,5. | 0,6253 | Không đủ | Chunk đúng là `::5`, yêu cầu GPA từ 3,2, không vi phạm Tier 3/4, hoàn thành E.X.C.E.L và gặp Advisor; không xuất hiện trong top-3. |
| 3 | Sinh viên cần thỏa những điều kiện nào để tham gia Outbound Student Exchange Program (OSEP)? | `outbound-student-exchange-procedure::9`: mục đích và phạm vi chương trình OSEP. | 0,7721 | Không đủ | Chunk đúng là `::15`, gồm full-time active, CGPA ≥ 2,5, không kỷ luật Level 3+, đủ 2 học kỳ và còn 1 học kỳ, tài chính và ngoại ngữ phù hợp; không xuất hiện trong top-3. |
| 4 | Khi học lại một học phần, lần học nào được dùng để tính CGPA? | `masters-academic-regulations::24`: điểm lần học cuối là điểm chính thức. | 0,6093 | Có về nội dung, nhưng sai văn bản chuẩn | Đáp án là chỉ lần học gần nhất được tính CGPA. Chunk chuẩn của quy định đại học là `undergraduate-academic-regulations::63`, nhưng không vào top-3; câu hỏi cần nêu rõ bậc đại học để tránh nhiễu. |
| 5 | Thí sinh chương trình Medical Doctor phải hoàn thành yêu cầu tiếng Anh đầu vào chậm nhất khi nào để được nhập học và bắt đầu chương trình chính thức? | `masters-academic-regulations::52`: thủ tục liên quan đến nghỉ học. | 0,6508 | Không | Chunk đúng là `undergraduate-admissions-english-requirements::21`: trước/ngày 30 tháng 8; không xuất hiện trong top-3. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 2 / 5.

> `KnowledgeBaseAgent` trong `main.py` đang dùng `demo_llm`, chỉ hiển thị preview của prompt. Vì vậy cột cuối là câu trả lời được đối chiếu thủ công từ các chunk và gold answer, không khẳng định là văn bản do demo LLM sinh ra.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

Với tài liệu quy định, chia theo mục/tiêu đề có thể giữ toàn bộ danh sách điều kiện trong một chunk tốt hơn cắt thuần theo độ dài. Metadata như `audience`, `category` và `department` cũng cần được dùng cho các câu hỏi dễ nhầm giữa tuyển sinh, tốt nghiệp, đại học và thạc sĩ.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 4 / 10 |
| **Tổng phần cá nhân** | **54 / 60** |
