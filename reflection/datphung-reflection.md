# NHẬT KÝ PHẢN TƯ CÁ NHÂN (REFLECTION LOG)

**Học viên:** Phùng Đình Đạt  
**Vai trò trong dự án:** Deployment & Hỗ trợ tích hợp Backend API (VLearn Adaptive Review)

---

## 1. Vai trò & Phần việc đảm nhận (Role & Contributions)

Trong dự án này, tôi chịu trách nhiệm chính về việc **triển khai frontend và backend trên cùng một máy**, đồng thời hỗ trợ nhóm backend trong quá trình **đóng gói và tích hợp API** để hệ thống có thể chạy thống nhất trong buổi demo.

- **Triển khai frontend và backend:** Tôi thiết lập môi trường chạy cho cả frontend và backend trên cùng một máy, kiểm tra các lệnh khởi động, cổng dịch vụ và thứ tự chạy của từng thành phần. Mục tiêu là bảo đảm giao diện có thể gọi được backend và toàn bộ luồng chính của sản phẩm hoạt động trong cùng một môi trường.

- **Cấu hình kết nối frontend–backend:** Tôi hỗ trợ cấu hình địa chỉ API và cổng của backend để frontend không gọi nhầm địa chỉ hoặc sai cổng. Tôi cũng kiểm tra các vấn đề liên quan đến CORS và cách backend nhận request từ giao diện.

- **Hỗ trợ đóng gói API backend:** Tôi hỗ trợ nhóm backend chuẩn hóa các endpoint để frontend có thể sử dụng thống nhất. Công việc bao gồm kiểm tra dữ liệu đầu vào, cấu trúc JSON trả về và tên các trường dữ liệu mà frontend cần hiển thị.

- **Kiểm tra luồng tích hợp:** Tôi chạy thử các luồng từ giao diện đến API, chẳng hạn như chọn bài học, xem lộ trình ôn tập và nhận kết quả từ backend. Khi phát hiện lỗi, tôi phối hợp với các thành viên phụ trách backend và frontend để xác định lỗi nằm ở URL, request, response hay logic xử lý.

- **Hỗ trợ chuẩn bị demo:** Trước khi demo, tôi kiểm tra lại toàn bộ quy trình khởi động hệ thống, bảo đảm frontend và backend có thể chạy ổn định trên cùng một máy và giảm khả năng xảy ra lỗi do cấu hình môi trường.

---

## 2. AI đã hỗ trợ như thế nào? (AI Assistance)

Trong quá trình làm việc, tôi sử dụng các công cụ AI như Cursor và Claude để hỗ trợ việc đọc code, tìm lỗi cấu hình và kiểm tra cách đóng gói API:

- **Phân tích lỗi khi chạy hệ thống:** Khi frontend không gọi được backend, AI giúp tôi đọc log và phân tích các khả năng như sai cổng, sai URL API, backend chưa khởi động hoặc request bị chặn bởi CORS. Nhờ đó, tôi có thể khoanh vùng nguyên nhân nhanh hơn thay vì kiểm tra ngẫu nhiên.

- **Hỗ trợ kiểm tra cấu trúc API:** AI giúp rà soát các endpoint và so sánh dữ liệu frontend gửi lên với dữ liệu backend yêu cầu. Việc này giúp phát hiện một số khác biệt về tên trường, kiểu dữ liệu và cấu trúc JSON response.

- **Hỗ trợ cấu hình môi trường chạy:** AI gợi ý cách tổ chức các biến cấu hình như địa chỉ backend, cổng dịch vụ và môi trường development. Tuy nhiên, tôi vẫn phải tự kiểm tra và hiểu các thay đổi trước khi áp dụng vì cấu hình được đề xuất có thể không hoàn toàn phù hợp với cấu trúc dự án.

- **Giải thích code backend:** Khi hỗ trợ đóng gói API, AI giúp giải thích luồng xử lý request, cách FastAPI khai báo endpoint và cách trả response. Điều này giúp tôi hiểu rõ hơn phần backend mình đang hỗ trợ thay vì chỉ sao chép đoạn code có sẵn.

Qua quá trình này, tôi nhận ra AI có thể tăng tốc việc tìm lỗi và viết cấu hình, nhưng người sử dụng vẫn cần kiểm tra bằng cách chạy thử thực tế. Một cấu hình nhìn có vẻ đúng trong code chưa chắc đã hoạt động đúng khi frontend và backend chạy cùng nhau.

