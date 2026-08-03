# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

- **Họ tên:** Bùi Đặng Quốc An
- **Mã số sinh viên:** 2A202601799
- **Nhóm:** K3 — University Services Retrieval
- **Ngày:** 2026-08-03

## 1. Khởi động (Warm-up)

### Độ tương tự cosine

Cosine similarity đo góc giữa hai vector embedding. Điểm gần `1` nghĩa là hai văn bản được biểu diễn theo hướng gần nhau (thường gần nghĩa); gần `0` là ít liên quan; gần `-1` là hai hướng đối nghịch.

Ví dụ điểm cao: “Điều kiện duy trì học bổng 100% là gì?” và “Sinh viên cần GPA bao nhiêu để giữ học bổng toàn phần?” đều hỏi về cùng chính sách. Ví dụ điểm thấp: “Thời hạn nộp đơn nghỉ học tạm thời là bao lâu?” và “Cơ sở dữ liệu vector lưu dữ liệu thế nào?” thuộc hai chủ đề không liên quan.

Cosine được ưu tiên cho text embedding vì trọng tâm là hướng/ngữ nghĩa của vector, ít bị ảnh hưởng bởi độ dài hay độ lớn tuyệt đối của vector. Euclidean distance nhạy với magnitude nên kém phù hợp hơn khi các embedding đã được chuẩn hoá.

### Bài toán chunking

Với 10.000 ký tự, `chunk_size=500`, `overlap=50`:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23` chunks.

Khi `overlap=100`: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` chunks. Overlap lớn hơn tạo thêm chunk để giữ ngữ cảnh qua ranh giới, đổi lại là nhiều embedding và chi phí lưu trữ/truy vấn hơn.

## 2. Hướng tiếp cận của tôi (My Approach)

### Các hàm chunking

`SentenceChunker.chunk` dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết thúc câu, giữ lại dấu câu. Các câu được `strip()`, bỏ phần rỗng, rồi ghép theo `max_sentences_per_chunk`; chuỗi rỗng trả về danh sách rỗng.

`RecursiveChunker` thử lần lượt `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là ký tự. Mỗi đơn vị ngắn được ghép đến khi chạm `chunk_size`; đơn vị dài được tách tiếp bằng separator ưu tiên thấp hơn. Base case là đoạn đã đủ ngắn; nếu đã hết separator thì dùng `FixedSizeChunker` không overlap để đảm bảo giới hạn kích thước.

### EmbeddingStore

`add_documents` chuẩn hoá record gồm id duy nhất, content, metadata và embedding. Store dùng ChromaDB khi khả dụng, nếu không thì dùng list trong bộ nhớ; metadata ngày tháng từ YAML được chuyển thành chuỗi để tương thích Chroma. `search` nhúng query, tính dot product trên các vector chuẩn hoá trong fallback, sắp điểm giảm dần và trả về `id`, `content`, `metadata`, `score`.

`search_with_filter` lọc metadata trước khi xếp hạng, nên loại tài liệu sai đối tượng ngay từ tập ứng viên. `delete_document` xoá mọi chunk có `metadata['doc_id']` trùng mã tài liệu và trả về boolean cho biết có bản ghi nào bị xoá không.

### KnowledgeBaseAgent

`answer` lấy top-k chunk từ store, đánh số chúng và đưa vào phần `Retrieved context` của prompt. Prompt yêu cầu LLM chỉ dùng ngữ cảnh đã lấy; nếu thiếu thông tin phải nói rõ. Sau đó agent gọi `llm_fn(prompt)` để tạo câu trả lời, nhờ đó câu trả lời có thể được truy vết về các chunk đã truy xuất.

## 3. Hoàn thiện code (Core Implementation)

Đã hoàn thiện `SentenceChunker`, `RecursiveChunker`, `compute_similarity`, `ChunkingStrategyComparator`, toàn bộ `EmbeddingStore`, và `KnowledgeBaseAgent`.

Kết quả kiểm thử:

```text
pytest tests/ -v
============================= 42 passed in 5.48s =============================
```

Ngoài unit test, `python ingest.py` đã qua self-check (parse 4 metadata keys và tạo 18 chunks); `main.py` đã nạp được 298 chunks từ `data/k3_university/` bằng mock backend. Mock chỉ được dùng để kiểm tra đường chạy; không dùng để kết luận chất lượng ngữ nghĩa.

## 4. Dự đoán độ tương tự (Similarity Predictions)

Các điểm dưới đây chạy bằng `_mock_embed` để kiểm tra công thức `compute_similarity`. Kết quả cho thấy rõ hạn chế của mock: nó sinh vector xác định theo toàn bộ chuỗi, không phải embedding ngữ nghĩa.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Học bổng 100% cần GPA 3.2. | Để duy trì học bổng 100%, GPA tích lũy phải từ 3.2. | cao | -0.0609 | Không |
| 2 | Sinh viên nộp đơn nghỉ học tạm thời ở đâu? | Đơn LOA được gửi đến registrar@vinuni.edu.vn. | cao | 0.0466 | Có (rất yếu) |
| 3 | Quy định kháng nghị điểm áp dụng thế nào? | Sinh viên có thể nộp đơn kháng nghị theo quy trình. | cao | -0.0875 | Không |
| 4 | Học bổng cần GPA bao nhiêu? | Thư viện có chính sách gia hạn sách. | thấp | 0.0565 | Không |
| 5 | Kỳ nghỉ hè bắt đầu khi nào? | Cơ sở dữ liệu vector lưu embeddings. | thấp | 0.2419 | Không |

Kết quả bất ngờ nhất là cặp 5 (không liên quan) lại có điểm cao nhất. Điều này xác nhận cảnh báo của lab: MockEmbedder phù hợp cho unit test có tính xác định, nhưng không biểu diễn ý nghĩa tiếng Việt/Anh và không được dùng để so sánh retrieval. Khi môi trường có thể tải model, cần chạy lại phần này với `EMBEDDING_PROVIDER=local` và `paraphrase-multilingual-MiniLM-L12-v2`.

## 5. Kết quả truy xuất của tôi (Competition Results)

Tôi dùng corpus 8 chính sách công khai trong `data/k3_university/`, có `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, và `language`. Chiến lược cá nhân là `RecursiveChunker(chunk_size=200)`: nó bảo toàn ranh giới heading/paragraph/câu tốt hơn cắt theo số ký tự. Trên hai tài liệu đầu, baseline cho kết quả sau:

