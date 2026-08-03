# NHẬT KÝ PHẢN TƯ CÁ NHÂN (REFLECTION LOG)
**Học viên:** Lương Trí Tuệ  
**Vai trò trong dự án:** Xây dựng Mastery Model và cơ chế đánh giá mức độ nắm vững kiến thức cho VLearn Adaptive Review

---

## 1. Vai trò & Phần việc đảm nhận (Role & Contributions)
Trong dự án này, tôi phụ trách phần **mastery model** — tức lớp logic ước lượng học viên đang yếu, đang học hay đã nắm vững một khái niệm nào đó dựa trên lịch sử làm quiz và tương tác ôn tập.

Các đầu việc chính của tôi gồm:
- **Thiết kế công thức cập nhật mastery:** xây dựng cơ chế cập nhật theo kiểu Elo để mỗi lần học viên trả lời đúng/sai, điểm mastery của người học và độ khó của item đều được điều chỉnh dần.
- **Chuẩn hóa trạng thái kiến thức:** chuyển từ điểm số liên tục sang các trạng thái dễ hiểu hơn như `weak`, `learning`, `mastered`, để giao diện và logic gợi ý không phải xử lý một con số khó diễn giải.
- **Xử lý dữ liệu ít và dữ liệu khởi tạo:** thiết kế cách khởi tạo điểm đầu vào từ khảo sát hoặc dữ liệu prior để hệ thống vẫn hoạt động khi người học mới có rất ít lượt làm quiz.
- **Phối hợp với phần đánh giá gợi ý:** đảm bảo mastery model không chỉ trả về một con số đẹp mà còn phục vụ trực tiếp cho việc chọn slide cần ôn và giải thích vì sao hệ thống ưu tiên nội dung đó.

Điểm tôi chú ý nhất là phần này không được “ảo tưởng chính xác”. Khi số lượt làm còn ít, mastery nên được xem như một tín hiệu định hướng, không phải một phán quyết tuyệt đối về năng lực của người học.

---

## 2. AI đã hỗ trợ như thế nào? (AI Assistance)
AI giúp tôi rất nhiều ở phần biến một ý tưởng thống kê thành code chạy được và dễ kiểm thử:
- **Tạo khung công thức và kiểm tra biên:** AI hỗ trợ phác thảo nhanh cách cập nhật Elo, cách đổi từ rating sang mastery percentage, và cách chia trạng thái theo ngưỡng.
- **Gỡ mơ hồ trong thiết kế dữ liệu ít:** khi cần xử lý trường hợp mới có một vài câu làm thử, AI gợi ý các quy tắc an toàn như chỉ tăng mức khẳng định khi đã có đủ lượt quan sát.
- **Hỗ trợ diễn giải cho UI và spec:** AI giúp tôi chuyển các khái niệm kỹ thuật như `expected`, `K factor`, `confidence` thành ngôn ngữ dễ đọc hơn để cả nhóm thống nhất cách trình bày trong sản phẩm.

Tuy nhiên, tôi nhận ra AI chỉ hữu ích khi mình đã có ranh giới rõ: cái gì là công thức, cái gì là quy ước hiển thị, và cái gì phải giữ ở mức thận trọng vì chưa có đủ dữ liệu.

---

## 3. Bài học từ một Case Fail của chính nhóm (Lesson from a Team Failure Case)
**Sự cố gặp phải:**
Ở một phiên thử nội bộ, hệ thống sớm gắn nhãn `weak` cho nhiều học viên dù họ trả lời đúng liên tiếp ở vài câu đầu. Nhìn từ giao diện thì điều này tạo cảm giác mô hình “đánh giá quá tay”, làm người dùng khó tin vào phần gợi ý tiếp theo.

**Nguyên nhân:**
1. **Dữ liệu quan sát còn quá ít:** một vài câu đúng chưa đủ để kết luận người học đã thật sự nắm chắc khái niệm, nhưng nếu hiển thị trạng thái quá tiêu cực thì người dùng cũng không thấy hợp lý.
2. **Thiếu lớp diễn giải confidence:** trước đó hệ thống chủ yếu trả về mastery percentage, nhưng chưa tách rõ giữa “điểm hiện tại” và “độ tin cậy của ước lượng”.
3. **Ngưỡng trạng thái chưa phản ánh hành vi thực tế:** nếu chỉ dựa vào một ngưỡng cứng, mastery có thể đổi trạng thái quá sớm hoặc quá muộn so với trải nghiệm học tập thật.

**Bài học rút ra:**
1. **Phải phân biệt mastery và confidence:** mastery là ước lượng mức nắm bài; confidence là mức tin cậy của ước lượng đó. Hai thứ này không nên bị nhập làm một.
2. **Cần ưu tiên an toàn khi ít dữ liệu:** nếu chưa đủ lượt làm, hệ thống nên nghiêng về thông báo thận trọng thay vì khẳng định mạnh.
3. **Người dùng cần hiểu vì sao hệ thống chấm như vậy:** khi hiển thị trạng thái `learning` hoặc `weak`, cần cho thấy nó đến từ lịch sử nào, không chỉ từ một con số cuối cùng.

---

## 4. Những điều tôi rút ra cho phần mastery model
- Một mô hình tốt không chỉ là công thức đúng, mà còn phải **đọc được** và **giải thích được** cho người học.
- Khi dữ liệu còn ít, ưu tiên lớn nhất là **tránh kết luận quá sớm**.
- Cần giữ thiết kế đủ đơn giản để demo chạy ổn, nhưng vẫn đủ chặt để có thể mở rộng sang nhiều quiz và nhiều bài học sau này.
- Các ngưỡng như `weak`, `learning`, `mastered` chỉ thực sự có ý nghĩa khi chúng gắn với hành vi người học và được kiểm tra lại bằng dữ liệu thật.

---

## 5. Cách tôi muốn cải thiện ở vòng sau
- Thêm cách đo confidence rõ hơn thay vì chỉ dựa vào một điểm mastery duy nhất.
- Kiểm tra xem điểm khởi tạo từ khảo sát có làm lệch trạng thái ban đầu hay không.
- Bổ sung thêm test cho các trường hợp ít lượt làm, trả lời xen kẽ đúng/sai, và học viên có tiến bộ nhanh.
- Làm cho giao diện giải thích dễ đọc hơn để học viên biết vì sao hệ thống đề xuất một concept là "cần ôn" hay "đã khá vững".
