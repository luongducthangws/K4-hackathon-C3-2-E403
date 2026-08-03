# AI SPEC — Adaptive Review sau quiz · Nhóm C3-2 · Zone A

Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở  
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## Canvas 7 dòng

1. **Chiến tuyến:** VLearn — Adaptive Review (ôn tập thích ứng sau quiz).
2. **Vai cụ thể:** Học viên vừa nộp quiz sau một bài giảng dài khoảng 50–70 slide.
3. **Vướng gì:** Học viên sai một số câu nhưng không biết mình chưa vững khái niệm nào, nên phải tự lật lại toàn bộ bài giảng để dò phần cần ôn; thao tác này tốn công, dễ bị bỏ dở và không ngăn được việc lặp lại lỗi cũ.
4. **Bằng chứng:** Khảo sát có 32 phản hồi ở câu chọn tính năng và 31 phản hồi hợp lệ ở các câu pain liên quan: **9/31 (29,0%)** cho biết không biết cách tự đánh giá mức tiến bộ hoặc xác định chính xác phần kiến thức còn yếu; **2/31 (6,5%)** chọn vấn đề dễ lặp lại lỗi sai cũ vì không được tổng hợp và cảnh báo; **9/32 (28,1%)** chọn tính năng “ghi nhớ tiến trình, tự động phát hiện điểm yếu và gợi ý chính xác phần cần ôn” là hữu ích nhất. Chưa có log chứng minh tỷ lệ sai lại cùng concept hoặc thời gian 15–20 phút; hai chỉ số này phải được đo ở vòng validation/log VLearn.
5. **Lát cắt một câu:** Một học viên vừa nộp quiz sau bài giảng · bấm xem kết quả · hệ thống ước lượng khái niệm chưa vững từ các câu sai · trả về đúng 3–5 slide cần ôn kèm mức nắm từng khái niệm.
6. **AI tự làm đến đâu:** AI tự gán câu sai vào khái niệm và chọn slide khi concept map đã bao phủ câu hỏi; nếu câu nằm ngoài map hoặc bằng chứng không đủ, hệ thống báo “chưa đủ dữ liệu” thay vì đoán.
7. **Phân công:** Mỗi người sở hữu một phần riêng: concept map; mapping quiz → concept; mastery model; UI; validation. Điền tên thật ở §8, không ghi “cả nhóm cùng làm”.

---

## §1. User & Job

### Job executor + workflow

- **Job executor:** học viên vừa hoàn thành một quiz sau bài giảng 50–70 slide.
- **Workflow hiện tại:** `Nộp quiz → xem câu đúng/sai → tự đoán phần kiến thức yếu → lật lại nhiều slide → chọn phần để ôn → làm lại quiz`.
- **Workflow đề xuất:** `Nộp quiz → xem kết quả → hệ thống nối câu sai với concept → ước lượng mastery → trả 3–5 slide nên ôn → học viên mở đúng slide`.

### Core JTBD

> Sau khi làm quiz, tôi muốn biết chính xác mình chưa vững khái niệm nào và nên xem lại phần nào của bài giảng, để không phải tự dò lại toàn bộ tài liệu.

### Problem statement

Sau khi nộp quiz, học viên chỉ nhìn thấy câu đúng và câu sai nhưng chưa được chỉ ra lỗi sai thuộc khái niệm nào hoặc nằm ở phần nào trong bài giảng. Vì vậy, người học phải tự dò lại nhiều slide, khó ưu tiên nội dung cần ôn và có thể tiếp tục sai ở cùng một điểm trong lần làm sau.

### Evidence

- Nguồn: `Mẫu không có tiêu đề (Câu trả lời).xlsx`, sheet `Câu trả lời biểu mẫu 1`.
- Khảo sát có 33 dòng phản hồi; từng câu có 31–32 phản hồi hợp lệ do có ô trống.

| Tín hiệu khảo sát | Số thật | Ý nghĩa |
|---|---:|---|
| Không biết cách tự đánh giá mức tiến bộ hoặc xác định chính xác phần kiến thức còn yếu | **9/31 = 29,0%** | Xác nhận pain “không biết mình yếu concept nào”. |
| Dễ lặp lại lỗi sai cũ vì không được tổng hợp và cảnh báo kịp thời | **2/31 = 6,5%** | Có tín hiệu trực tiếp về lỗi lặp lại, nhưng tỷ lệ còn thấp và cần kiểm chứng thêm bằng log. |
| Chọn tính năng ghi nhớ tiến trình, tự động phát hiện điểm yếu và gợi ý chính xác phần cần ôn | **9/32 = 28,1%** | Xác nhận nhu cầu đối với Adaptive Review. |
| Đọc xong nhanh quên và không chắc đã nắm bản chất | **6/31 = 19,4%** | Bổ trợ cho nhu cầu kiểm tra mức nắm kiến thức sau học. |
| Mất thời gian lục lại và đọc lại từ đầu thay vì được nhắc trực tiếp | **16/31 = 51,6%** | Xác nhận chi phí dò lại nội dung cũ. |

