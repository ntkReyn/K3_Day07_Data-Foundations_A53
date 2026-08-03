# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Quang Huy

**Nhóm:** A53

**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding hướng gần giống nhau, do đó hai đoạn văn thường có nội dung hoặc ý nghĩa ngữ nghĩa gần nhau. Giá trị càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể gia hạn sách thư viện trực tuyến.
- Câu B: Người học được phép kéo dài thời gian mượn sách qua hệ thống thư viện.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng nói về việc sinh viên gia hạn thời gian mượn sách.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên đăng ký học phần trên cổng đào tạo.
- Câu B: Thời tiết hôm nay có mưa lớn.
- Tại sao khác: Hai câu thuộc hai chủ đề và mục đích hoàn toàn khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector thay vì độ lớn, nên phù hợp hơn khi cần so sánh ý nghĩa của văn bản. Khoảng cách Euclid dễ bị ảnh hưởng bởi độ lớn vector, dù hai vector có hướng và nội dung ngữ nghĩa gần giống nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22,11)`.
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(24,75) = 25`, tức tăng từ 23 lên 25 chunks. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng dữ liệu trùng lặp, chi phí embedding và số lượng kết quả cần lưu.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng đứng sau dấu kết thúc câu `.`, `!` hoặc `?`, nhờ đó vẫn giữ dấu câu trong nội dung. Sau khi loại khoảng trắng thừa và phần tử rỗng, các câu được nhóm theo `max_sentences_per_chunk`. Chuỗi rỗng hoặc chỉ chứa khoảng trắng trả về danh sách rỗng; tham số số câu được giới hạn tối thiểu là 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi thử separator theo thứ tự ưu tiên `\n\n`, `\n`, `. `, khoảng trắng rồi đến ký tự. Trước tiên, các phần nhỏ liền kề được ghép lại nếu tổng độ dài không vượt `chunk_size`; phần còn quá dài tiếp tục được xử lý đệ quy bằng separator có độ ưu tiên thấp hơn. Base case là đoạn đã có độ dài không vượt giới hạn; nếu không còn separator hữu ích thì cắt trực tiếp theo số ký tự để thuật toán luôn kết thúc.

