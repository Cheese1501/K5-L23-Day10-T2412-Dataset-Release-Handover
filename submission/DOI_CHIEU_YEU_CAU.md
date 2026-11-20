# Đối chiếu yêu cầu bài nộp — Nhóm T2412

Ngày kiểm: 20/11/2026. Người tổng hợp: Hoàng Kim Chi, TV7. Căn cứ: SUBMISSION.md, RULES.md, GUIDE.md, CHECKPOINTS.md và RUBRIC.md trong repo.

## 1. Cấu trúc và nội dung bắt buộc

| Yêu cầu | Bằng chứng trong repo | Kết quả |
|---|---|---|
| README ghi nhóm | README.md ghi Nhóm T2412 | Đủ |
| TEAM có danh tính, phân công và seed | TEAM.md có 7 người, MSHV, GitHub, vai trò, seed 2412007 | Đủ nội dung; TV1 ghi nhận đội hình 7 người được chấp thuận |
| CLI validator đúng giao diện | validator/validate.py, --out và --candidates | Đã chạy được |
| Validator chỉ dùng thư viện chuẩn, dữ liệu delivery | validate.py và hai module rules; hàm kiểm đường dẫn Delivery.file | Đã rà mã nguồn; không dùng mạng hoặc đáp án riêng trong validator |
| Lô sạch không báo lỗi luật; biết số ứng viên | Lượt chạy lại seed 5, no-faults, 50 ảnh calib | 0 lỗi luật, 0 ứng viên |
| Luyện tập có errors/candidates/review/trace/security | r2412007/ | Đủ năm file |
| Lỗi gán nhãn có confirmed và ghi chú >=20 ký tự | r2412007/review_log.csv đối chiếu errors.json | 6 ca confirmed hợp lệ |
| V2 đủ bảy phần | images, labels, manifest, label_summary, truyvet, rework_queue, README | Đủ |
| Hash, thống kê, rework và người xử lý khớp | Manifest 484 file; 242 ảnh, 1.656 box, 8 ảnh rework | Đã đối chiếu |
| V1 giữ nguyên; nhãn v2 không sửa tay | Bộ kiểm H1/H7 trên bản sao kiểm chứng; v1 local không bị ghi đè | PASS |
| Lineage HOLD v1, release v2 có parent | lineage.jsonl | Đủ |
| Bộ kiểm gốc không FAIL | r2412007/check_handover.txt | 17 PASS, 0 FAIL |
| Security đủ ba tình huống và ví dụ ảnh | r2412007/security.md; ảnh 000000004395 do TV1 xác nhận | Đủ nội dung |
| REPORT có số liệu và giải thích bắt buộc | REPORT.md, sáu mục theo mẫu | Đủ |
| Nhật ký sử dụng công cụ theo RULES | prompts.md | Có prompt, hạn chế/sai sót và cách kiểm lại |
| Đề ẩn đủ bốn file | de_an/errors.json, candidates.json, review_log.csv, trace.json | Đủ; 14 lỗi, 6 confirmed/1 rejected |
| Ca rejected không đưa vào errors | de_an/review_log.csv, errors.json | Đã đối chiếu |
| Không đưa dữ liệu/ZIP bị cấm vào Git | git ls-files đối chiếu runs, data_source, delivery, *.zip | Không có file bị cấm ở các đường dẫn này |

Điểm F1 luyện tập lấy từ report.md đã bàn giao: tổng ≈0,8; luật ≈1,0; gán nhãn ≈0,6. F1 không được suy ra từ PASS của bộ kiểm. Chưa có F1 đề ẩn hoặc kết quả xếp hạng của giảng viên.

## 2. Phần TV7

| Yêu cầu | Bằng chứng | Kết quả |
|---|---|---|
| Bảo mật theo mẫu ba mục | r2412007/security.md | Đủ |
| Báo cáo nhóm với số thật | REPORT.md và file đầu ra được dẫn | Đủ |
| Báo cáo cá nhân và bàn giao | TV7_REPORT.md, TV7_STATUS.md | Đủ |
| Có xem ảnh trong Pha 2 | Dòng 000000023023 có tên TV7 trong log tổng hợp TV4 | Có bằng chứng xem chéo; giữ nguyên ghi chú gốc |
| Hai commit có nội dung, đúng tài khoản/email | af665fe và f230d3a, Cheese1501, hoangkimchi46@gmail.com | Đủ hai commit: kiểm gói và hoàn thiện hồ sơ |
| Chuẩn bị ba nội dung vấn đáp | TV7_VAN_DAP.md | Đã chuẩn bị; việc trả lời thực tế do học viên thực hiện |

Theo tiêu chí hồ sơ, phần nội dung TV7 đã được tập hợp đủ trên main. Ảnh khuôn mặt và review đề 07 được ghi đúng người xem là TV1, không đổi thành TV7.

## 3. Các điều kiện ngoài nội dung hồ sơ

- TV2 có bản gốc và cherry-pick của cùng một thay đổi; TV3 có một commit gốc. Hai thành viên cần tự có thêm đóng góp thực tế để đạt yêu cầu hai commit mỗi người. Hồ sơ của TV7 không thể thay thế lịch sử của họ.
- Tên repo hiện tại khác mẫu trong SUBMISSION.md. Chưa có bằng chứng lớp chấp thuận ngoại lệ tên repo; không ghi là đã đạt mục này.
- TV1 xác nhận thời lượng đề ẩn của lớp là 20 phút, nhưng hồ sơ chưa có giờ bắt đầu/kết thúc thực tế. Không tự điền giờ đã làm.
- Chưa có hạn/kênh nộp được xác nhận hoặc bằng chứng nộp LMS. Bài trên main là bộ file đã chuẩn bị, không đồng nghĩa đã nộp.
- Điểm nhãn đề ẩn, thứ hạng và vấn đáp do giảng viên đánh giá; không thay bằng kết quả kiểm định dạng.

Các mục trên không ngăn việc hoàn thiện file TV7. Nhóm đã có đủ đầu ra kỹ thuật để tiếp tục thủ tục nộp theo hướng dẫn lớp.