**Bằng chứng chưa có và không được ghi như fact:**

- Chưa có số liệu xác nhận người học mất **15–20 phút** mỗi lần dò slide.
- Chưa có tỷ lệ `X/Y` học viên sai lại đúng concept đã sai ở quiz trước.
- Chưa có quote kèm tên người nói vì biểu mẫu hiện tại không thu tên và không có câu trả lời tự do.

**Cách bổ sung bằng chứng ngay từ log VLearn:**

1. Lấy các quiz attempt có cùng `user_id` và cùng quiz/course.
2. Sắp xếp theo thời gian, ghép hai lần làm liên tiếp.
3. Map từng câu sai sang `concept_id`.
4. Đếm `X = số học viên sai lại ít nhất một concept đã sai ở lần trước`.
5. Đếm `Y = số học viên có ít nhất hai lần làm hợp lệ`.
6. Báo cáo `X/Y` và tỷ lệ; tách thêm theo bài học và số ngày giữa hai lần làm.

## §2. Impact & quyết định chọn

| Ứng viên | Bằng chứng | Giá trị | Khả thi | Quyết định |
|---|---:|---|---|---|
| Adaptive Review sau quiz | 9/31 không xác định được phần yếu; 9/32 ưu tiên phát hiện điểm yếu | Chỉ đúng concept và slide cần ôn ngay sau quiz | Cao nếu quiz đã có đáp án, slide và concept map | **CHỌN** |
| Tạo quiz tự động | 16/31 mất thời gian tự soạn quiz; 10/32 ưu tiên tính năng này | Giảm thời gian tạo câu hỏi | Trung bình; cần đánh giá chất lượng câu hỏi | Hoãn |
| Tra cứu/giải thích tài liệu | 13/32 ưu tiên | Hữu ích khi đang đọc tài liệu | Cao nhưng không bám “sau quiz” | Không chọn cho lát cắt này |

**Lý do chọn:** Adaptive Review tạo một luồng demo ngắn, rõ và kiểm chứng được: `nộp quiz → nhận 3–5 slide cần ôn`. Việc vẫn tồn tại khi bỏ AI vì học viên hiện phải tự suy ra concept và tự dò slide.

## §3. Giải pháp tương tự đã nghiên cứu

- **Quiz review truyền thống:** hiển thị câu đúng/sai và đáp án; đáng học ở tính minh bạch, nhưng chưa nối lỗi sai với concept và slide.
- **Adaptive learning/mastery dashboard:** đáng học ở cách biểu diễn mức nắm kiến thức; cần tránh tạo cảm giác điểm mastery là sự thật tuyệt đối khi dữ liệu còn ít.
- **Khác biệt của lát cắt:** tập trung vào hành động ngay sau quiz, chỉ trả 3–5 slide ưu tiên và luôn chỉ ra vì sao từng slide được chọn.

## §4. Thiết kế

### Lát cắt một câu

> **Một học viên vừa nộp quiz sau bài giảng, bấm xem kết quả; hệ thống ước lượng khái niệm chưa vững từ các câu sai và trả về đúng 3–5 slide cần ôn kèm mức nắm từng khái niệm.**

### Non-goals

1. Không sinh toàn bộ lộ trình học dài hạn cho cả khóa.
2. Không tự động thay đổi điểm quiz hoặc chấm lại đáp án.
3. Không tạo quiz mới trong lát cắt này.
4. Không suy luận tính cách, năng lực tổng quát hoặc xếp hạng học viên.
5. Không gợi ý slide khi câu hỏi chưa được concept map bao phủ.
6. Không dùng điểm mastery như chẩn đoán chắc chắn sau chỉ một câu hỏi.

### Mức prototype

- [ ] Sketch  [ ] Mock  [x] Working
- **Làm thật:** đọc kết quả quiz; mapping câu hỏi → concept; concept → slide; tính mastery đơn giản; hiển thị 3–5 slide; mở đúng slide.
- **Mock/giới hạn:** dữ liệu chỉ dùng một bài giảng và một quiz đã chuẩn hóa; concept map được tạo thủ công hoặc bán tự động rồi duyệt trước demo.

### Automation

- [x] augment  [ ] conditional  [ ] automate

AI hỗ trợ phân loại câu sai và xếp hạng slide, nhưng học viên là người quyết định mở và ôn nội dung nào. Hệ thống chỉ tự động gợi ý khi mapping có đủ căn cứ; ngoài map thì dừng an toàn.

### Nguyên tắc áp dụng

