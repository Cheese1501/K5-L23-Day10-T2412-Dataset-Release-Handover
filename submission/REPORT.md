# Báo cáo Day 10 — Nhóm T2412

## Kết quả tích hợp mới nhất trên dev

Đã nhận đủ 6 kết luận `confirmed` từ các thành viên qua TV4 và bản ghi cuối của TV6, cùng kết quả ảnh lệch hash `intact` của TV5. `errors.json` hiện có 16 lỗi, tương ứng 16/250 = 6,4%, v1 HOLD.

Tự đo sau khi gộp đủ review cho F1 tổng ≈ 0,8, lỗi luật ≈ 1,0, lỗi gán nhãn ≈ 0,6. Truy vết tier_a, tier_b, notify đều ≈ 1,0. Báo cáo gốc ở `r2412007/report.md`. Các lần đo ở bảng baseline bên dưới là lịch sử trước khi gộp review.

V2 hiện có 242 ảnh, 1.656 nhãn và 8 ảnh rework, đã được đóng gói và xuất sang `submission/r2412007/handover/`. Ngày 20/11/2026, TV1 xác nhận đã xem ảnh 000000004395 và còn thấy rõ mặt người. Đã hoàn tất security.md, dựng lại và xuất gói cuối. Bộ kiểm gốc trả 17 PASS, 0 FAIL; log ở `r2412007/check_handover.txt`. H14 có event v2 với parent; README v2 ghi Release theo xử lý lỗi detection, v1 vẫn HOLD. Tình huống bảo mật có yêu cầu làm mờ vẫn trả lời HOLD và báo người phụ trách. [Việc còn lại](CON_LAI.md)

## 1. Số liệu baseline luyện tập trước khi gộp review

| Lô | Số lỗi luật | F1 lỗi luật | F1 tổng nếu chỉ báo lỗi luật | Ứng viên |
|---|---:|---:|---:|---:|
| T2412 · seed 2412007 · 250 ảnh | 10 | ≈ 1.0 | ≈ 0.7 | 6 ca trên 6 ảnh |
| Seed 11 · 250 ảnh | 13 | ≈ 1.0 | ≈ 0.8 | 3 ca trên 3 ảnh |
| Seed 22 · 250 ảnh | 9 | ≈ 1.0 | ≈ 0.7 | Chưa chạy chế độ ứng viên |
| Lô sạch · 50 ảnh | 0 | | | 0 |

Seed 2412007 lấy theo ví dụ `2412 × 1000 + 7` trong GUIDE.md. Điểm lấy từ script tự đo ở chế độ học viên. F1 lỗi gán nhãn còn chờ nhóm xem và xác nhận.

Checkpoint sau review TV1 trước đó có 11 lỗi, gồm 10 lỗi luật và 1 `class_swap`. Bản mới nhất sau khi nhận đủ review có 16 lỗi, như phần kết quả tích hợp ở đầu báo cáo.

Validator ghép lớp theo tên và dùng IoU, phần trăm pixel segment nằm trong box, cùng lớp và kích thước vật. Hai nguồn khác lớp được ưu tiên review khi IoU từ 0,56, phủ mask từ 78% và không có cặp cạnh tranh gần bằng. Segment thiếu box phải có ít nhất 170 pixel, với hai chiều bbox từ 10 px. Các ngưỡng giữ số ca ở mức nhóm có thể mở từng ảnh. Kiểm thử lô sạch cho thấy 0 ca lệch tự nhiên được đưa vào hàng đợi trên 50 ảnh. Cần đo lại nếu nhóm điều chỉnh ngưỡng.

## 2. Vì sao báo hết ứng viên có thể làm F1 giảm?

Ứng viên sai làm tăng FP, kéo precision và F1 xuống. Nếu chọn cả hai loại lỗi cho một bất đồng lớp, sẽ có ít nhất một báo cáo sai dù ảnh thật sự có lỗi. Bản review cuối có 6 confirmed và 0 rejected, lô sạch tạo 0 ứng viên với ngưỡng hiện tại. F1 gán nhãn đo được ≈ 0,6 cho thấy độ khớp của kết luận người xem còn có giới hạn, nên các lần thay đổi nhãn tiếp theo cần dựa trên quan sát ảnh cụ thể.

## 3. Quyết định và lineage

Lô `lab250_ebedbc794d29` hiện có 16/250 target lỗi, tương ứng 6,4%, nên v1 tiếp tục **HOLD**. Truy vấn impact trả về `R-021: affected=True action=review_or_retrain`. Model của R-021 đã học từ v1, nên nhóm cần xem lại ảnh hưởng khi đánh giá hoặc train lại trên lô đã xử lý. V2 dựng từ review đầy đủ có 242 ảnh, 1.656 nhãn và 8 ảnh rework. Ảnh lệch hash đã được TV5 mở và xác nhận intact, nên giữ trong v2 với hash thật.

## 4. Vai trò của hash

