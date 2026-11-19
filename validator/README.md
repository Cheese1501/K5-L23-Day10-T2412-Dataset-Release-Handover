# Validator của nhóm

Viết `validate.py` ở đây. Giao diện cố định:

```
python validator/validate.py <thư_mục_delivery> --out <errors.json> [--candidates <candidates.json>]
```

Chỉ đọc thư mục delivery được truyền vào; chỉ thư viện chuẩn; không mạng. Xem [GUIDE.md](../GUIDE.md) Pha 1–2 và [RULES.md](../RULES.md).

## Phần TV2 đã tích hợp

TV1 nhận hai module từ commit `b5b5c8d` trên nhánh `ducanh`, giữ tác giả TV2 bằng cherry-pick.

- `rules_detection.find_duplicate_boxes(delivery_dir)` trả danh sách `duplicate_box`.
- `rules_panoptic.find_thing_overlaps(delivery_dir)` trả danh sách `thing_overlap`.

`validate.py` gọi mỗi hàm một lần cho mỗi lô, gộp các cặp `(type, target)` vào tập lỗi chung. Phần kiểm hai lỗi này trong code TV1 cũ đã được thay bằng lời gọi module. Bộ đối chiếu tiếp tục dùng pixel mask để sinh ứng viên.

TV1 đã chạy lại seed `2412007`, seed `22` và lô sạch 50 ảnh. Kết quả lần lượt là 10, 9 và 0 lỗi luật, khớp baseline. Lô nhóm có 6 ứng viên, seed 22 có 6 ứng viên, lô sạch có 0 ứng viên. Kết quả này xác nhận việc tích hợp trên các lô đã kiểm. Bản chấm F1 cuối được cập nhật khi có đủ review theo RULES.md.
