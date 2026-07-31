# VLearn Adaptive Learning Loop — Tài liệu tổng hợp

**Venture Arena Khóa 3** · Tài liệu chính của dự án · Cập nhật 30/07/2026

> File này gộp toàn bộ: định hướng sản phẩm, canvas, kiến trúc, mô hình đo lường, cơ sở dữ liệu, luồng LLM, API, user story, lộ trình. Dùng làm nguồn tham chiếu duy nhất cho cả nhóm.

---

## Mục lục

1. [Tóm tắt sản phẩm](#1-tóm-tắt-sản-phẩm)
2. [Canvas 7 dòng](#2-canvas-7-dòng)
3. [Kiến trúc hai tầng](#3-kiến-trúc-hai-tầng)
4. [Mô hình đo lường: Elo và Mastery](#4-mô-hình-đo-lường-elo-và-mastery)
5. [Cơ sở dữ liệu](#5-cơ-sở-dữ-liệu)
6. [Luồng LLM](#6-luồng-llm)
7. [Pipeline seed nội dung](#7-pipeline-seed-nội-dung)
8. [API](#8-api)
9. [Tech stack](#9-tech-stack)
10. [User Story](#10-user-story)
11. [Luồng demo](#11-luồng-demo)
12. [Vấn đề đã biết và cách xử lý](#12-vấn-đề-đã-biết-và-cách-xử-lý)
13. [Đo lường hiệu quả](#13-đo-lường-hiệu-quả)
14. [Lộ trình 3 ngày](#14-lộ-trình-3-ngày)
15. [Glossary](#15-glossary)

---

## 1. Tóm tắt sản phẩm

**Vấn đề.** Sinh viên làm quiz xong chỉ biết đúng/sai, không biết mình yếu khái niệm nào và phải xem lại slide nào trong 50–70 slide. Kết quả: lật lại cả bài rồi bỏ cuộc, lần sau vẫn sai đúng chỗ cũ.

**Giải pháp.** Vòng lặp **Đo → Chữa → Đo lại**. Hệ thống theo dõi mức nắm (mastery) từng khái niệm bằng thuật toán Elo, chọn câu hỏi đúng vùng trình độ, và chỉ ra chính xác cụm slide cần đọc lại.

**Khác biệt.** Các nhóm khác đo "sinh được quiz". Chúng ta đo "mastery tăng bao nhiêu sau N vòng". LLM chỉ sản xuất nguyên liệu; quyết định cá nhân hoá do engine Elo thực hiện — deterministic, rẻ, giải thích được.

**Câu pitch một dòng:** *LLM viết đề, Elo phân phối đề.*

---

## 2. Canvas 7 dòng

| # | Mục | Nội dung |
|---|---|---|
| 1 | Chiến tuyến | VLearn — Adaptive Review (ôn tập thích ứng sau quiz) |
| 2 | Vai cụ thể | Học viên vừa nộp quiz sau bài giảng 50–70 slide |
| 3 | Vướng gì | Sai vài câu nhưng không biết yếu khái niệm nào, phải lật lại cả 60 slide để tự dò — mất 15–20 phút, thường bỏ cuộc, thi lại vẫn sai chỗ cũ |
| 4 | Bằng chứng | *(cần số thật — xem mẫu bên dưới)* |
| 5 | Lát cắt MỘT CÂU | Một học viên vừa nộp quiz · bấm xem kết quả · AI ước lượng khái niệm chưa vững từ các câu sai · trả về đúng 3 slide cần ôn kèm mức nắm từng khái niệm |
| 6 | AI tự làm đến đâu | AI tự gán câu sai → khái niệm và chọn slide khi concept map đã cover; báo "chưa đủ dữ liệu" khi câu nằm ngoài map — vì gợi ý sai slide làm học viên ôn lệch chỗ và mất niềm tin ngay lần đầu |
| 7 | Phân công | *(điền tên thật, mỗi người một phần riêng — CP5 hỏi ngẫu nhiên "phần của bạn là gì")* |

### Mẫu điền dòng 4 — bằng chứng

**Nhánh A — số liệu từ log (ưu tiên)**

1. Nguồn: export CSV bảng `quiz_attempts` từ VLearn admin (`user_id`, `quiz_id`, `question_id`, `is_correct`, `submitted_at`)
2. Phạm vi: môn, bài giảng, khoảng thời gian cụ thể
3. Đơn vị đếm: 1 dòng = 1 câu trả lời trong 1 lượt làm quiz của 1 học viên
4. Cách lọc: nhóm theo `user_id` + `quiz_id`, giữ học viên có ≥2 lượt nộp → còn **Y** học viên
5. Định nghĩa "sai lại chỗ cũ": `question_id` sai ở lượt 1 ∩ sai ở lượt 2; hai câu cùng concept tính là 1 concept sai lại
6. Kết quả: **X/Y học viên (Z%) sai lại ≥1 concept đã sai ở lượt trước**
7. Ai đếm, ngày nào, bằng script gì (nộp kèm script để tái lập)

**Nhánh B — câu nói nguyên văn (dự phòng)**

1. Tên thật + lớp
2. Câu nguyên văn, không diễn giải lại
3. Bối cảnh hỏi (khi nào, ở đâu)
4. Người thứ 2 nói ý tương tự

> **Tự kiểm:** con số có kèm cách đếm tái lập được không? Người khác cầm cùng dữ liệu có ra cùng con số không? Nếu không — chưa đạt.

---

## 3. Kiến trúc hai tầng

Đây là quyết định kiến trúc quan trọng nhất của dự án.

### Tầng LLM — Content factory (offline, 1 lần)

Đọc nội dung slide → sinh concept map → sinh ngân hàng câu hỏi → lọc → lưu DB.
Chạy lúc seed dữ liệu, **không chạy lúc người dùng bấm nút**.

### Tầng Engine — Decision engine (runtime, toán thuần)

Cập nhật Elo sau mỗi câu trả lời · chọn concept yếu · chọn câu ở độ khó phù hợp · chọn cụm slide cần ôn.
Không gọi LLM, latency < 100ms, không tốn token, không phụ thuộc uptime của LLM API.

### Vì sao tách

| Tiêu chí | Sinh runtime (không tách) | Sinh trước (tách tầng) |
|---|---|---|
| Thời gian chờ | 2–5 giây mỗi lần tạo quiz | < 100ms |
| Chất lượng câu | Mỗi lần khác nhau, không kiểm duyệt kịp | Đọc duyệt trước, loại câu tệ |
| Độ khó câu | Chưa ai làm → không ước lượng được | Hiệu chỉnh dần theo dữ liệu thật |
| Chi phí | Token mỗi request | Một lần duy nhất |
| Trả lời "AI quyết định gì" | "LLM sinh câu hỏi" (trùng mọi nhóm) | "Engine chọn câu nào cho ai, lúc nào" |

### Vì sao không dùng RAG cho quiz

Hệ đã biết chính xác học viên yếu concept nào → tra bằng khoá (`WHERE concept_id = 'c4'`), không cần tìm mờ bằng vector.
RAG chỉ dùng cho chatbot (P1), nơi câu hỏi tự do và không biết trước đoạn nào liên quan.

---

## 4. Mô hình đo lường: Elo và Mastery

### Ba tầng khái niệm

| Tên | Kiểu | Nơi lưu | Dùng để |
|---|---|---|---|
| `elo` | số nguyên (1100–1800) | **Lưu DB** — nguồn sự thật | Tính toán |
| `mastery` | % (0–100) | Không lưu — tính từ `elo` | Hiển thị cho người dùng |
| `mastery_state` | `weak` / `learning` / `mastered` | Không lưu — suy ra | Logic chọn slide ôn |

Không lưu `mastery` và `mastery_state` vào DB để tránh lệch dữ liệu — luôn tính lại từ `elo`.

### Công thức

**Khởi tạo từ khảo sát đầu vào** (giải quyết cold-start):

$$S_0 = 1200 + 100 \times v, \quad v \in [1,5]$$

**Cập nhật sau mỗi câu trả lời** (đối xứng — cả học viên và câu hỏi cùng được hiệu chỉnh):

$$p = \frac{1}{1 + 10^{(D_q - S_{u,c})/400}}$$

$$S \leftarrow S + K(y - p), \qquad D_q \leftarrow D_q - K'(y - p)$$

với $y \in \{0,1\}$ là đúng/sai; $K = 40$ khi $n < 10$ rồi giảm về 20; $K' = 8$ vì độ khó câu chỉ nên nhích chậm.

**Mastery — luôn neo vào độ khó chuẩn cố định $D_{\text{ref}} = 1500$:**

$$M_{u,c} = \frac{1}{1 + 10^{(1500 - S_{u,c})/400}} \times 100\%$$

> **Lỗi cần tránh:** đừng tính mastery so với độ khó câu vừa làm. Mốc trôi thì % hôm nay không so được với hôm qua, và màn "trước → sau" mất ý nghĩa.

### Ngưỡng

| State | Điều kiện | Hành vi hệ thống |
|---|---|---|
| `weak` | mastery < 50% | Đưa vào lộ trình ôn, ưu tiên ra câu hỏi |
| `learning` | 50% ≤ mastery < 75% | Tiếp tục luyện, không bắt ôn slide |
| `mastered` | mastery ≥ 75% **và** ≥ 5 lượt | Loại khỏi danh sách ưu tiên |

Ràng buộc số lượt là cần thiết: đúng 2/2 câu may mắn không phải là thành thạo.

### Chọn câu hỏi tiếp theo

Chọn câu có $|item\_elo - user\_elo|$ nhỏ nhất trong pool chưa làm → xác suất đúng ≈ 50%, vùng học hiệu quả nhất. Người dùng có thể ghi đè: dễ hơn (P≈75%) hoặc thử thách (P≈30%).

### Vì sao không dùng "% đúng" cho gọn

- **% đúng không phân biệt độ khó.** Đúng 3 câu dễ và đúng 1 câu khó đều ra 100%, nhưng là hai trình độ khác nhau.
- **% đúng không cộng dồn.** Vòng 1 được 40%, vòng 2 được 60% — do giỏi lên hay do câu dễ hơn? Không trả lời được.
- **% đúng không chọn được câu tiếp theo.** Không có thang năng lực thì mọi câu như nhau, "quiz thích ứng" chỉ còn là lọc theo concept.

Elo chỉ khoảng 15 dòng code. Chi phí thật nằm ở cách diễn đạt, không ở thuật toán.

---

## 5. Cơ sở dữ liệu

**Postgres (Supabase)** cho cả dữ liệu quan hệ và vector — một instance, dễ deploy nhiều đội.

```sql
-- ============ Nội dung gốc ============
CREATE TABLE lectures (
  lecture_id  TEXT PRIMARY KEY,
  title       TEXT,
  n_slides    INT,
  summary     TEXT           -- tóm tắt cả bài (~200 token), chèn vào prompt chatbot
);

CREATE TABLE slides (
  lecture_id  TEXT REFERENCES lectures,
  slide_no    INT,
  title       TEXT,
  body_text   TEXT,          -- text trích từ PDF/PPTX
  image_url   TEXT,          -- ảnh render trang, để hiển thị
  PRIMARY KEY (lecture_id, slide_no)
);

-- ============ Tri thức do LLM trích xuất ============
CREATE TABLE concepts (
  concept_id  TEXT PRIMARY KEY,          -- 'c4'
  lecture_id  TEXT REFERENCES lectures,
  name        TEXT,                      -- 'L1 Regularization'
  prereq_id   TEXT REFERENCES concepts,  -- concept tiên quyết, nullable
  embedding   VECTOR(1536)               -- P1, chỉ dùng cho chatbot
);

CREATE TABLE slide_concept (
  lecture_id   TEXT,
  concept_id   TEXT REFERENCES concepts,
  slide_start  INT,                      -- CỤM slide, không phải slide đơn
  slide_end    INT,
  PRIMARY KEY (lecture_id, concept_id, slide_start)
);

CREATE TABLE questions (
  question_id   SERIAL PRIMARY KEY,
  concept_id    TEXT REFERENCES concepts,
  stem          TEXT,
  options       JSONB,
  answer_idx    INT,
  explanation   TEXT,
  item_elo      INT DEFAULT 1500,        -- độ khó, tự hiệu chỉnh theo attempts
  source_slide  INT,                     -- truy vết về slide gốc
  reviewed      BOOL DEFAULT FALSE       -- đã người duyệt chưa
);

-- ============ Người dùng & tiến trình ============
CREATE TABLE users (
  user_id     SERIAL PRIMARY KEY,
  name        TEXT,
  email       TEXT UNIQUE,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE mastery (
  user_id     INT REFERENCES users,
  concept_id  TEXT REFERENCES concepts,
  elo         INT DEFAULT 1400,
  n_attempts  INT DEFAULT 0,
  updated_at  TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, concept_id)
);

CREATE TABLE attempts (
  attempt_id  SERIAL PRIMARY KEY,
  user_id     INT REFERENCES users,
  question_id INT REFERENCES questions,
  correct     BOOL,
  round_no    INT,
  created_at  TIMESTAMPTZ DEFAULT now()
);
```

### Ba truy vấn chạy toàn bộ cá nhân hoá

```sql
-- 1. Concept yếu nhất của học viên trong bài đang học
SELECT m.concept_id, m.elo FROM mastery m
JOIN concepts c USING (concept_id)
WHERE m.user_id = 42 AND c.lecture_id = 'day05'
ORDER BY m.elo LIMIT 3;

-- 2. Câu chưa làm, độ khó gần Elo học viên (vùng P≈50%)
SELECT * FROM questions q
WHERE q.concept_id = 'c4'
  AND q.reviewed = TRUE
  AND q.question_id NOT IN (SELECT question_id FROM attempts WHERE user_id = 42)
ORDER BY abs(q.item_elo - 1300) LIMIT 5;

-- 3. Cụm slide cần ôn
SELECT slide_start, slide_end FROM slide_concept
WHERE lecture_id = 'day05' AND concept_id IN ('c4','c3')
ORDER BY slide_start;
```

### Phân biệt ba thứ dễ lẫn

| Bảng | Là gì | Ai tạo |
|---|---|---|
| `slides.body_text` | Nội dung gốc của bài giảng | Pipeline trích text |
| `concepts` | Nhãn khái niệm trích ra từ nội dung đó | LLM |
| `questions` | Câu hỏi viết dựa trên nội dung đó | LLM |

`slide_concept` là cầu nối — nhờ nó mà từ "yếu concept c4" ra được "đọc lại slide 33–35".

---

## 6. Luồng LLM

**4 điểm gọi LLM, chỉ 1 chạy lúc người dùng thao tác.**

| # | Khi nào | Việc | Số call |
|---|---|---|---|
| 1 | Offline · seed | Trích text từ slide | 0 (PyMuPDF, không LLM) |
| 2 | Offline · seed | Sinh concept map | 1 call/bài |
| 3 | Offline · seed | Sinh ngân hàng câu hỏi | 1 call/concept (~12/bài) |
| 4 | Offline · seed | Tự kiểm chất lượng câu | 1 call/câu (batch) |
| 5 | **Runtime** | Chat hỏi bài (P1) | 2 call/lượt hỏi |

**Tạo quiz, chấm điểm, gợi ý slide ôn — không gọi LLM.** Chỉ SQL + Elo.

### Chi tiết từng bước

**Bước 2 — concept map.** Input: toàn bộ text bài giảng. Output JSON: 10–15 concept, mỗi concept có `slide_start`/`slide_end` và `prereq_id`.

**Bước 3 — sinh câu hỏi.** Lặp theo từng concept, mỗi lần chỉ đưa 2–4 slide của concept đó và xin 8–10 câu. **Không gộp một call cho cả bài** — output dài thì chất lượng đoạn cuối tụt rõ.

Ràng buộc bắt buộc trong prompt:
- Sinh **chỉ từ nội dung slide được cung cấp**, không thêm kiến thức ngoài
- Mỗi distractor phản ánh **một hiểu lầm phổ biến cụ thể** (VD nhầm L1 với L2), không sai lộ liễu
- Ghi rõ đáp án đúng, giải thích, slide nguồn

**Bước 4 — tự kiểm.** Cho LLM trả lời chính câu nó vừa sinh, không kèm đáp án. Trả lời sai → câu mơ hồ → loại. Rẻ và lọc được nhiều rác trước khi người đọc duyệt tay.

**Bước 5 — chat runtime, định tuyến 2 tầng** (thay vì vector search toàn kho):
- Call 1 (rẻ): đưa ~60 tên concept của cả môn (~500 token) + câu hỏi → model trả về 1–3 `concept_id`
- Call 2: `SELECT` slide của concept đó (~2–3k token) + câu hỏi → trả lời kèm số trang
- Fallback: không khớp concept nào → giới hạn trong `lecture_id` đang mở

Ưu điểm so với embedding: định tuyến theo **khái niệm** thay vì độ giống chữ, nên câu hỏi xuyên slide vẫn kéo đủ ngữ cảnh; câu trả lời truy được về concept + slide nguồn.

**Tổng chi phí seed một bài giảng ≈ 15 call + batch tự kiểm, chạy một lần.** Sau đó toàn bộ vòng lặp học tập không tốn token nào.

---

## 7. Pipeline seed nội dung

### Bước 1 — Trích text từ slide

| Nguồn | Công cụ | Ghi chú |
|---|---|---|
| `.pptx` (ưu tiên) | `python-pptx` | Text sạch theo shape, có cả speaker notes |
| `.pdf` | **PyMuPDF (fitz)** | Mặc định: nhanh, `page.get_text()` theo trang, Unicode tiếng Việt ổn |
| Slide dạng ảnh/sơ đồ | VLM (render ảnh → vision model) | Fallback khi text layer < 50 ký tự |
| Slide scan thuần | OCR (PaddleOCR, model `vi`) | Hiếm dùng |

**Chiến lược lai:** chạy PyMuPDF trước, đếm ký tự mỗi trang; trang nào dưới ngưỡng thì render ảnh và đẩy qua VLM. Tránh mất concept nằm trong sơ đồ.

### Bước 2–4 — LLM

Xem [mục 6](#6-luồng-llm).

### Bước 5 — Hiệu chỉnh `item_elo` trước demo

Chạy vài lượt trả lời thử (hoặc simulated learner) để `item_elo` phản ánh độ khó thật. Không có bước này thì "chọn câu ở vùng P≈50%" chỉ là chữ trên slide pitch — vì nhãn khó/dễ do LLM gán lúc sinh không đáng tin.

### Sản lượng mục tiêu

12 concept × 8–10 câu ≈ **100–120 câu/bài giảng** — đủ cho một học viên chạy 5–7 vòng không lặp câu.

---

## 8. API

**FastAPI**, 9 endpoint. P0 = bắt buộc cho MVP.

| # | Method | Endpoint | Mô tả | Ưu tiên |
|---|---|---|---|---|
| 1 | POST | `/auth/register` | Tạo tài khoản | P0 |
| 2 | POST | `/auth/login` | Đăng nhập, trả session token | P0 |
| 3 | POST | `/users/me/survey` | Nộp khảo sát → khởi tạo Elo prior per concept | P0 |
| 4 | GET | `/users/me/mastery?lecture_id=` | Mastery hiện tại per concept | P0 |
| 5 | POST | `/quizzes/generate` | `{lecture_id, concept_ids?, n, difficulty}` → danh sách câu + P(đúng) | P0 |
| 6 | POST | `/attempts` | `{question_id, answer}` → `{correct, elo_delta, mastery_new}` | P0 |
| 7 | GET | `/users/me/review-path?lecture_id=` | 3–5 slide cần ôn theo concept yếu | P0 |
| 8 | GET | `/lectures/{id}/concepts` | Concept map của bài giảng | P1 |
| 9 | POST | `/chat/ask` | Hỏi bài — định tuyến concept → lấy slide → LLM trả lời | P1 |

**Ghi chú thiết kế:**

- Endpoint 6 nhận **từng câu**, không phải cả bài — Elo cập nhật online sau mỗi response, đúng bản chất thuật toán và cho phép adaptive ngay trong lúc làm bài sau này.
- Endpoint 5 với `concept_ids` bỏ trống = engine tự chọn concept yếu nhất (mặc định, đúng tinh thần cá nhân hoá).
- Endpoint 1–7 không gọi LLM.

---

## 9. Tech stack

| Thành phần | Công cụ | Vai trò |
|---|---|---|
| Backend | FastAPI | Toàn bộ endpoint, gọi LLM lúc seed, tính Elo |
| CSDL | Postgres (Supabase) + pgvector | Dữ liệu quan hệ + embedding (P1) trong một instance |
| Trích text | PyMuPDF / python-pptx | Pipeline seed |
| LLM | API (Claude/GPT) | Sinh concept map + ngân hàng câu hỏi (offline), chat (P1) |
| Embedding | OpenAI/Voyage | P1, chỉ cho chatbot |
| Frontend | HTML/JS tĩnh | Gọi API qua `fetch` |
| Hosting | Railway / Render | ⚠️ **Cần xác minh Cloudflare Workers chạy được FastAPI (Python ASGI) trước khi chốt** |

---

## 10. User Story

### Nhóm A — Vào hệ thống (P0)

**A1.** Là sinh viên mới, tôi muốn **đăng ký và làm khảo sát 30 giây**, để quiz đầu tiên đúng trình độ chứ không phải câu ngẫu nhiên.
*AC:* Nộp khảo sát → mỗi concept có Elo prior khác nhau theo câu trả lời; mở tab học thấy concept yếu đã được đánh dấu.

**A2.** Là sinh viên cũ, tôi muốn **đăng nhập và thấy lại mastery lần trước**, để học tiếp chứ không bắt đầu lại từ đầu.
*AC:* Mastery và danh sách câu đã làm được giữ nguyên sau đăng xuất/đăng nhập.

### Nhóm B — Vòng lặp lõi (P0)

**B1.** Là sinh viên vừa học xong bài, tôi muốn **tạo quiz mà không phải tự cấu hình**, để không phải đoán mình yếu chỗ nào.
*AC:* Mở màn tạo quiz → concept yếu nhất đã được tick sẵn kèm % mastery; bấm một nút là ra đề.

**B2.** Là sinh viên đang làm quiz, tôi muốn **câu hỏi vừa sức**, để không nản vì quá khó hay chán vì quá dễ.
*AC:* Câu được chọn có `|item_elo − mastery_elo|` nhỏ nhất trong pool; không lặp câu đã làm; UI hiện P(đúng) dự đoán.

**B3.** Là sinh viên vừa trả lời sai, tôi muốn **biết đọc lại slide nào**, để không phải lật cả 62 slide.
*AC:* Nộp bài → hiện ≤3 cụm slide, mỗi cụm gắn concept sai; bấm mở là trình xem nhảy đúng trang.

**B4.** Là sinh viên đã ôn xong, tôi muốn **làm lại vòng mới với câu khác**, để kiểm chứng mình đã hiểu thật chứ không phải nhớ đáp án.
*AC:* Vòng N+1 không lặp câu của vòng N; concept được chọn lại theo Elo mới.

**B5.** Là sinh viên kết thúc buổi học, tôi muốn **thấy mình tiến bộ bao nhiêu**, để biết thời gian bỏ ra có đáng.
*AC:* Màn kết quả hiện mastery đầu → cuối, delta từng concept, số vòng đã chạy.

### Nhóm C — Hỏi bài (P1)

**C1.** Là sinh viên đang đọc slide, tôi muốn **hỏi và nhận câu trả lời có số trang**, để kiểm chứng được thay vì tin mù.
*AC:* Trả lời kèm ≥1 slide nguồn; câu hỏi xuyên slide ("bài này có mấy kỹ thuật regularization?") vẫn kéo đủ ngữ cảnh cùng bài.

### Nhóm D — Vận hành nội dung (P1)

**D1.** Là người seed dữ liệu, tôi muốn **duyệt và loại câu hỏi kém chất lượng**, để học viên không gặp câu vô nghĩa trong demo.
*AC:* Chỉ câu có `reviewed = TRUE` mới được đưa vào quiz.

### Ưu tiên khi thiếu thời gian

Nhóm B là **lát cắt trong canvas**. Nếu phải cắt: cắt nhóm C trước, rồi D. **Không cắt B3** — "biết đọc lại slide nào" chính là "1 công việc" đã cam kết.

---

## 11. Luồng demo

1. **Mở** tab "Học thích ứng" → hệ thống đã tick sẵn concept đang yếu (kèm % mastery), bấm **"Tạo quiz vòng 1"**
2. **Làm** quiz 4 câu (câu hỏi ở độ khó ≈50% theo trình độ cá nhân) → bấm **Nộp bài**
3. **Ra** ngay: điểm số + thanh mastery từng concept + danh sách **3 slide cần đọc lại**
4. **Bấm** "Mở slide" → trình xem nhảy thẳng đến trang đó, đọc xong đánh dấu ✓
5. **Bấm** "Quiz vòng 2" → hệ thống sinh bộ câu mới theo mastery vừa cập nhật → làm lại
6. **Bấm** "Kết thúc" → màn hình so sánh mastery **trước → sau** (VD: 32% → 58%)

Mỗi học viên nhận quiz và lộ trình ôn khác nhau vì mọi lựa chọn (concept, độ khó, slide) đều tính từ hồ sơ mastery cá nhân.

---

## 12. Vấn đề đã biết và cách xử lý

### Slide rời rạc, mất ngữ cảnh

Slide trong bài giảng liên kết với nhau; đưa slide đơn lẻ thì người đọc khó hiểu và LLM mất ngữ cảnh. Bốn biện pháp:

1. **Lưu theo cụm** — `slide_concept` có `slide_start`/`slide_end`, concept L1 là slide 33–35 chứ không phải riêng 33
2. **Dùng `prereq_id`** — yếu c4 mà c1 cũng yếu thì xếp c1 lên trước, lộ trình có thứ tự sư phạm
3. **Tóm tắt cả bài** sinh sẵn (`lectures.summary`), chèn đầu mọi prompt chatbot
4. **Câu dẫn nối** sinh sẵn cho người học: *"Phần này tiếp nối ý bias–variance ở slide 8…"*

Cộng thêm padding ±1 slide khi đưa vào prompt.

### Cạn ngân hàng câu hỏi

Học viên chăm chỉ sẽ hết câu chưa làm → gặp lại câu cũ → học thuộc đáp án thay vì hiểu.
**Xử lý hybrid:** khi một concept còn dưới 3 câu chưa dùng cho user đó, gọi LLM sinh bổ sung 5 câu trong nền, INSERT vào bảng. Pre-generated là chính, sinh bổ sung khi cạn.

### `item_elo` do LLM gán không đáng tin

Nhãn khó/dễ do LLM tự gán lúc sinh không phản ánh độ khó thật.
**Giải pháp:** `item_elo` tự hiệu chỉnh — sau mỗi attempt, câu bị trả lời sai nhiều thì Elo của nó tăng. Ngân hàng câu tự học độ khó từ dữ liệu.

### Trần chất lượng câu hỏi

50–70 slide chỉ chứa lượng mệnh đề hữu hạn. Ép sinh 15 câu/concept thì câu thứ 8 trở đi thành trùng lặp hoặc vụn vặt. Giữ ở 8–10 câu/concept.

### Cá nhân hoá vô hình với người dùng

Người dùng không biết Elo là gì, chỉ thấy "chip được tick sẵn". Cần chỗ **phô ra** sự cá nhân hoá: hiển thị % mastery trên chip, hiện P(đúng) dự đoán trên mỗi câu, và dòng giải thích "bạn nhận bộ câu này vì đang yếu L1".

---

## 13. Đo lường hiệu quả

### Track 1 — Simulated learner (chạy trước, luôn có số)

50+ học viên mô phỏng, so sánh **adaptive vs random item selection**, cùng seed khởi tạo.
Chỉ số: số câu cần để đạt ngưỡng mastery, độ chính xác post-test sau N câu.
Lưu ý khi trình bày: đây là bằng chứng sàng lọc trước triển khai, không phải hiệu quả lớp học đã kiểm chứng.

### Track 2 — Pre/post người thật (chạy ngày 3)

5–15 bạn cùng lớp: pretest → một phiên ôn thích ứng → posttest.
Chỉ số: **normalized gain** $g = \frac{post - pre}{100 - pre}$.

### Chỉ số baseline tái lập được (cho dòng 4 canvas)

**Tỉ lệ lặp lỗi:** % học viên sai lại cùng concept ở ≥2 lượt liên tiếp — đếm trực tiếp từ bảng `attempts`, nộp kèm script để người khác tái lập.

---

## 14. Lộ trình 3 ngày

| Ngày | Việc | Tiêu chí xong | Ai |
|---|---|---|---|
| **1** | Pipeline seed: parse slide → LLM sinh concept + câu hỏi → INSERT → **duyệt tay** | DB có 1 bài giảng, 10–12 concept, ~80 câu `reviewed = TRUE` | *(điền tên)* |
| **2** | 7 endpoint P0 + Elo engine; nối frontend hiện có vào API thật | Chạy hết được một vòng đo → chữa → đo lại trên dữ liệu thật | *(điền tên)* |
| **3** | Chạy thử với 5–10 bạn, lấy số pre/post, sửa lỗi. **Không thêm tính năng** | Có con số cho slide pitch | *(điền tên)* |

### Phạm vi MVP

**Giữ:** 1 bài giảng seed sẵn · đăng nhập tối giản + khảo sát 3 câu · vòng lặp đo→chữa→đo lại · màn kết quả trước/sau.

**Cắt (làm sau nếu còn giờ):** chatbot hỏi bài · pgvector/embedding · upload tài liệu động · nhiều bài giảng · dark mode · bút/highlight · sinh câu runtime.

### Rủi ro theo dõi

1. **Chất lượng câu hỏi** — engine chạy đúng nhưng câu vô nghĩa thì demo vẫn sập. Dành ≥2 giờ ngày 1 duyệt tay.
2. **Hosting FastAPI** — xác minh sớm, đừng để đến ngày 3.
3. **Thời gian duyệt tay** — dễ bị đánh giá thấp.

---

## 15. Glossary

| Thuật ngữ | Định nghĩa |
|---|---|
| **Concept** | Khái niệm trong bài giảng (VD "L1 Regularization"), do LLM trích từ slide. Đơn vị đo mastery. |
| **Concept map** | Tập concept của một bài giảng + quan hệ tiên quyết giữa chúng. |
| **Elo** | Số nguyên đo năng lực học viên trên một concept, hoặc độ khó một câu hỏi. Lưu DB. |
| **Mastery** | % suy ra từ Elo, neo vào độ khó chuẩn 1500. Chỉ để hiển thị, không lưu. |
| **Mastery state** | Nhãn `weak`/`learning`/`mastered`, suy ra từ mastery + số lượt. Dùng cho logic review. |
| **Item Elo** | Độ khó câu hỏi, tự hiệu chỉnh theo dữ liệu trả lời thật. |
| **Cold start** | Vấn đề user mới chưa có dữ liệu. Giải bằng khảo sát đầu vào → Elo prior. |
| **Review path** | Danh sách cụm slide cần đọc lại, chọn theo concept yếu. |
| **Vòng (round)** | Một lần đo → chữa → đo lại trong phiên học. |
| **Decision engine** | Phần backend chọn concept, câu hỏi, slide — toán thuần, không gọi LLM. |
| **Content factory** | Pipeline LLM offline sinh concept map + ngân hàng câu hỏi. |