**`HeadingChunker.chunk`** — chiến lược cá nhân cho dữ liệu K3:
> Tôi tách tài liệu tại heading Markdown, các mục đánh số như `4.1`, và tiêu đề dạng `Article N`/`Điều N`, đồng thời giữ tiêu đề đi cùng nội dung của mục. Section dài hơn 1.000 ký tự được chia tiếp bằng `RecursiveChunker`, còn các section ngắn được ghép nếu vẫn nằm trong giới hạn. Cách này phù hợp với văn bản quy định vì giảm nguy cơ tách điều kiện khỏi tên điều khoản, dù corpus hiện còn nhiều heading theo trang do được chuyển từ PDF.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Với mỗi `Document`, tôi tạo một record chuẩn hóa gồm ID tài liệu, storage ID duy nhất, nội dung, bản sao metadata và embedding. Store hỗ trợ ChromaDB nếu thư viện có sẵn, đồng thời giữ một bản in-memory để hành vi tìm kiếm và lọc nhất quán. Khi tìm kiếm, truy vấn được embedding một lần, sau đó tính dot product với từng record, sắp xếp điểm giảm dần và lấy tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record theo tất cả cặp khóa–giá trị metadata trước, sau đó mới tính similarity trên tập ứng viên còn lại; cách này tránh để tài liệu sai đối tượng cạnh tranh trong bảng xếp hạng. `delete_document` tìm toàn bộ chunk có `metadata["doc_id"]` tương ứng, xóa chúng khỏi bản in-memory và khỏi ChromaDB bằng các storage ID, rồi trả về `True` nếu thực sự có dữ liệu bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search(question, top_k)` để lấy các chunk liên quan và nối nội dung của chúng thành phần `Context`. Prompt yêu cầu mô hình chỉ trả lời dựa trên context và nói không biết nếu tài liệu không chứa đáp án, sau đó đặt câu hỏi trong phần `Question`. Nếu không truy xuất được chunk nào, prompt ghi rõ rằng không tìm thấy ngữ cảnh liên quan trước khi gọi `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
..........................................                               [100%]
42 passed in 0.22s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Students must maintain a GPA of 3.2 to keep the scholarship. | A cumulative GPA of at least 3.2 is required to retain the scholarship. | Cao | 0.5107 | Có |
| 2 | Students should contact the instructor to appeal a grade. | A grade appeal begins by consulting the course instructor. | Cao | 0.4426 | Có |
| 3 | The minimum CGPA for student exchange is 2.5. | Outbound exchange applicants need a CGPA of at least 2.5. | Cao | 0.3591 | Có, nhưng thấp hơn dự kiến |
| 4 | Students must meet English graduation requirements. | The weather forecast predicts heavy rain tomorrow. | Thấp | 0.0000 | Có |
| 5 | Sinh viên phải đáp ứng chuẩn tiếng Anh để tốt nghiệp. | Người học cần đạt yêu cầu ngoại ngữ trước khi được xét tốt nghiệp. | Cao | 0.4631 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 3 bất ngờ nhất vì hai câu gần như cùng một thông tin nhưng TF-IDF chỉ đạt 0.3591; nguyên nhân là hai câu dùng nhiều từ khác nhau và TF-IDF chủ yếu dựa trên từ trùng. Thí nghiệm này cho thấy lexical vector có thể nhận ra từ khóa và con số nhưng không biểu diễn quan hệ đồng nghĩa tốt như semantic embedding. Các điểm trên được tính bằng TF-IDF rồi truyền vào `compute_similarity`, do local multilingual model chưa cài được trong môi trường Python 3.13.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Theo quy định **dành cho sinh viên đang học**, cần đáp ứng yêu cầu tiếng Anh nào để được xét tốt nghiệp? Chạy với `metadata_filter={"audience": "student"}`. | Sinh viên phải cung cấp bằng chứng năng lực tiếng Anh theo một phương thức được chấp nhận trong English Entry Requirements Policy. Với bậc đại học, hoàn thành đạt các học phần tiếng Anh bắt buộc, gồm Academic English hoặc Fundamentals of Academic Writing và các học phần Pathway English (nếu được yêu cầu), cũng được xem là đáp ứng yêu cầu. | `english-language-graduation-requirements` — mục 4.1 và 4.2. |
| 2 | Điều kiện để duy trì học bổng đầu vào Full hoặc 100% là gì? | GPA tích lũy của năm học được đánh giá phải từ 3.2 trở lên (trung bình Fall và Spring); sinh viên không vi phạm Tier 3 hoặc Tier 4; đồng thời hoàn thành tự đánh giá E.X.C.E.L và gặp Advisor để trao đổi. | `entry-scholarship-financial-aid-guidelines` — mục 3, hàng “Merit-based Scholarships — Full & 100%”. |
| 3 | Sinh viên cần thỏa những điều kiện nào để tham gia Outbound Student Exchange Program (OSEP)? | Phải là sinh viên toàn thời gian đang hoạt động; có academic standing tốt với CGPA tối thiểu 2.5 và đáp ứng yêu cầu của trường tiếp nhận; không bị kỷ luật mức 3 trở lên; đã hoàn thành ít nhất 2 học kỳ tại VinUni và còn ít nhất 1 học kỳ trước tốt nghiệp sau OSEP; có tình trạng tài chính tốt và đáp ứng yêu cầu ngôn ngữ của trường tiếp nhận. | `outbound-student-exchange-procedure` — mục 4.1 “Eligible criteria for application”. |
| 4 | Khi học lại một học phần, lần học nào được dùng để tính CGPA? | Chỉ kết quả của lần học gần nhất (latest attempt) được tính vào CGPA. | `undergraduate-academic-regulations` — Article 6, mục b về CGPA. |
| 5 | Thí sinh chương trình Medical Doctor phải hoàn thành yêu cầu tiếng Anh đầu vào chậm nhất khi nào để được nhập học và bắt đầu chương trình chính thức? | Chậm nhất ngày 30 tháng 8 của năm tuyển sinh. | `undergraduate-admissions-english-requirements` — mục 4.3 “Conditional admission”. |

