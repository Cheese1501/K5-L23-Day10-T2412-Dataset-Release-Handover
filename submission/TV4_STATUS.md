# Tiến độ TV4 — Dương Quốc Huy

Cập nhật ngày 19/11/2026. MSHV `2A202603311`. Làm trên nhánh `tv4/review-tools`, tách từ `docs/t2412-lab-plan` tại `7a497fc`.

## Bảng chia ảnh lô 2412007

Theo kế hoạch nhóm đã thông báo. File dữ liệu ở `runs/r2412007/assignments.csv`. Máy khác tạo lại bằng nội dung dưới đây.

```csv
image,kind,owner,cross
000000004765,hash,TV5,
000000006012,semantic,TV3,
000000009891,semantic,TV1,
000000018491,semantic,TV2,
000000023023,semantic,TV4,TV7
000000023781,semantic,TV5,
000000025386,semantic,TV6,
```

| Ca | Người xem | Trạng thái |
|---|---|---|
| `000000009891` class_swap | TV1 | `confirmed` (nhận từ `submission/reviews/TV1.csv`, đã nhập vào lô) |
| `000000018491` | TV2 | Chờ |
| `000000006012` instance_merge | TV3 | Chờ |
| `000000023023` | TV4, xem chéo TV7 | Chờ |
| `000000023781` bbox_drift | TV5 | Chờ |
| `000000025386` | TV6 | Chờ |
| `000000004765` hash | TV5 | Chờ |

## Đã làm

- Bỏ danh sách mã ảnh ghi cứng trong `lab/review_server.py`. Với bản cũ, trên mọi seed khác 2412007 và trên đề ẩn (`img_0001…`), không ca nào có người phụ trách, và TV7 chỉ thấy ca xem chéo nếu ca đó thuộc TV4. Bảng chia giờ đọc từ `assignments.csv` của lô, chưa có thì tự chia đều.
- Thêm `lab/split_review.py` để chia và in bảng phân công.
- Thêm `lab/collect_reviews.py` để thành viên xuất `submission/reviews/TVx.csv` và TV4 nhập vào lô. Công cụ báo xung đột, không ghi đè.
- Thêm `--delivery` cho `review_server.py` để dùng khi `delivery/` của đề ẩn ở gốc repo. Thêm `lab/MO_LAB_WINDOWS.cmd`. Công cụ review tự đặt UTF-8 cho console.
- Thêm `tests/test_tv4_review.py` (8 test). Test cũ trong `tests/test_review_workspace.py` vẫn đạt.

## Đã kiểm trên máy Windows

| Lô | Lệnh tạo | Kết quả |
|---|---|---|
| `runs/r2412007` | `run_lab.py --seeds 2412007` | 10 lỗi luật, 6 ứng viên, 1 hash. Mã ảnh khớp kế hoạch. Release ID ở máy này là `lab250_0c34aa159f7a`, khác `lab250_ebedbc794d29` của máy tích hợp, nên bản `errors.json` chính thức gộp trên máy TV1. |
| `runs/tv4/r2412004` | `inject_release.py --seed 2412004` | 10 lỗi luật, 8 ứng viên, 2 hash. Bảng chia đều 7 người. |
| `runs/tv4/opaque` → `de_an_sim` | `inject_release.py --seed 2412404 --opaque` | 11 lỗi luật, 5 ứng viên, 1 hash. Validate, prepare và split mất khoảng 14 giây. Server với `--delivery` trả ảnh và mask. |
| `runs/tv4/clean` | `inject_release.py --seed 5 --no-faults` | 0 lỗi luật, 0 ứng viên, CSV chỉ có header. |

Các lô `inject_release.py` không ghi vào `runs/lineage.jsonl`.

## Còn chờ

1. Ảnh của TV4: `000000023023` (người thật xem).
2. Kết luận của TV2, TV3, TV5, TV6 và ca xem chéo của TV7, gửi qua `submission/reviews/TVx.csv` hoặc nhập trực tiếp trên máy tích hợp.
3. Khi đủ 6/6 ca và hash, bấm gộp hoặc chạy `merge_review.py`, rồi giao `errors.json` và `review_log.csv` cho TV1 và TV5.
