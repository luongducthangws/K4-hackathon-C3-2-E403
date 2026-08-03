# NHẬT KÝ PHẢN TƯ CÁ NHÂN (REFLECTION LOG)
**Học viên:** Nguyễn Hoàng Vũ
**Vai trò trong dự án:** Build AI & Thiết lập Hệ thống RAG (Retrieval-Augmented Generation / VLearn Tutor Chatbot)

---

## 1. Vai trò & Phần việc đảm nhận (Role & Contributions)
Trong dự án này, tôi chịu trách nhiệm chính về mảng **Thiết kế và Triển khai Hệ thống RAG & AI Chatbot** nhằm hỗ trợ học viên giải đáp các thắc mắc về nội dung bài giảng:
- **Thiết kế Kiến trúc RAG bằng LangGraph:** Xây dựng luồng xử lý Agent với StateGraph gồm 2 node chính:
  - `route_node`: Sử dụng LLM (`gemini-3.5-flash`) định tuyến câu hỏi của học viên vào 1-3 khái niệm (`concept_id`) tương ứng trong bài giảng, hoặc phát hiện các câu hỏi ngoài đề (out-of-scope/phiếm) để từ chối sớm (IRRELEVANT).
  - `retrieve_node`: Truy xuất thông tin từ database PostgreSQL/SQLite bao gồm tóm tắt bài giảng và nội dung các trang slide tương ứng dựa trên `concept_ids` được định tuyến hoặc trích xuất số trang slide cụ thể (`slide|trang #`) từ prompt của người học.
- **Xây dựng cơ chế Quản lý Lịch sử (Memory Management):** Sử dụng `MemorySaver` của LangGraph để lưu trữ trạng thái hội thoại. Thiết lập Composite Thread ID theo cấu trúc `user_id + lecture_id` để phân tách phiên trò chuyện theo từng học viên và bài học, tự động xóa bộ nhớ chat cũ khi học viên chuyển sang ngày học/bài học mới.
- **Tối ưu hóa Trải nghiệm Phản hồi (Streaming & Reasoning):** 
  - Triển khai luồng Stream response sử dụng FastAPI `StreamingResponse` kết hợp Server-Sent Events (SSE) để hiển thị câu trả lời dạng chữ chạy (mượt mà hơn so với chờ toàn bộ câu trả lời).
  - Tích hợp khả năng hiển thị luồng suy luận nội tâm (reasoning/thinking process) của các mô hình lý luận lên giao diện, giúp học viên không có cảm giác giao diện bị treo khi AI đang xử lý thông tin phức tạp.

---

## 2. AI đã hỗ trợ như thế nào? (AI Assistance)
Các công cụ AI (Cursor/Claude) đã hỗ trợ tôi rất nhiều trong việc hiện thực hóa hệ thống RAG phức tạp này:
- **Tăng tốc triển khai LangGraph:** AI hỗ trợ tạo khung code mẫu (boilerplate) cho StateGraph, định nghĩa `AgentState` và xử lý các conditional edges một cách chuẩn xác, giúp giảm thiểu thời gian đọc tài liệu thư viện.
- **Tinh chỉnh System Prompt định tuyến:** Viết prompt hệ thống là khâu tốn thời gian. AI đã giúp tôi tối ưu prompt định tuyến cho `route_node` để phân biệt rõ câu hỏi thuộc phạm vi bài giảng với các câu hỏi phiếm, đảm bảo mô hình luôn trả về kết quả định dạng có cấu trúc (`RELEVANT: id` hoặc `IRRELEVANT: từ chối`).
- **Xử lý bất đồng bộ (Async/Streaming):** Khi tích hợp luồng streaming từ LangGraph vào endpoint API FastAPI, AI đã hỗ trợ gỡ lỗi và đưa ra giải pháp cấu trúc generator thích hợp để truyền tải dữ liệu chunk-by-chunk mượt mà về client.

---

## 3. Bài học từ một Case Fail của chính nhóm (Lesson from a Team Failure Case)
**Sự cố gặp phải:**
Trong quá trình chạy thử tính năng VLearn Tutor Chatbot ở bài giảng Day 02, chatbot liên tục báo lỗi hệ thống hoặc phản hồi "Chưa đủ dữ liệu" dù câu hỏi nằm hoàn toàn trong nội dung bài giảng. Hệ thống RAG không thể tìm thấy slide liên quan để đưa vào ngữ cảnh.

**Nguyên nhân:**
Có hai nguyên nhân chính:
1. **Lỗi định danh tài liệu (Identifier Mismatch):** Frontend truyền tên bài giảng lên là `day02`, nhưng backend database và concept map lại lưu trữ dưới tên `d2-xac-dinh-bai-toan`. Do đó, truy vấn lấy thông tin slide/concept từ database trả về kết quả rỗng.
2. **Thiếu cơ chế dự phòng (Missing Fallback):** Hệ thống RAG ban đầu chỉ dựa hoàn toàn vào các concept được định tuyến để lấy slide. Khi định tuyến lỗi hoặc concept rỗng, RAG không lấy được slide nào và ngay lập tức dừng hoặc trả thông tin nghèo nàn.

**Bài học rút ra:**
1. **Thống nhất API Spec & Data Alignment:** Cần thiết kế và chốt spec cấu trúc dữ liệu sớm giữa tất cả các phần (UI, Database, AI Engine), sử dụng một bộ định danh chuẩn. Chúng tôi đã khắc phục bằng cách thiết kế hàm `resolve_lecture_id` để ánh xạ mọi dạng alias về tên bài học chuẩn.
2. **Thiết kế RAG bền bỉ (Robust RAG):** Khi xây dựng RAG, cần có chiến lược Fail-safe. Trong `retrieve_node`, tôi đã thêm một lớp dự phòng (Fallback): Nếu không xác định được concept cụ thể nào từ câu hỏi nhưng câu hỏi vẫn hợp lệ, RAG sẽ load toàn bộ nội dung tóm tắt và slide của bài giảng đó làm ngữ cảnh thay vì trả về rỗng. Điều này đảm bảo AI luôn có dữ liệu nền tảng để trả lời người học.