---

## 3. Bài học từ một Case Fail của chính nhóm (Lesson from a Team Failure Case)

**Sự cố gặp phải:**

Trong lần chạy thử trước buổi demo, frontend hiển thị giao diện bình thường nhưng khi người dùng thực hiện thao tác lấy lộ trình ôn tập thì request không nhận được dữ liệu từ backend. Trên giao diện, hệ thống hiển thị trạng thái loading trong thời gian dài hoặc báo lỗi không lấy được dữ liệu.

Backend vẫn chạy và có thể truy cập khi kiểm tra trực tiếp bằng địa chỉ local. Tuy nhiên, frontend lại không kết nối được với endpoint tương ứng.

**Nguyên nhân:**

Sau khi kiểm tra, nhóm xác định sự cố đến từ một số vấn đề cấu hình và tích hợp:

1. Frontend đang gọi tới một cổng khác với cổng mà backend thực tế đang sử dụng.
2. Một số endpoint chưa thống nhất hoàn toàn về đường dẫn và phương thức request giữa frontend và backend.
3. Cấu trúc dữ liệu frontend gửi lên chưa khớp với schema mà API backend yêu cầu.
4. Một số trường hợp lỗi từ backend chưa được trả về theo định dạng thống nhất, khiến frontend không hiển thị được thông báo phù hợp.

Nguyên nhân chính là nhóm tập trung nhiều vào việc hoàn thiện từng phần riêng lẻ nhưng chưa kiểm tra sớm toàn bộ luồng từ frontend đến backend trên cùng một môi trường chạy.

**Cách khắc phục:**

Tôi phối hợp với các thành viên kiểm tra lại từng bước của luồng tích hợp:

- Xác nhận backend đang chạy ở cổng nào.
- Cập nhật lại địa chỉ API mà frontend sử dụng.
- Đối chiếu endpoint, HTTP method và request body giữa hai phía.
- Thống nhất lại tên trường dữ liệu trong request và response.
- Kiểm tra response bằng công cụ gọi API trước khi kết nối lại với frontend.
- Chạy thử trực tiếp từ giao diện sau khi thay đổi cấu hình.
- Chuẩn bị lại thứ tự khởi động frontend và backend để thuận tiện cho buổi demo.

Sau khi điều chỉnh, frontend đã gọi được API và hiển thị dữ liệu theo đúng luồng mong muốn.

**Bài học rút ra:**

1. **Deployment không chỉ là khởi động được ứng dụng:** Một hệ thống được xem là triển khai thành công khi các thành phần có thể giao tiếp đúng với nhau và người dùng thực hiện được luồng chính.

2. **Cần thống nhất API contract sớm:** Frontend và backend phải thống nhất từ đầu về endpoint, method, request body, response và cách xử lý lỗi. Nếu không, lỗi tích hợp thường chỉ xuất hiện khi ghép các phần lại với nhau.

3. **Nên kiểm tra tích hợp trước khi hoàn thiện toàn bộ sản phẩm:** Việc chạy thử một luồng nhỏ từ frontend đến backend sớm sẽ giúp phát hiện lỗi cổng, URL, CORS hoặc schema trước khi đến giai đoạn demo.

4. **Cần hiểu cấu hình thay vì chỉ làm theo AI:** AI giúp đưa ra hướng xử lý nhanh, nhưng tôi vẫn phải kiểm tra bằng log và chạy thử thực tế để biết thay đổi đó có thật sự phù hợp với hệ thống hay không.

5. **Đóng gói API cần chú ý đến người sử dụng API:** API không chỉ cần chạy đúng về mặt backend mà còn phải có cấu trúc rõ ràng, ổn định và dễ tích hợp với frontend.

Qua dự án, tôi hiểu rõ hơn vai trò của deployment trong một sản phẩm AI. Deployment là bước kết nối các phần việc của cả nhóm thành một hệ thống có thể sử dụng và trình diễn được. Đồng thời, việc hỗ trợ đóng gói API giúp tôi hiểu hơn về mối liên hệ giữa giao diện người dùng, backend và dữ liệu được trao đổi giữa hai bên.