### Thiết lập đánh giá cá nhân

- Chiến lược: `HeadingChunker(chunk_size=1000)`.
- Corpus: 8 tài liệu, tạo 209 chunks, độ dài trung bình 632,5 ký tự.
- Backend: TF-IDF lexical baseline; câu hỏi tiếng Việt được dịch tương đương sang tiếng Anh để khớp ngôn ngữ nguồn. Không dùng mock embedding để kết luận chất lượng retrieval.
- Câu 1 dùng `metadata_filter={"audience": "student"}`.

| # | Top-1 chunk truy xuất được (tóm tắt) | Score | Top-3 có chunk chứa gold answer? | Câu trả lời dựa trên context |
|---|--------------------------------------|------:|----------------------------------|-----------------------------|
| 1 | Mục 4.1 về bằng chứng năng lực tiếng Anh được chấp nhận để tốt nghiệp | 0.3635 | Có — Top-1 | Phải cung cấp bằng chứng theo English Entry Requirements Policy; sinh viên đại học cũng có thể đáp ứng qua các học phần tiếng Anh bắt buộc. |
| 2 | Phần tiêu chí duy trì scholarship/financial aid | 0.3393 | Có — các phần gold ở Top-2 và Top-3 | GPA năm học từ 3.2, không vi phạm Tier 3/4, hoàn thành E.X.C.E.L và trao đổi với Advisor. |
| 3 | Trách nhiệm xin phê duyệt trước việc chuyển đổi tín chỉ OSEP | 0.2633 | Không | Context top-3 không chứa đầy đủ mục 4.1, vì vậy agent nên trả lời chưa đủ thông tin thay vì suy đoán. |
| 4 | Điều khoản quy định chỉ latest attempt được dùng tính CGPA | 0.1850 | Có — Top-1 | Chỉ kết quả lần học gần nhất được tính vào CGPA. |
| 5 | Mục conditional admission nêu hạn ngày 30 August | 0.3913 | Có — Top-1 | Chậm nhất ngày 30 tháng 8 của năm tuyển sinh. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

### So sánh chiến lược

| Chiến lược | Số chunk | Độ dài trung bình | Số câu có gold answer trong top-3 |
|------------|----------:|------------------:|---------------------------------:|
| Fixed-size, size 1000, overlap 100 | 150 | 977,5 | 4 / 5 |
| Sentence, 5 câu/chunk | 231 | 571,9 | 4 / 5 |
| Recursive, size 1000 | 199 | 663,9 | 4 / 5 |
| Heading, size 1000 | 209 | 632,5 | 4 / 5 |

> HeadingChunker không tăng recall top-3 so với các baseline trong lần chạy này, nhưng tạo ranh giới dễ giải thích hơn vì tên mục được giữ cùng nội dung. Failure case là câu OSEP: các chunk tổng quan và trách nhiệm có nhiều từ khóa trùng với truy vấn nên đứng trên mục `4.1 Eligible criteria for application`. Có thể cải thiện bằng cách làm sạch lại Markdown để biến các tiêu đề mục trong PDF thành heading chuẩn, dùng semantic multilingual embedding và bổ sung metadata filter theo `category=student-exchange`.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng không nên chỉ so sánh số lượng hoặc độ dài chunk; cần kiểm tra trực tiếp xem chunk có giữ trọn điều kiện, ngoại lệ và tiêu đề của điều khoản hay không. Metadata filtering giúp thu hẹp đúng đối tượng, còn chất lượng heading từ bước làm sạch dữ liệu ảnh hưởng trực tiếp đến hiệu quả của chiến lược chia theo section.

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
