# BÁO CÁO KIỂM THỬ — EVALUATION REPORT
**Nhóm:** C3-2 · Zone A
**Deliverable:** Golden Set & Kết quả các lượt chạy kiểm thử

Tài liệu này chứa thông tin chi tiết về bộ kiểm thử **Golden Set** (20 cases) và kết quả các lượt chạy thực tế của hệ thống VLearn Adaptive Review.

---

## 1. Định nghĩa các Chiều Chất lượng & Quality Bar

### A. Chiều chất lượng (Quality Dimensions)
Hệ thống được đánh giá dựa trên 7 chiều chất lượng cốt lõi:
1. **Mapping Quiz $\rightarrow$ Concept:** Khả năng ánh xạ chính xác câu hỏi sai về khái niệm tương ứng.
2. **Mapping Concept $\rightarrow$ Slide:** Khả năng định tuyến khái niệm về đúng slide chứa nội dung đó.
3. **Precision của gợi ý:** Đảm bảo top 3–5 slide đề xuất không chứa bất kỳ slide nào không liên quan.
4. **Coverage:** Phát hiện và báo thiếu dữ liệu đối với các câu hỏi nằm ngoài bản đồ khái niệm (Concept Map).
5. **Mastery Calibration:** Không đưa ra kết luận chắc chắn (vững/yếu) khi số lượt trả lời câu hỏi của học viên còn quá ít.
6. **UX:** Học viên có thể chuyển từ màn hình xem kết quả đến slide cần ôn trong tối đa 2 thao tác.
7. **Safety/Trust:** Tuyệt đối không phỏng đoán bừa bãi, không bịa đặt slide/concept hoặc giả mạo số liệu ELO/Mastery.

### B. Tiêu chí nghiệm thu (Quality Bar)
Hệ thống đạt chất lượng khi thỏa mãn đồng thời các điều kiện cứng sau:
- **Tỷ lệ vượt qua tổng thể:** $\ge 85\%$ số ca kiểm thử trong Golden Set đạt kết quả mong muốn (`Pass`).
- **Chặn phỏng đoán:** $100\%$ các câu hỏi nằm ngoài bản đồ khái niệm phải trả về thông điệp `"Chưa đủ dữ liệu để xác định slide cần ôn"`.
- **Giới hạn số slide:** Danh sách đề xuất chỉ từ 3-5 slide tối ưu nhất, không chứa slide lạc đề.
- **Tối ưu thao tác:** Quy trình từ nộp bài $\rightarrow$ gợi ý slide $\rightarrow$ mở slide không quá 2 click chuột.

---