| Nguyên tắc | Áp dụng cụ thể |
|---|---|
| Nói rõ AI đang dựa vào đâu | Mỗi concept hiển thị các câu sai liên quan và slide được map. |
| Truyền đạt độ chắc chắn | Hiển thị mức `chưa đủ dữ liệu / cần ôn / tương đối vững`, không dùng phần trăm giả chính xác. |
| Cho người dùng kiểm soát | Học viên có thể bỏ qua gợi ý, mở slide khác hoặc đánh dấu “gợi ý không đúng”. |
| Thất bại an toàn | Câu ngoài concept map trả “chưa đủ dữ liệu”, không đoán slide. |
| Hỗ trợ sửa sai | Sau lần làm quiz tiếp theo, mastery được cập nhật theo lịch sử mới. |
| Giới hạn số lựa chọn | Chỉ trả 3–5 slide ưu tiên, không đẩy lại toàn bộ bài giảng. |

## §5. Kiểu lỗi — 4 lớp chỗ khó

| Lớp | Kịch bản | Hành vi mong đợi |
|---|---|---|
| ① Không đủ căn cứ | Câu sai chưa có `concept_id` | Báo chưa đủ dữ liệu; không gợi ý slide. |
| ① Không đủ căn cứ | Concept có nhưng chưa map slide | Hiển thị concept cần ôn, không bịa số slide. |
| ① Không đủ căn cứ | Quiz attempt thiếu dữ liệu câu trả lời | Báo lỗi dữ liệu và giữ màn hình kết quả gốc. |
| ② Low-confidence | Chỉ có một câu hỏi đại diện cho concept | Gắn nhãn “dữ liệu còn ít”, không kết luận chắc chắn. |
| ② Low-confidence | Một câu hỏi được map tới nhiều concept | Hiển thị concept chính/phụ hoặc yêu cầu reviewer sửa map. |
| ② Low-confidence | Nhiều slide cùng nói về một concept | Chọn tối đa 3–5 slide theo mức liên quan và prerequisite. |
| ③ Ngoài phạm vi | Học viên yêu cầu giải thích một câu không thuộc bài | Chuyển sang trợ lý học tập khác hoặc báo ngoài phạm vi. |
| ③ Ngoài phạm vi | Yêu cầu dự đoán điểm thi cuối kỳ | Từ chối suy luận vì dữ liệu không đủ và không thuộc lát cắt. |
| ④ Domain | Câu hỏi sai do đề/đáp án bị lỗi | Cho phép report câu hỏi; không hạ mastery cho đến khi review. |
| ④ Domain | Slide thay đổi nhưng concept map chưa cập nhật | Chặn gợi ý dựa trên version cũ và yêu cầu remap. |
| ④ Domain | Câu hỏi kiểm tra nhiều bước suy luận | Không quy toàn bộ lỗi cho một concept duy nhất nếu không đủ căn cứ. |
| ④ Domain | Học viên đoán đúng nhưng không hiểu | Không tăng mastery quá mạnh chỉ dựa trên một đáp án đúng. |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** học viên nộp quiz → mở kết quả → thấy 2 concept cần ôn → nhận 4 slide ưu tiên → bấm mở đúng slide.
- **Low-confidence:** concept chỉ có một câu hỏi hoặc mapping mơ hồ → hệ thống gắn nhãn “dữ liệu còn ít” và giảm mức khẳng định.
- **Failure/không căn cứ:** câu sai ngoài concept map → hiển thị “chưa đủ dữ liệu để xác định slide cần ôn”; vẫn giữ kết quả đúng/sai gốc.
- **Correction:** học viên bấm “gợi ý không đúng” hoặc giảng viên sửa mapping → hệ thống ghi feedback và cập nhật map/version sau khi review.
- **Ngoài phạm vi:** không dự đoán điểm thi, không xây lộ trình cả khóa, không trả lời kiến thức ngoài bài.
- **Case domain:** câu hỏi lỗi, nhiều concept, slide đổi version hoặc đáp án đúng do đoán phải được xử lý riêng.

## §7. Kiểm thử

### Chiều chất lượng

| Chiều | Định nghĩa pass |
|---|---|
| Mapping quiz → concept | Câu hỏi trong golden set được gán đúng concept theo nhãn giảng viên. |
| Mapping concept → slide | Slide đề xuất chứa nội dung trực tiếp hoặc prerequisite cần thiết cho concept. |
| Precision của gợi ý | Không đưa slide không liên quan vào top 3–5. |
| Coverage | Câu ngoài map được phát hiện và báo thiếu dữ liệu. |
| Mastery calibration | Không kết luận “vững/yếu” chắc chắn khi số câu quá ít. |
| UX | Từ màn hình kết quả tới slide cần ôn không quá 2 thao tác. |
| Safety/trust | Không có slide bịa, concept bịa hoặc số liệu mastery giả chính xác. |

