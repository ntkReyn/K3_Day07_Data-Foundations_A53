# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** A53

| STT | Họ tên | MSSV |
|---:|---|---|
| 1 | Nguyễn Quang Huy | 2A202601165 |
| 2 | Nguyễn Thế Khôi | 2A202601439 |
| 3 | Lê Tiến Đạt | 2A202601263 |
| 4 | Bùi Đặng Quốc An | 2A202601799 |

**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**

> Các quy định học vụ và dịch vụ dành cho người học tại VinUniversity: yêu cầu tiếng Anh, học bổng, trao đổi sinh viên, điểm số, tạm nghỉ/rút học và quy chế đào tạo.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | English Language Proficiency Requirements for Graduation at VinUniversity | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/english-language-proficiency-requirements-for-graduation-at-vinuniversity/) | 03/08/2026 · v1.0 | 3.252 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 2 | Guidelines for Maintaining Entry Scholarship and Financial Aid Support | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/) | 03/08/2026 · v2.1 | 5.148 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 3 | Procedure for Requesting a Leave of Absence, Withdrawal and Return from a Leave of Absence | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/procedure-for-requesting-a-leave-of-absence-withdrawal-and-return-from-a-leave-of-absence/) | 03/08/2026 · v1.0 | 6.996 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 4 | Quy chế đào tạo trình độ Thạc sĩ | [VinUni Policy](https://policy.vinuni.edu.vn/academic-affairs/academic-regulations-for-master-programs/) | 03/08/2026 · v1.1 | 34.177 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 5 | Procedure for Outbound Student Exchange Programs | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/outbound-student-exchange-procedure/) | 03/08/2026 · v4 | 25.396 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 6 | Student Grade Appeal Procedure | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/student-grade-appeal-procedure/) | 03/08/2026 · v2.0 | 5.952 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 7 | Academic Regulations for Full-Time Undergraduate Programs | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergraduate-programs/) | 03/08/2026 · v8.0 | 38.124 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 8 | English Language Requirements for Undergraduate Admissions | [VinUni Policy](https://policy.vinuni.edu.vn/academic-affairs/english-language-requirements-for-undergraduate-admissions/) | 03/08/2026 · v4.1 | 13.377 | `doc_id`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chỉ chứa các chính sách công khai từ website VinUniversity; không nạp dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Cả 8 tài liệu đều có `source_url`, `retrieved_at` và `document_version` trong YAML front matter; danh sách đối chiếu nằm tại `data/k3_university/sources.csv`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `undergraduate-academic-regulations` | Định danh ổn định từng tài liệu; dùng để truy vết chunk và xóa toàn bộ chunk của một tài liệu. |
| `title` | string | `Academic Regulations for Full-Time Undergraduate Programs` | Cung cấp tên chính sách dễ đọc khi hiển thị nguồn trả lời. |
| `audience` | string | `student`, `all` | Lọc đúng đối tượng áp dụng; ví dụ câu hỏi về tốt nghiệp dùng `audience: student` để loại quy định tuyển sinh. |
| `department` | string | `registrar`, `admissions` | Phân biệt quy định do Registrar, Admissions hoặc Student Affairs phụ trách. |
| `category` | string | `academic-regulations`, `student-exchange` | Thu hẹp tìm kiếm theo chủ đề, giảm nhiễu giữa học bổng, tuyển sinh và quy chế học vụ. |
| `language` | string | `en`, `vi` | Hỗ trợ kiểm soát/nghiên cứu tác động của ngôn ngữ truy vấn so với ngôn ngữ tài liệu. |
| `source_url` | URL string | `https://policy.vinuni.edu.vn/...` | Cho phép kiểm chứng nguồn gốc của câu trả lời. |
| `retrieved_at` | date | `2026-08-03` | Theo dõi thời điểm thu thập để đánh giá độ mới của thông tin. |
| `document_version` | string | `8.0` | Xác định phiên bản chính sách được dùng, tránh trích dẫn quy định cũ. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2 tài liệu đại diện:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| English Language Proficiency Requirements for Graduation | FixedSizeChunker (`fixed_size`) | 18 | 199.6 ký tự | Có overlap 20 ký tự, nhưng có thể cắt giữa ý/bảng. |
| English Language Proficiency Requirements for Graduation | SentenceChunker (`by_sentences`) | 13 | 249.2 ký tự | Giữ câu tốt, nhưng một số chunk dài do văn bản PDF đã làm sạch. |
| English Language Proficiency Requirements for Graduation | RecursiveChunker (`recursive`) | 23 | 140.1 ký tự | Tốt; ưu tiên paragraph/câu nên ngữ cảnh mạch lạc hơn. |
| Guidelines for Maintaining Entry Scholarship and Financial Aid Support | FixedSizeChunker (`fixed_size`) | 29 | 196.8 ký tự | Có overlap, nhưng có thể tách điều kiện GPA khỏi điều kiện kỷ luật. |
| Guidelines for Maintaining Entry Scholarship and Financial Aid Support | SentenceChunker (`by_sentences`) | 16 | 320.6 ký tự | Giữ trọn câu, nhưng chunk lớn có thể lẫn nhiều điều kiện. |
| Guidelines for Maintaining Entry Scholarship and Financial Aid Support | RecursiveChunker (`recursive`) | 35 | 145.8 ký tự | Tốt nhất cho heading/bảng chính sách; cần đánh giá thêm bằng local embedder. |
| Quy định học thuật | FixedSizeChunker (`fixed_size`) | 8 | ~420 ký tự | Có, vì mỗi chunk giữ một phần liên tục của văn bản. |
| Quy định học thuật | SentenceChunker (`by_sentences`) | 6 | ~550 ký tự | Có, vì chunk theo câu giúp giữ ý nghĩa hoàn chỉnh. |
| Quy định học thuật | RecursiveChunker (`recursive`) | 7 | ~480 ký tự | Có, vì chia theo đoạn và cấu trúc ngữ pháp tự nhiên. |
| English Language Graduation Requirements | FixedSizeChunker (`fixed_size`) | 4 | 813,0 ký tự | Không ổn định; có thể cắt giữa câu hoặc giữa điều khoản. |
| English Language Graduation Requirements | SentenceChunker (`by_sentences`) | 9 | 360,3 ký tự | Có ở mức câu, nhưng dễ tách tiêu đề khỏi nội dung. |
| English Language Graduation Requirements | RecursiveChunker (`recursive`) | 5 | 649,0 ký tự | Khá tốt; ưu tiên đoạn và xuống dòng. |
| Entry Scholarship & Financial Aid Guidelines | FixedSizeChunker (`fixed_size`) | 6 | 858,0 ký tự | Có thể chia một hàng tiêu chí sang hai chunk. |
| Entry Scholarship & Financial Aid Guidelines | SentenceChunker (`by_sentences`) | 11 | 466,7 ký tự | Dễ đọc, nhưng một chunk dài tới 1.270 ký tự. |
| Entry Scholarship & Financial Aid Guidelines | RecursiveChunker (`recursive`) | 7 | 733,7 ký tự | Tốt hơn trong việc giữ cụm tiêu chí gần nhau. |
| Outbound Student Exchange Procedure | FixedSizeChunker (`fixed_size`) | 26 | 976,8 ký tự | Chunk đều nhưng có nguy cơ cắt giữa các bước thủ tục. |
| Outbound Student Exchange Procedure | SentenceChunker (`by_sentences`) | 75 | 337,4 ký tự | Mạch lạc ở cấp câu nhưng tạo nhiều chunk nhỏ. |
| Outbound Student Exchange Procedure | RecursiveChunker (`recursive`) | 38 | 666,8 ký tự | Cân bằng kích thước và ranh giới nội dung tốt nhất trong ba baseline. |
| Corpus 8 tài liệu | HeadingChunker (`custom`, 1000) | 209 | 632,5 ký tự | Tốt; giữ heading cùng nội dung theo sau và dùng Recursive làm fallback cho section dài. |


### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Thế Khôi**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=700)`.
- **Mô tả & lý do chọn cho chủ đề này:** Chiến lược thử các dấu phân cách theo thứ tự đoạn (`\n\n`), dòng (`\n`), câu (`. `), khoảng trắng rồi mới cắt ký tự. Cách này phù hợp với quy định đại học vì giữ các đề mục và danh sách điều kiện tương đối mạch lạc, trong khi 700 ký tự đủ chứa nhiều tiêu chí liên quan của một quy trình. Khi chạy với local multilingual embedder trên 269 chunks, kết quả có chunk liên quan trong top-3 ở 2/5 câu hỏi (4/10).
- **Code snippet:** Không dùng chiến lược custom; sử dụng `RecursiveChunker` đã hoàn thiện trong `src/chunking.py`.

**Thành viên 2 — Bùi Đặng Quốc An (2A202601799)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=200)`.
- **Mô tả & lý do chọn cho chủ đề này:** Corpus chính sách đại học có heading, đoạn, danh sách và bảng được chuyển từ PDF. RecursiveChunker ưu tiên ranh giới `\n\n`, `\n`, `. ` rồi mới đến khoảng trắng/ký tự, vì vậy giữ điều kiện và mốc thời gian trong cùng ngữ cảnh tốt hơn FixedSizeChunker. Kích thước 200 ký tự giúp mỗi chunk đủ ngắn để truy xuất chính xác nhưng vẫn chứa một ý hoàn chỉnh.
- **Code snippet:** Không dùng custom chunker; dùng implementation `RecursiveChunker` trong `src/chunking.py`.

**Thành viên 3 — Lê Tiến Đạt**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`.
- **Mô tả & lý do chọn cho chủ đề này:** Fixed-size phù hợp với các quy định học thuật vì văn bản có nhiều đoạn dài và cần giữ được cấu trúc liên tục. Chiến lược này đơn giản, dễ triển khai và ổn định cho các tài liệu có độ dài lớn.
- **Code snippet:**
```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

**Thành viên 4 — Nguyễn Quang Huy**
- **Loại chiến lược:** Custom — `HeadingChunker(chunk_size=1000)`.
- **Mô tả & lý do chọn cho chủ đề này:** Tôi chia tài liệu tại heading Markdown, tiêu đề mục đánh số như `4.1`, và các tiêu đề dạng `Article N`/`Điều N`; tiêu đề luôn được giữ cùng nội dung theo sau. Nếu một section vượt quá 1.000 ký tự, tôi dùng `RecursiveChunker` để chia tiếp; các section ngắn liền nhau được ghép khi vẫn nằm trong giới hạn. Cách này phù hợp với quy định đại học vì giúp bảo toàn tên điều khoản cùng các điều kiện, thời hạn và ngoại lệ liên quan.
- **Kết quả cá nhân:** Corpus 8 tài liệu tạo 209 chunks, độ dài trung bình 632,5 ký tự. Với 5 benchmark queries, 4/5 câu có chunk chứa gold answer trong top-3; câu OSEP thất bại vì các đoạn tổng quan có nhiều từ khóa trùng hơn mục `4.1 Eligible criteria for application`.
- **Thiết lập đánh giá:** TF-IDF lexical baseline; các câu hỏi tiếng Việt được dịch tương đương sang tiếng Anh do tài liệu nguồn chủ yếu là tiếng Anh; câu 1 dùng `metadata_filter={"audience": "student"}`. Kết quả này là baseline có thể diễn giải, chưa phải kết quả semantic multilingual embedding.
- **Code snippet (custom):**
```python
class HeadingChunker:
    HEADING_PATTERN = re.compile(
        r"(?m)^(?:"
        r"#{1,6}[ \t]+.+"
        r"|\d+(?:\.\d+)+\.?[ \t]+[^\n]{2,120}"
        r"|(?:Article|Điều)[ \t]+\d+[^\n]{0,120}"
        r")\s*$",
        re.IGNORECASE,
    )

    def __init__(self, chunk_size: int = 1000) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        # Tách theo heading, giữ heading với section và dùng recursive
        # fallback khi section dài hơn chunk_size.
        ...
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Thế Khôi | Recursive, `chunk_size=700` | 4 / 10 | Ưu tiên giữ cấu trúc đoạn/dòng/câu; câu 1 có lọc metadata đưa đúng quy định tốt nghiệp vào top-3. | Cắt theo độ dài vẫn có thể tách rời danh sách điều kiện; nhiễu giữa tài liệu cùng chủ đề và giữa bậc đại học/thạc sĩ. |
| Bùi Đặng Quốc An | RecursiveChunker, `chunk_size=200` | 6/10 | Bảo toàn paragraph/câu; phù hợp chính sách nhiều heading và điều kiện. | Tạo nhiều chunk hơn và chưa được chấm semantic retrieval bằng local multilingual model. |
| Lê Tiến Đạt | FixedSizeChunker, `chunk_size=500`, `overlap=50` | 8 / 10 | Dễ triển khai, bảo toàn ngữ cảnh liên tục. | Có thể cắt ở giữa câu hoặc đoạn. |
| Nguyễn Quang Huy | HeadingChunker, `chunk_size=1000` | 8 / 10 (4/5 queries) | Giữ tiêu đề cùng nội dung; ranh giới chunk dễ giải thích. | Phụ thuộc chất lượng heading sau khi chuyển PDF; chưa cải thiện recall so với Recursive. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chưa kết luận cuối cùng vì Thành viên 2 chưa chạy local embedder trên cùng 5 câu hỏi. Tạm thời, FixedSize của Lê Tiến Đạt và HeadingChunker của Nguyễn Quang Huy đều đạt 8/10, cao hơn kết quả Recursive 700 ký tự của Thành viên 1. Tuy nhiên, kết quả của Huy dùng TF-IDF và câu hỏi tiếng Anh đã dịch, còn các thành viên khác dùng/định dùng local multilingual embedding; cần chạy cùng một embedder, corpus và câu hỏi trước khi khẳng định chiến lược tốt nhất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Theo quy định **dành cho sinh viên đang học**, cần đáp ứng yêu cầu tiếng Anh nào để được xét tốt nghiệp? Chạy với `metadata_filter={"audience": "student"}`. | Sinh viên phải cung cấp bằng chứng năng lực tiếng Anh theo một phương thức được chấp nhận trong English Entry Requirements Policy. Với bậc đại học, hoàn thành đạt các học phần tiếng Anh bắt buộc, gồm Academic English hoặc Fundamentals of Academic Writing và các học phần Pathway English (nếu được yêu cầu), cũng được xem là đáp ứng yêu cầu. | `english-language-graduation-requirements` — mục 4.1 và 4.2. |
| 2 | Điều kiện để duy trì học bổng đầu vào Full hoặc 100% là gì? | GPA tích lũy của năm học được đánh giá phải từ 3.2 trở lên (trung bình Fall và Spring); sinh viên không vi phạm Tier 3 hoặc Tier 4; đồng thời hoàn thành tự đánh giá E.X.C.E.L và gặp Advisor để trao đổi. | `entry-scholarship-financial-aid-guidelines` — mục 3, hàng “Merit-based Scholarships — Full & 100%”. |
| 3 | Sinh viên cần thỏa những điều kiện nào để tham gia Outbound Student Exchange Program (OSEP)? | Phải là sinh viên toàn thời gian đang hoạt động; có academic standing tốt với CGPA tối thiểu 2.5 và đáp ứng yêu cầu của trường tiếp nhận; không bị kỷ luật mức 3 trở lên; đã hoàn thành ít nhất 2 học kỳ tại VinUni và còn ít nhất 1 học kỳ trước tốt nghiệp sau OSEP; có tình trạng tài chính tốt và đáp ứng yêu cầu ngôn ngữ của trường tiếp nhận. | `outbound-student-exchange-procedure` — mục 4.1 “Eligible criteria for application”. |
| 4 | Khi học lại một học phần, lần học nào được dùng để tính CGPA? | Chỉ kết quả của lần học gần nhất (latest attempt) được tính vào CGPA. | `undergraduate-academic-regulations` — Article 6, mục b về CGPA. |
| 5 | Thí sinh chương trình Medical Doctor phải hoàn thành yêu cầu tiếng Anh đầu vào chậm nhất khi nào để được nhập học và bắt đầu chương trình chính thức? | Chậm nhất ngày 30 tháng 8 của năm tuyển sinh. | `undergraduate-admissions-english-requirements` — mục 4.3 “Conditional admission”. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).


| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Yêu cầu tiếng Anh để tốt nghiệp | HeadingChunker| Có | HeadingChunker nằm trong 4/5 câu thành công; Recursive 700 của Khôi cũng đưa chunk mục 4.1–4.2 vào top-3 khi dùng `metadata_filter={"audience": "student"}`. |
| 2 | Duy trì học bổng Full/100% | HeadingChunker| Có | Thuộc 4/5 câu thành công; cần kiểm tra top-3 có đủ GPA, kỷ luật và E.X.C.E.L. khi chạy local multilingual embedding. |
| 3 | Điều kiện OSEP | HeadingChunker| Không | HeadingChunker thất bại ở câu này vì chunk tổng quan có nhiều từ khóa trùng hơn mục 4.1; Recursive 700 của Khôi cũng chưa đưa mục điều kiện đầy đủ vào top-3. |
| 4 | Lần học được tính CGPA | HeadingChunker (| Có | Thuộc 4/5 câu thành công; cần bảo đảm truy xuất đúng quy định đại học, không nhầm với quy chế thạc sĩ. |
| 5 | Hạn tiếng Anh đầu vào của MD | HeadingChunker| Có | Thuộc 4/5 câu thành công; kiểm tra phân biệt chính sách tuyển sinh với yêu cầu tốt nghiệp. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, ở câu 1. Cả tài liệu tuyển sinh (`audience: all`) và tài liệu tốt nghiệp (`audience: student`) đều chứa khái niệm “English requirements”; lọc `audience: student` loại tài liệu tuyển sinh để ưu tiên đúng quy định áp dụng cho sinh viên đang học. Nhóm sẽ ghi lại top-3 trước/sau lọc để kiểm tra lợi ích thực tế và theo dõi đánh đổi về recall.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Metadata `audience` giúp tách chính sách dành cho sinh viên đang học khỏi chính sách tuyển sinh: ở câu tiếng Anh tốt nghiệp, bộ lọc `{"audience": "student"}` loại tài liệu admissions và đưa chunk mục 4.1–4.2 vào top-3.
- Chiến lược chunking thay đổi trực tiếp loại lỗi: FixedSize đơn giản và đạt 8/10 ở cấu hình của Lê Tiến Đạt nhưng có nguy cơ cắt giữa câu/điều khoản; Recursive giữ ranh giới tự nhiên hơn; HeadingChunker của Nguyễn Quang Huy giữ tiêu đề cùng phần nội dung, nên dễ giải thích nguồn trả lời.
- Failure case OSEP cho thấy chỉ khớp từ khóa là chưa đủ: các đoạn giới thiệu/tổng quan có nhiều từ “exchange”, “student”, “program” hơn nên lấn át chunk mục 4.1 chứa danh sách điều kiện. HeadingChunker và Recursive 700 đều chưa đưa đúng mục điều kiện đầy đủ vào top-3.

**Bài học rút ra khi so sánh trong nhóm:**

Cùng một corpus nhưng chunk ngắn không mặc nhiên tốt hơn chunk dài: chunk ngắn tăng độ chính xác cục bộ, nhưng có thể chia rời danh sách điều kiện; chunk lớn giữ đủ ngữ cảnh nhưng dễ chứa nhiều ý gây nhiễu. Chia theo heading/section phù hợp với văn bản quy định vì liên kết được tên điều khoản với ngoại lệ, thời hạn và tiêu chí ngay sau nó. Tuy nhiên, để so sánh công bằng, các thành viên cần chạy cùng corpus, cùng 5 câu hỏi và cùng backend embedding thay vì trộn TF-IDF với multilingual embedding.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

Nhóm sẽ chuẩn hóa tài liệu PDF thành Markdown có heading rõ ràng, đặc biệt giữ riêng các bảng điều kiện và danh sách gạch đầu dòng. Mỗi chunk sẽ bổ sung metadata cấp mục như `section`, `article` hoặc `program_level` để lọc chính xác giữa đại học, thạc sĩ, tuyển sinh và tốt nghiệp. Với OSEP, nhóm sẽ tạo một chunk chuyên biệt cho mục 4.1 và dùng truy vấn mở rộng như “eligible criteria”, “CGPA 2.5”, “disciplinary action” để cải thiện recall.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **36 / 40** |
