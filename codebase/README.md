# VLearn Adaptive Review — Prototype Codebase

Thư mục này chứa toàn bộ mã nguồn của prototype **VLearn Adaptive Review (Ôn tập thích ứng sau Quiz)**.

---

## 1. Cấu trúc mã nguồn (Code Structure)

```
codebase/
├── backend/
│   ├── database.py       # Cấu hình SQLAlchemy kết nối CSDL (PostgreSQL/SQLite)
│   ├── elo.py            # Công thức ELO cập nhật độ mastery của học viên sau quiz
│   ├── graph.py          # Luồng xử lý định tuyến RAG sử dụng LangGraph
│   ├── main.py           # FastAPI endpoints, xử lý Streaming Response, SSE
│   ├── models.py         # SQLAlchemy ORM Models (User, Concept, Attempt, Slide...)
│   └── schemas.py        # Pydantic Schemas định nghĩa dữ liệu API
├── scripts/
│   ├── build_concept_map.py  # Xây dựng bản đồ khái niệm (Concept Map) từ slides
│   ├── build_questions.py    # Xây dựng ngân hàng câu hỏi, kiểm thử, xoay vòng đáp án
│   ├── seed_all.py           # Seed toàn bộ dữ liệu mẫu bài giảng, slide, câu hỏi
│   └── seed_questions.py     # Script seed câu hỏi và concepts bổ sung
├── vlearn-adaptive-loop-v7.html # Giao diện Frontend hiển thị slide & Chatbot RAG
├── requirements.txt      # Thư viện Python phụ thuộc
└── cli.py                # Command Line Tool để kiểm thử nhanh
```

---

## 2. Phân định AI thật vs. Mock/Quy tắc (AI vs. Mock/Rules)

Để phục vụ chấm điểm tiêu chí **R5 · Prototype chạy được**, dưới đây là chi tiết các thành phần thực tế và thành phần giả lập/quy tắc:

### A. Thành phần AI chạy thật (Real AI Calls)
* **Bộ định tuyến câu hỏi (Router Node - `backend/graph.py`):** Sử dụng mô hình `gemini-3.5-flash` để phân tích câu hỏi học viên trong thời gian thực, tự động gán vào tối đa 3 khái niệm (`concept_id`) trong bài học hoặc trả về trạng thái từ chối `IRRELEVANT` nếu câu hỏi ngoài luồng (chit-chat, spam).
* **AI Giải đáp bài học (Generator - `backend/main.py`):** Sử dụng Gemini hoặc FPT Cloud API để tạo phản hồi dựa trên ngữ cảnh slide đã trích xuất, truyền dữ liệu theo dạng streaming (SSE) từng từ về UI.
* **Tích hợp Reasoning Process:** Hiển thị tiến trình suy luận (thought process) trực quan lên giao diện trong lúc mô hình lý luận (Reasoning Model) xử lý câu hỏi.

### B. Thành phần Mock & Quy tắc (Mock/Rule-based)
* **Concept Map & Quiz Mapping:** Bản đồ khái niệm (liên kết Concept $\leftrightarrow$ Slide) và ngân hàng câu hỏi (liên kết Question $\leftrightarrow$ Concept) được xây dựng tĩnh thông qua file JSON ở thư mục dữ liệu nhằm bảo đảm tính chính xác tuyệt đối về mặt chuyên môn cho bài học demo.
* **Mastery ELO Model:** Công thức tính mastery và cập nhật ELO của học viên được xử lý dựa trên thuật toán ELO chuẩn (`backend/elo.py`) thay vì dùng AI ước lượng, giúp đảm bảo tính nhất quán và thất bại an toàn (Fail-safe).
* **Database & Seeded Users:** Dữ liệu học viên, quiz attempt ban đầu được nạp sẵn bằng script seed dữ liệu để dễ dàng kiểm thử các trường hợp khác nhau (người dùng mới vs. người dùng đã học sâu).

---

## 3. Hướng dẫn khởi chạy (How to Run)

### Bước 1: Thiết lập môi trường và cài đặt thư viện
1. Di chuyển vào thư mục codebase:
   ```bash
   cd codebase
   ```
2. Tạo và kích hoạt môi trường ảo:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```

### Bước 2: Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc của repository với các thông tin:
```env
GEMINI_API_KEY="your-gemini-api-key"
DATABASE_URL="sqlite:///./vlearn.db" # Hoặc postgresql://user:pass@host/dbname
```

### Bước 3: Khởi tạo và nạp dữ liệu mẫu
Chạy script seed dữ liệu để khởi tạo database SQLite và nạp toàn bộ bài học mẫu:
```bash
python scripts/seed_all.py
```

### Bước 4: Chạy Backend Server
Khởi chạy server FastAPI sử dụng Uvicorn:
```bash
uvicorn backend.main:app --reload
```

### Bước 5: Truy cập ứng dụng
Mở trình duyệt và truy cập:
* Giao diện học viên: `http://localhost:8000/` (được tự động trỏ tới file `vlearn-adaptive-loop-v7.html`)
* Tài liệu API Swagger: `http://localhost:8000/docs`
