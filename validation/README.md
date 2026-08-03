# NHẬT KÝ KIỂM THỬ NGƯỜI DÙNG — USER VALIDATION LOG
**Nhóm:** C3-2 · Zone A
**Deliverable:** Feedback Log & Phân tích Cải tiến từ User Test

Vòng kiểm thử được thực hiện với 5 người dùng ngoài nhóm (bao gồm 2 Willing Users đã đăng ký từ mốc CP1 và 3 thành viên từ các zone khác). Mỗi phiên test kéo dài 10 phút.

---

## 1. Bảng Nhật ký Feedback (Feedback Log)

| Người thử (Tên/Vai — Willing User?) | Task Giao | Quan sát của Nhóm | Quote Nguyên Văn | Mức Nghiêm Trọng |
|---|---|---|---|:---:|
| **Trần Văn An** <br> *(Học viên K4 - Willing User)* | Làm quiz bài Day 02 $\rightarrow$ Xem gợi ý slide cần ôn $\rightarrow$ Click xem slide. | Khi gửi quiz ở bài giảng Day 02, màn hình gợi ý slide hoàn toàn trống trơn. Học viên bối rối tưởng mạng bị lỗi và F5 liên tục. | *"Ủa sao mình làm bài Day 02 xong nó không ra danh sách ôn tập gì hết vậy? Màn hình trắng xóa luôn nè, có lỗi gì không nhóm?"* | **Cao** <br> (Blocker) |
| **Nguyễn Thị Lan** <br> *(Học viên K4 - Willing User)* | Chat với AI Tutor để hỏi sâu hơn về nội dung Slide 12 (Day 01). | Nhập câu hỏi và bấm gửi, màn hình đơ khoảng 4-5 giây trước khi hiển thị toàn bộ câu trả lời cùng một lúc. Người dùng tưởng web bị crash và bấm nút reload trang liên tục. | *"Chatbot phản hồi hơi lâu. Mình gõ xong chờ mãi không thấy gì, cứ tưởng trang web bị đơ hay crash rồi nên lại bấm reload lại trang."* | **Trung bình** <br> (UX) |
| **Lê Hoàng Nam** <br> *(Học viên K4 - Zone B)* | Thực hiện ôn tập bài Day 01 $\rightarrow$ Chuyển sang bài giảng Day 02 và hỏi chatbot tiếp. | Khi học viên chuyển sang bài Day 02, chatbot vẫn giữ nguyên lịch sử trò chuyện của Day 01. AI trả lời bị lẫn lộn kiến thức của ngày học trước vào ngày học sau. | *"Ủa mình đang mở bài Day 02 mà chatbot vẫn trả lời dựa trên nội dung bài Day 01 nãy mình hỏi vậy? Hai bài khác nhau mà lịch sử chat bị lẫn lộn hết rồi."* | **Trung bình** <br> (UX/Logic) |
| **Phạm Minh Đức** <br> *(Học viên K4 - Zone C)* | Xem danh sách slide gợi ý và click mở các slide để ôn tập. | Học viên click vào slide thứ nhất, chuyển đúng nội dung. Học viên hiểu vì sao slide được chọn nhưng muốn ghi rõ lý do. | *"Gợi ý slide khá chuẩn, mình click vào là ra đúng trang slide nói về LLM Foundation. Nhưng có thể hiển thị rõ hơn lý do vì sao gợi ý slide này không? Ví dụ như ghi là 'Bạn trả lời sai câu hỏi số 3'."* | **Thấp** <br> (Góp ý) |
| **Vũ Hoàng Yến** <br> *(Học viên K4 - Zone A)* | Đọc danh sách slide gợi ý ôn tập cho concept `problem-discovery` sau quiz. | Khi học viên làm sai câu hỏi thuộc concept rộng này, hệ thống gợi ý tới 7 slide, khiến người dùng cảm thấy bị ngợp và lười đọc. | *"Ôi sai một concept mà gợi ý tận 7 slide thế này thì nhiều quá, mình lật mỏi tay luôn. Nhóm có cách nào cô đọng lại những slide chính nhất được không?"* | **Trung bình** <br> (UX) |

---

## 2. Tổng hợp Kết quả & Hành động Khắc phục (Changelog Alignment)

Dựa trên phản hồi từ người dùng thực tế, nhóm đã thực hiện phân tích và triển khai các thay đổi quan trọng trước buổi demo nghiệm thu:

### 1. Chủ đề lặp lại nhiều nhất (Top Issue)
- **Vấn đề phản hồi chậm và đơ màn hình:** Người dùng cảm thấy khó chịu khi phải đợi 4-5 giây cho câu trả lời của Chatbot xuất hiện cùng một lúc.
- **Trùng lặp lịch sử chat:** Lịch sử trò chuyện bị lẫn lộn giữa các ngày học khác nhau.

### 2. Các thay đổi đã thực hiện trước Demo (Đã đồng bộ vào Changelog)
Nhóm đã triển khai sửa đổi trực tiếp vào codebase trong ngày 31/07/2026:
- **[Sửa lỗi định danh Day 02]:** Cấu trúc lại API `/concepts/{lecture_id}` và sửa đổi script `seed_questions.py` để tự động quét các bài học và thực hiện mapping `day02` $\rightarrow$ `d2-xac-dinh-bai-toan`. (Khắc phục lỗi màn hình trống của **Trần Văn An**).
- **[Nâng cấp luồng Streaming & Reasoning]:** Di chuyển luồng sinh câu trả lời sang kiến trúc Streaming (FastAPI `StreamingResponse` + SSE) cho chữ chạy từng từ cực mượt, đồng thời hiển thị luồng suy luận nội tâm (`reasoning_content`) để người dùng không cảm thấy màn hình bị treo. (Khắc phục lỗi đơ màn hình của **Nguyễn Thị Lan**).
- **[Tách biệt Session hội thoại]:** Sử dụng Composite Thread ID dạng `user_id + lecture_id` trong LangGraph để tự động làm sạch (refresh) bộ nhớ chat khi chuyển bài học mới. (Khắc phục lỗi lẫn lộn lịch sử của **Lê Hoàng Nam**).
- **[Giới hạn số slide gợi ý]:** Giới hạn thuật toán gợi ý tối đa từ 3-5 slide ưu tiên ở API `/review-path` tránh gây ngợp cho người học. (Khắc phục lỗi gợi ý quá dài của **Vũ Hoàng Yến**).

### 3. Các quyết định giữ nguyên có lý do căn cứ
- **Cơ chế ELO/Mastery cập nhật sau từng câu:** Một số người dùng muốn điểm mastery cập nhật ngay sau khi làm xong cả bộ quiz thay vì cập nhật từng câu. Nhóm quyết định **giữ nguyên cập nhật từng câu** vì việc tính toán ELO thời gian thực giúp hệ thống thích ứng ngay lập tức để chọn câu hỏi tiếp theo ở độ khó phù hợp nếu học viên làm quiz nhiều lượt, đồng thời giảm thiểu rủi ro mất dữ liệu giữa chừng.

### 4. Đưa vào Backlog phát triển tiếp (Roadmap)
- **Hiển thị lý do gợi ý chi tiết (Góp ý của Phạm Minh Đức):** Bổ sung tooltip hoặc dòng chú thích dưới mỗi slide gợi ý để học viên biết slide này được đề xuất do sai câu hỏi cụ thể nào trong bài quiz.
- **Tích hợp tính năng bookmark/đánh dấu:** Cho phép học viên lưu lại những slide quan trọng hoặc đánh dấu "Gợi ý này không chính xác" để cải thiện thuật toán RAG.