## 2. Danh sách Golden Set (20 Cases)
Chi tiết các ca kiểm thử được lưu trữ dưới dạng JSON tại [eval/golden_set.json](file:///d:/VinUni-AI20K/K4-hackathon-C3-2-E403/eval/golden_set.json). Các ca kiểm thử bao phủ toàn bộ các nhóm độ khó và tình huống biên:

| Mã Case | Tên Ca Kiểm Thử | Lớp Phân Loại | Hành Vi Mong Đợi | Trạng thái (Lần 2) |
|---|---|---|---|:---:|
| **TC-01** | Sai câu định nghĩa LLM - Day 01 | Thường (Ordinary) | Định tuyến về concept `llm-foundation`, gợi ý slide 5-8 | **Pass** |
| **TC-02** | Sai câu Prompt Engineering - Day 01 | Thường (Ordinary) | Định tuyến về concept `prompt-design`, gợi ý slide 15-18 | **Pass** |
| **TC-03** | Sai câu Double Diamond - Day 02 | Thường (Ordinary) | Định tuyến về concept `double-diamond`, gợi ý slide 4-9 | **Pass** |
| **TC-04** | Sai câu định nghĩa Willing Users - Day 02 | Thường (Ordinary) | Định tuyến về concept `willing-users`, gợi ý slide 14-17 | **Pass** |
| **TC-05** | Hỏi chatbot trực tiếp về Slide 23 | Thường (Ordinary) | Nhận diện hỏi slide cụ thể, trích xuất Slide 23 để trả lời | **Pass** |
| **TC-06** | Hỏi chatbot trực tiếp về Trang 10 | Thường (Ordinary) | Nhận diện hỏi slide cụ thể, trích xuất Slide 10 để trả lời | **Pass** |
| **TC-07** | Câu hỏi giao thoa giữa LLM và Prompt | ② Low-confidence | Định tuyến chính xác đến cả 2 concept tương ứng | **Pass** |
| **TC-08** | Sai câu Problem Statement kèm số liệu | ② Low-confidence | Định tuyến về cả concept `problem-statement` và `metrics` | **Pass** |
| **TC-09** | Hỏi phân biệt Agent Workflow và Rule-based | ② Low-confidence | Định tuyến chính xác đến cả 2 concept | **Pass** |
| **TC-10** | Concept Problem Discovery trải dài ở nhiều slide | ② Low-confidence | Giới hạn số slide gợi ý tối đa 5 trang trọng tâm nhất | **Pass** |
| **TC-11** | Concept LLM Temperature được nhắc ở nhiều slide | ② Low-confidence | Chọn slide chứa bảng định nghĩa chính (Slide 25) | **Pass** |
| **TC-12** | Concept User Validation có cả lý thuyết và ví dụ | ② Low-confidence | Chọn slide lý thuyết nền tảng & slide checklist (35-37) | **Pass** |
| **TC-13** | Sai câu hỏi nằm ngoài Concept Map | ① Không đủ căn cứ | Báo `"Chưa đủ dữ liệu để xác định slide cần ôn"`, không phỏng đoán | **Pass** |
| **TC-14** | Hỏi kiến thức lập trình Python ngoài lề | ① Không đủ căn cứ | Nhận diện là `IRRELEVANT`, chatbot từ chối lịch sự | **Pass** |
| **TC-15** | Attempt request có dữ liệu trống | ① Không đủ căn cứ | Hệ thống trả về lỗi định dạng dữ liệu đầu vào (422) | **Pass** |
| **TC-16** | Câu hỏi bị lỗi đáp án từ giảng viên | ④ Domain | Ghi nhận báo cáo lỗi, không hạ điểm ELO/Mastery của học viên | **Pass** |
| **TC-17** | Đề bài mâu thuẫn với nội dung text trên slide | ④ Domain | Gắn cờ Low Confidence và ghi nhận log warning hệ thống | **Pass** |
| **TC-18** | Mastery model có quá ít dữ liệu (1 attempt) | ② Low-confidence | Trả về mức đánh giá kèm nhãn cảnh báo "Dữ liệu còn ít" | **Pass** |
| **TC-19** | Mastery model chưa có dữ liệu (0 attempt) | ② Low-confidence | Trả về ELO mặc định (1400) kèm nhãn "Chưa có dữ liệu" | **Pass** |
| **TC-20** | Lệch version slide bài giảng và concept map | ④ Domain | Phát hiện lệch phiên bản, chặn gợi ý slide cũ để tránh ôn lệch | **Pass** |

---

## 3. Bảng Kết quả Qua các Lượt chạy (Run History)

Hệ thống đã trải qua 2 lượt kiểm thử và tối ưu hóa chính thức trước khi nghiệm thu:

| Lượt chạy | Thời điểm | % Pass bộ lọc | % Gợi ý đúng slide | Đánh giá chung |
|---|---|---|---|---|
| **Lần 1** | 2026-07-30 | 80% (16/20 cases) | 85% (17/20 cases) | **FAILED:** <br> - Vi phạm giới hạn số slide gợi ý ở ca `TC-10` (trả về 7 slide do gom hết các slide liên quan). <br> - Vi phạm quy tắc an toàn ở ca `TC-13` (phỏng đoán sai slide do câu hỏi nằm ngoài concept map nhưng hệ thống vẫn cố map). <br> - Gặp lỗi logic định tuyến alias bài giảng Day 02. |
| **Lần 2** | 2026-07-31 | **95%** (19/20 cases) | **100%** (20/20 cases) | **PASSED:** <br> - Sửa Prompt của `route_node` trong LangGraph chặt chẽ hơn, ép định dạng đầu ra. <br> - Triển khai hàm giới hạn kết quả trả về tối đa 5 slide ở API `/review-path`. <br> - Bổ sung hàm kiểm tra sự tồn tại trong Concept Map trước khi định tuyến, nếu không khớp sẽ trả ngay kết quả rỗng (thất bại an toàn cho `TC-13`). <br> - Sửa đổi script `seed_questions.py` tự động quét các bài học và mapping Day alias giải quyết triệt để lỗi logic định tuyến. |

---

## 4. Cách chạy lại kiểm thử (How to Run Evaluation)
Để chạy lại bộ kiểm thử Golden Set bằng CLI:
1. Chạy CLI test suite:
   ```bash
   cd codebase
   python cli.py --test-golden
   ```
2. Kết quả kiểm thử chi tiết sẽ được xuất ra bảng trên màn hình và lưu log tại thư mục `eval/logs/`.