### Golden set — tối thiểu 20 case

- 6 case mapping câu sai → một concept rõ ràng.
- 3 case một câu → nhiều concept.
- 3 case concept → nhiều slide.
- 3 case câu nằm ngoài concept map.
- 2 case câu/đáp án bị report lỗi.
- 2 case mastery có quá ít dữ liệu.
- 1 case cập nhật slide version làm map cũ không hợp lệ.

### Quality bar

> **Đạt khi ≥ 85% golden cases pass; 100% câu ngoài map phải trả “chưa đủ dữ liệu”; top 3–5 không chứa slide ngoài concept; và luồng demo hoàn thành từ nộp quiz đến mở slide trong tối đa 2 thao tác sau màn hình kết quả.**

### Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

| Lượt chạy | Thời điểm | % Pass bộ lọc | % Gợi ý đúng slide | Ghi chú |
|---|---|---|---|---|
| Lần 1 | 2026-07-30 | 80% | 85% | Bản nháp đầu tiên, còn lỗi logic định tuyến |
| Lần 2 | 2026-07-31 | 95% | 100% | Sửa prompt nới lỏng định tuyến và bổ sung kiến thức Day 02 |

### Metrics cần thu từ log

- `repeat_concept_error_rate = X/Y` giữa hai attempt liên tiếp.
- Thời gian từ mở kết quả đến mở slide đầu tiên.
- Tỷ lệ học viên mở ít nhất một slide được gợi ý.
- Tỷ lệ “gợi ý không đúng”.
- Tỷ lệ câu hỏi không có concept map.
- Tỷ lệ cải thiện ở concept sau khi ôn và làm lại quiz.

## §8. Phân công & kế hoạch

> Điền tên thật; mỗi hạng mục chỉ có một owner chính.

| Người | Sở hữu chính | Deliverable |
|---|---|---|
| **Lương Đức Thắng** | Concept map | Danh sách concept, prerequisite, map concept → slide và version. |
| **Nguyễn Hoàng Vũ** | Mapping quiz → concept | Schema, nhãn câu hỏi, rule/AI mapping và bộ test mapping. |
| **Lương Trí Tuệ** | Mastery model | Công thức cập nhật mastery, confidence và xử lý ít dữ liệu. |
| **Phùng Đình Đạt** | UI | Màn kết quả, thẻ concept, danh sách 3–5 slide, feedback. |
| **Lương Đức Thắng** | Validation | Log analysis, tuyển người thử, phỏng vấn và báo cáo metric. |

### Validation CP5

Ba câu hỏi:

1. “Danh sách này có chỉ đúng phần bạn chưa vững không?”
2. “Bạn có hiểu vì sao từng slide được gợi ý không?”
3. “Sau khi xem gợi ý, bạn có mở slide và tiếp tục ôn không?”


## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 2026-07-30 | Chuyển từ Agent Builder/document assistant sang VLearn Adaptive Review | Canvas mới chốt chiến tuyến VLearn và luồng sau quiz. |
| 2026-07-30 | Đổi user từ Creator sang học viên vừa nộp quiz | Đúng vai cụ thể và demo end-to-end. |
| 2026-07-30 | Thay lát cắt bằng quiz → concept → 3–5 slide | Đảm bảo một user, một việc, một quyết định AI, một kết quả. |
| 2026-07-30 | Loại các số 15–20 phút và tỷ lệ sai lặp chưa được đo | Tránh biến giả thuyết thành bằng chứng. |
| 2026-07-30 | Bổ sung kế hoạch tính X/Y từ quiz attempts | Tạo bằng chứng hành vi kiểm chứng được từ log VLearn. |
| 2026-07-31 | Di chuyển luồng sinh câu trả lời sang kiến trúc Streaming (FastAPI StreamingResponse + SSE) | Cho phép hiển thị chữ chạy từng từ cực mượt, cải thiện trải nghiệm phản hồi. |
| 2026-07-31 | Tích hợp hiển thị luồng suy luận nội tâm (reasoning_content) lên giao diện Web | Tránh cảm giác đơ/treo màn hình do các mô hình lý luận (Reasoning Model) mất nhiều thời gian phân tích tư duy. |
| 2026-07-31 | Thiết lập hệ thống tách biệt Session nhớ theo từng slide/bài giảng bằng composite Thread ID (`user_id + lecture_id`) | Đảm bảo khi học viên chuyển Day, bộ nhớ chat sẽ được làm sạch (refresh) cho bài học mới. |
| 2026-07-31 | Sửa đổi script `seed_questions.py` tự động quét các bài học, cấu trúc lại API `/concepts/{lecture_id}` mapping `day02` → `d2-xac-dinh-bai-toan` | Sửa lỗi thiếu hụt dữ liệu Concept và lỗi chọn Concept trống không ở bài giảng 2. |