| Tài liệu | Fixed size | By sentences | Recursive |
|---|---:|---:|---:|
| English graduation requirements | 18 chunks, TB 199.6 ký tự | 13, TB 249.2 | 23, TB 140.1 |
| Entry scholarship & financial aid | 29 chunks, TB 196.8 ký tự | 16, TB 320.6 | 35, TB 145.8 |

Năm câu hỏi benchmark và căn cứ gold answer:

| # | Câu hỏi | Chunk/tài liệu cần truy xuất và câu trả lời chuẩn |
|---|---|---|
| 1 | Điều kiện GPA để duy trì học bổng merit Full hoặc 100% là gì? | `entry-scholarship-financial-aid-guidelines`, mục 3/Trang 2: cumulative GPA từ **3.2** trong năm học đánh giá (trung bình Fall và Spring); còn phải có kỷ luật tốt và hoàn thành E.X.C.E.L. |
| 2 | Muốn quay lại học sau LOA, sinh viên phải gửi đơn khi nào? | `leave-of-absence-withdrawal-return-procedure`, mục 3.2/Trang 4: gửi form cho Registrar **ít nhất một tháng trước** khi học kỳ quay lại bắt đầu. |
| 3 | Trong trao đổi sinh viên, tải học tập full-time tối thiểu là bao nhiêu tín chỉ? | `outbound-student-exchange-procedure`, mục 4.2 và 4.5: tối thiểu **12 credits** trong mỗi học kỳ chính; không có yêu cầu cho học kỳ hè. |
| 4 | Khi nào sinh viên có thể kháng nghị điểm cuối kỳ? | `student-grade-appeal-procedure`, mục 2: chỉ áp dụng cho **final course grades** bị lỗi hành chính hoặc thiên vị/tùy tiện; sinh viên phải bắt đầu trao đổi trực tiếp với giảng viên và cung cấp chứng cứ. |
| 5 | Với `metadata_filter={"audience": "student"}`, yêu cầu tiếng Anh tốt nghiệp cho sinh viên đại học là gì? | `english-language-graduation-requirements`, mục 4.2: hoàn thành các học phần tiếng Anh bắt buộc với điểm đạt, gồm Academic English/Fundamentals of Academic Writing và Pathway English (nếu được yêu cầu). Filter giữ đúng tài liệu dành cho student. |

Tất cả năm gold answers đều truy vết trực tiếp từ corpus. Khi chạy demo với mock, top-3 cho câu 1 là các chunk không liên quan, nên tôi không gán điểm retrieval giả tạo cho backend này. Đây là failure case rõ ràng: mock xếp nhầm quy trình trao đổi/LOA vì vector được sinh theo hash chuỗi, không phải ngữ nghĩa. Để chấm retrieval thật, chạy `pip install -r requirements-local.txt`, đặt `EMBEDDING_PROVIDER=local`, rồi chạy lại năm query với cùng corpus và `RecursiveChunker`; khi đó ghi top-1, score và độ liên quan thực tế vào bảng dưới đây.

| # | Kết quả mock hiện tại | Đánh giá |
|---|---|---|
| 1 | Top-1 là outbound exchange, score -0.382 | Không liên quan; không dùng để chấm semantic retrieval |
| 2–5 | Không chấm bằng mock | Cần local multilingual embedder theo yêu cầu Phase 2 |

Điều hay nhất tôi rút ra là chunking tốt không thể bù cho embedding không có ngữ nghĩa. Recursive splitting làm chunk ngắn và mạch lạc hơn cho chính sách có heading/bảng; metadata `audience=student` đặc biệt hữu ích để tách quy định sinh viên khỏi tài liệu cho faculty/staff. Lần tiếp theo, tôi sẽ đo precision@3 trên local model, lưu cả `doc_id`/`chunk_index` của gold chunk và so sánh A/B với SentenceChunker để có kết luận định lượng.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code (42/42 tests) | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất | Cần chạy local model để chấm chính thức / 10 |
| **Tổng có thể xác nhận** | **50 / 60 + phần retrieval local** |