So SHA-256 với manifest cho biết byte của file có khớp phiên bản được bàn giao. Một nhãn sai vẫn có thể có SHA-256 khớp. Tạo v2 riêng giúp giữ bằng chứng QC và truy về dữ liệu R-021 đã dùng.

## 5. Truy vết

Lấy lớp đổi quy tắc từ changelog và cảnh được báo từ ticket. Giữ các ảnh có box lớp đó thuộc job dùng guideline cũ. `tier_a` nằm trong cảnh được báo, `tier_b` là những ảnh còn lại thỏa điều kiện. `notify` là tập mã người gán và người kiểm từ các job có ảnh ở hai tầng. Dùng guideline ghi theo job vì metadata ảnh có thể bị lệch.

Seed 2412007 có 4 ảnh tầng A, 3 ảnh tầng B và 2 người trong danh sách báo. F1 làm tròn của cả ba mục đều ≈ 1.0.

## 6. Việc còn mở

Bộ kiểm mới nhất trên lô tích hợp trả 17 PASS, 0 FAIL sau xác nhận ảnh khuôn mặt của TV1. Đã đóng gói và xuất bài, v1 vẫn giữ nguyên. PASS xác nhận các yêu cầu mà bộ kiểm kiểm tra, không bảo đảm mọi kết luận nhãn đều đúng. Đã có đủ GitHub: TV1 xác nhận TV6 longnguyen3204 và TV7 Cheese1501. Còn rà commit cá nhân và hoàn tất thủ tục nộp. TV1 xác nhận thời gian đề ẩn là 20 phút; dev dùng hoàn thiện/kiểm thử, khi nộp chính thức mới hoàn thiện main. Chưa có giờ bắt đầu/kết thúc thực tế, hạn hoặc kênh nộp. TV1 đã cung cấp link Drive; chọn ngẫu nhiên đề 07 từ 20 đề trước khi xem nội dung. Validator hiện có tìm 8 lỗi luật, 7 ứng viên. Trace có 2 ảnh tầng A, 9 tầng B và 4 mã người; hai công cụ của nhóm cho cùng kết quả. TV1 đã xem đủ 7 ca nhãn (6 confirmed, 1 rejected) và ca hash intact. Ca img_0197 được cập nhật thành missing_box sau khi TV1 xác nhận chỉ có khung xanh panoptic quanh con chó. Đã xuất `submission/de_an/` với 14 lỗi (8 luật + 6 semantic); ca bbox_drift img_0247 bị rejected được giữ trong log và không đưa vào errors. Chưa có F1 đề ẩn. Bằng chứng kiểm nhất quán ở `de_an/review_validation.json`. Hướng dẫn chi tiết được lưu trong CON_LAI.md.

## 7. Tích hợp hai module TV2

TV1 đã cherry-pick commit `b5b5c8d` của TV2 thành `bceccca` trên nhánh `tv1/complete-lab`. Hai file `rules_detection.py`, `rules_panoptic.py` giữ nguyên nội dung và tác giả từ bản bàn giao. `validate.py` gọi `find_duplicate_boxes` và `find_thing_overlaps`, đồng thời bỏ phần kiểm tương ứng trong bản TV1 cũ.

| Lô kiểm sau tích hợp | Lỗi luật | Ứng viên | So với baseline |
|---|---:|---:|---|
| Seed 2412007 | 10 | 6 | Cùng toàn bộ cặp lỗi và danh sách ứng viên |
| Seed 22 | 9 | 6 | Cùng toàn bộ cặp lỗi luật, lần này chạy thêm ứng viên |
| Lô sạch 50 ảnh | 0 | 0 | Cùng kết quả |

21 kiểm thử đã đạt, gồm 4 ca mới kiểm lời gọi module, trùng box, chênh area mask, crowd và stuff. Các ca mới dùng dữ liệu tổng hợp. Kết quả chạy lô được ghi trong `runs/tv1_checks/integrated_*.json`. Review của thành viên giữ nguyên. Điểm F1 ở mục 1 thuộc lần đo baseline trước đó, lượt tích hợp này đối chiếu đầu ra đầy đủ để kiểm hồi quy.

## 8. Tích hợp đóng góp TV3

Đã nhận commit `0139ad5` của Hoàng Quang Trường (GitHub truonghoangg25). Bản mới kiểm tra cấu trúc delivery, xử lý dòng nhãn không phải số, thiếu tọa độ và giá trị không hữu hạn; tránh validator dừng vì lỗi chuyển kiểu. Hai module TV2 không đổi. Module `validator/crosscheck.py` là công cụ độc lập bổ sung của TV3; CLI chính giữ nguyên cách sinh ứng viên đang dùng.

20 kiểm thử mới của TV3 và 30 kiểm thử hiện có đều đạt. Trước tích hợp đã chạy CLI của TV3 trong thư mục tạm: lô nhóm 10 lỗi luật/6 ứng viên, lô sạch 0/0, đề 07 8/7; toàn bộ JSON khớp bản trước. Giữ nguyên errors, review và trace đã chốt của đề 07. Không đọc đáp án hay chạy lại F1 để điều chỉnh kết luận.
