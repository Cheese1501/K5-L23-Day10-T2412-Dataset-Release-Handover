# Tiến độ TV6 — Nguyễn Nhân Thành Long

Ghi nhận tích hợp trên dev, cập nhật ngày 20/11/2026. TV1 đã nhận đầu ra, hoàn tất bảo mật theo xác nhận trực tiếp về ảnh 000000004395, đóng gói lại và chạy bộ kiểm gốc đạt 17/17. Chi tiết hiện tại ở [TV1_STATUS.md](TV1_STATUS.md).

Cập nhật ngày 19/11/2026. MSHV `2A202603310`. Vai trò: truy vết ticket và đối chiếu người phụ trách.

## Kết quả review ảnh

Đã xem lại ảnh `000000025386` và xác nhận `class_swap`. Vật thể là ghế, nhưng detection gán lớp `keyboard`. Kết luận được ghi trong `submission/reviews/TV6.csv` để TV4 đối chiếu và gộp; bản tổng hợp hiện có trong `submission/reviews/review_log.csv`.

## Truy vết ticket

Bản bàn giao `submission/r2412007/trace.json` có 4 ảnh `tier_a`, 3 ảnh `tier_b`, và hai mã cần thông báo: `A05`, `Q02`. Theo ticket và guideline gắn với job, tầng A là ảnh trong các cảnh được báo (`scene_569`, `scene_839`) có nhãn thuộc lớp `cup`; tầng B là các ảnh còn lại thỏa điều kiện truy vết. Người cần thông báo được lấy từ các job liên quan đến các ảnh ở hai tầng. Không dùng metadata guideline của ảnh để thay thế guideline theo job.

Các danh sách ảnh và mã thông báo được lưu trong `trace.json`; TV1 đã đối chiếu độc lập kết quả này với ticket, nhãn detection và guideline của job. Kết quả H16 cần được kiểm trên gói bàn giao chính thức.

## File bàn giao

- `submission/reviews/TV6.csv`: kết luận ảnh TV6 đã xem.
- `submission/r2412007/trace.json`: các danh sách `tier_a`, `tier_b`, `notify`.

