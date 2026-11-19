# Báo cáo Day 10 — Nhóm T2412

## 1. Số liệu baseline luyện tập trước khi gộp review

| Lô | Số lỗi luật | F1 lỗi luật | F1 tổng nếu chỉ báo lỗi luật | Ứng viên |
|---|---:|---:|---:|---:|
| T2412 · seed 2412007 · 250 ảnh | 10 | ≈ 1.0 | ≈ 0.7 | 6 ca trên 6 ảnh |
| Seed 11 · 250 ảnh | 13 | ≈ 1.0 | ≈ 0.8 | 3 ca trên 3 ảnh |
| Seed 22 · 250 ảnh | 9 | ≈ 1.0 | ≈ 0.7 | Chưa chạy chế độ ứng viên |
| Lô sạch · 50 ảnh | 0 | | | 0 |

Seed 2412007 lấy theo ví dụ `2412 × 1000 + 7` trong GUIDE.md. Điểm lấy từ script tự đo ở chế độ học viên. F1 lỗi gán nhãn còn chờ nhóm xem và xác nhận.

Sau khi nhận review của TV1, `errors.json` hiện có 11 lỗi đã biết, gồm 10 lỗi luật và 1 `class_swap` do TV1 xác nhận. Còn 5 ca chờ người xem. Điểm F1 trong bảng là baseline chỉ báo lỗi luật. Lượt cập nhật này gộp bằng chứng người xem và chưa chạy lại công cụ chấm trên tập review còn thiếu.

Validator ghép lớp theo tên và dùng IoU, phần trăm pixel segment nằm trong box, cùng lớp và kích thước vật. Hai nguồn khác lớp được ưu tiên review khi IoU từ 0,56, phủ mask từ 78% và không có cặp cạnh tranh gần bằng. Segment thiếu box phải có ít nhất 170 pixel, với hai chiều bbox từ 10 px. Các ngưỡng giữ số ca ở mức nhóm có thể mở từng ảnh. Kiểm thử lô sạch cho thấy 0 ca lệch tự nhiên được đưa vào hàng đợi trên 50 ảnh. Cần đo lại nếu nhóm điều chỉnh ngưỡng.

## 2. Vì sao báo hết ứng viên có thể làm F1 giảm?

Ứng viên sai làm tăng FP, kéo precision và F1 xuống. Nếu chọn cả hai loại lỗi cho một bất đồng lớp, sẽ có ít nhất một báo cáo sai dù ảnh thật sự có lỗi. Sau review, bổ sung số ứng viên `confirmed` và `rejected` của seed 2412007 để minh hoạ.

## 3. Quyết định và lineage

Lô `lab250_ebedbc794d29` hiện có ít nhất 11/250 target lỗi, tương ứng 4,4%, nên v1 tiếp tục **HOLD**. Truy vấn impact trả về `R-021: affected=True action=review_or_retrain`. Model của R-021 đã học từ v1. Nhóm cần xem lại ảnh hưởng khi đánh giá model hoặc train lại trên lô đã xử lý. Bản nháp trước review giữ 244 ảnh với 1.682 box, tạm đưa 6 ảnh vào hàng đợi xử lý. Các con số v2 cần tính lại sau review đầy đủ. Một ảnh cần nhóm kiểm tra nội dung vì hash lệch.

## 4. Vai trò của hash

So SHA-256 với manifest cho biết byte của file có khớp phiên bản được bàn giao. Một nhãn sai vẫn có thể có SHA-256 khớp. Tạo v2 riêng giúp giữ bằng chứng QC và truy về dữ liệu R-021 đã dùng.

## 5. Truy vết

Lấy lớp đổi quy tắc từ changelog và cảnh được báo từ ticket. Giữ các ảnh có box lớp đó thuộc job dùng guideline cũ. `tier_a` nằm trong cảnh được báo, `tier_b` là những ảnh còn lại thỏa điều kiện. `notify` là tập mã người gán và người kiểm từ các job có ảnh ở hai tầng. Dùng guideline ghi theo job vì metadata ảnh có thể bị lệch.

Seed 2412007 có 4 ảnh tầng A, 3 ảnh tầng B và 2 người trong danh sách báo. F1 làm tròn của cả ba mục đều ≈ 1.0.

## 6. Việc còn mở

Bộ kiểm gốc trên gói nháp T2412 trả 14 PASS, 3 FAIL. Khi TV1 kiểm lại đường dẫn chính thức `runs/r2412007`, bộ kiểm trả 2 PASS, 2 FAIL rồi dừng tại H4 vì thiếu thư mục v2 trong `handover/`. H2 ghi nhận đủ 11 lỗi hiện có. H3 chờ các dòng review còn lại. Sau khi dựng v2 chính thức, cần kiểm đủ các mục còn lại. Checkpoint output thật được lưu trong `submission/r2412007/`, còn nội dung bảo mật đang chờ ví dụ khuôn mặt do người xem xác nhận. TV1 cho biết đội hình 7 người đã được đồng ý. Còn chờ tài khoản GitHub, commit và kết quả xem ảnh từ các thành viên. Đề ẩn làm khi giảng viên phát.
