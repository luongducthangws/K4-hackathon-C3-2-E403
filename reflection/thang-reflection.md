# NHẬT KÝ PHẢN TƯ CÁ NHÂN (REFLECTION LOG)
**Học viên:** Lương Đức Thắng
**Vai trò trong dự án:** Concept Map & Validation (VLearn Adaptive Review)

---

## 1. Vai trò & Phần việc đảm nhận (Role & Contributions)
Trong dự án này, tôi chịu trách nhiệm hai mảng: **xây dựng Concept Map** làm nền tảng cho toàn bộ luồng gợi ý, và **tổ chức vòng Validation với người dùng thật**:

- **Thiết kế Concept Map cho 2 bài giảng:** Từ `slides.json` (văn bản trích xuất từng slide), gom cụm nội dung thành **14 concept** cho Day 01 (`d1-ai-llm-foundation`) và **15 concept** cho Day 02 (`d2-xac-dinh-bai-toan`), mỗi concept gắn `slide_start`/`slide_end` và `prereq_id` để thể hiện thứ tự phụ thuộc kiến thức (ví dụ Attention phải sau Context window, Context window phải sau Tokenization).
- **Ràng buộc & validate concept map bằng script:** Viết `codebase/scripts/build_concept_map.py` để kiểm tra máy móc thay vì tin bằng mắt: mọi cụm phải có `slide_start <= slide_end` và nằm trong số slide thật của bài; không được overlap giữa hai concept trong cùng một lecture; mọi `prereq_id` phải trỏ về một `concept_id` đã tồn tại. Script ghi ra `concepts.json`, `slide_concept.json` cho từng bài và gộp thành `seed.sql` để seed DB một lần.
- **Vòng Validation với 5 người dùng ngoài nhóm:** Tuyển 2 Willing User (đã đăng ký từ CP1) và 3 bạn ở zone khác, mỗi phiên ~10 phút với 3 câu hỏi cố định (danh sách có đúng phần chưa vững không / có hiểu vì sao slide được gợi ý không / có mở slide và tiếp tục ôn không). Ghi log quan sát + quote nguyên văn vào `validation/README.md`, phân loại mức nghiêm trọng (Cao/Trung bình/Thấp) và đối chiếu từng phát hiện với thay đổi thực tế đã đưa vào changelog trước demo.

---

## 2. AI đã hỗ trợ như thế nào? (AI Assistance)
- **Content factory cho concept map:** Vì cụm nội dung theo mạch bài giảng là việc cần đọc hiểu ngữ nghĩa (không thể suy ra bằng rule cứng), tôi để Claude đọc toàn bộ `slides.json` của cả 2 bài và đề xuất cách gom cụm slide theo mạch nội dung thật — tôi đóng vai trò duyệt và chỉnh lại ranh giới cụm, còn script `build_concept_map.py` chỉ làm việc validate + lắp ráp, không tự suy luận cluster. Cách chia vai này giúp tránh vừa để AI tự "bịa" cấu trúc kiến thức vừa để AI tự chấm đúng/sai cho chính nó.
- **Tổng hợp log validation:** AI hỗ trợ tôi cấu trúc lại ghi chú tay trong 5 phiên phỏng vấn thành bảng feedback log có phân loại mức độ nghiêm trọng, và đối chiếu chéo từng dòng phản hồi với đúng commit/thay đổi đã fix, để tránh liệt kê phản hồi rồi bỏ quên không truy vết được đã sửa hay chưa.
- **Rà soát phrasing câu hỏi phỏng vấn:** Nhờ AI phản biện bộ 3 câu hỏi validation ban đầu (dễ dẫn dắt người thử trả lời theo ý nhóm muốn nghe) để chỉnh lại thành câu hỏi trung tính hơn trước khi đưa vào phiên thử thật.

---

## 3. Bài học từ một Case Fail của chính nhóm (Lesson from a Team Failure Case)
**Sự cố gặp phải:**
Ở lượt chạy golden set lần 1 (2026-07-30), case `TC-10` (concept "Problem Discovery" trải dài nhiều slide) fail: hệ thống trả về **7 slide** thay vì tối đa 3–5 như quality bar yêu cầu. Cùng lúc, trong vòng validation, người thử Vũ Hoàng Yến phản ánh đúng vấn đề này bằng lời: *"Ôi sai một concept mà gợi ý tận 7 slide thế này thì nhiều quá, mình lật mỏi tay luôn."*

**Nguyên nhân:**
Gốc rễ nằm ở chính concept map tôi thiết kế: một số concept (như "Problem Discovery") được gom quá rộng, bao trùm nhiều slide có mức liên quan khác nhau. Vì hệ thống gợi ý dựa trực tiếp trên khoảng `slide_start`–`slide_end` của concept, concept càng rộng thì số slide trả về càng nhiều — lỗi không nằm ở tầng gợi ý mà nằm ở granularity của concept map từ đầu.

**Bài học rút ra:**
1. **Granularity của concept map quyết định chất lượng downstream:** Một concept map "đúng nội dung" vẫn có thể tạo ra trải nghiệm tệ nếu cụm quá thô. Từ lần này tôi rút ra nguyên tắc: mỗi concept nên giới hạn trong một số slide đủ hẹp để luôn chọn được top slide có chủ đích, thay vì để tầng API phải tự cắt bớt.
2. **Bằng chứng định lượng (eval) và bằng chứng định tính (validation) nên đối chiếu chéo:** Việc `TC-10` fail trong golden set và lời phàn nàn của Vũ Hoàng Yến trỏ về đúng một nguyên nhân giúp tôi tin chắc đây là lỗi hệ thống chứ không phải case đơn lẻ, nên ưu tiên sửa trước demo thay vì bỏ qua. Nhóm đã khắc phục bằng cách giới hạn cứng số slide trả về tối đa 3–5 ở API `/review-path`, nhưng việc gốc — chia nhỏ lại concept "Problem Discovery" — vẫn nên làm nếu có thêm thời gian, vì giới hạn ở API chỉ là chặn triệu chứng, chưa sửa concept map gốc.
