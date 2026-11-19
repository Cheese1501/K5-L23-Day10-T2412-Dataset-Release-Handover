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

| Ca | Người xem | Kết luận |
|---|---|---|
| `000000009891` class_swap | TV1 | `confirmed` (từ `submission/reviews/TV1.csv`) |
| `000000018491` category_swap | TV2 | `confirmed` |
| `000000006012` instance_merge | TV3 | `confirmed` |
| `000000023023` category_swap | TV7 (TV4 xem lần đầu ghi class_swap, xem bảng dưới) | `confirmed` |
| `000000023781` bbox_drift | TV5 | `confirmed` (từ `submission/reviews/TV5.csv`) |
| `000000025386` category_swap | TV6 | `confirmed` |
| `000000004765` hash | TV5 | `intact` (từ `submission/reviews/TV5_hash.csv`) |

TV2, TV3, TV6, TV7 và TV4 tự xem ảnh và nhập trên bàn làm việc review ở máy TV4. TV1 và TV5 gửi file riêng, TV4 nhập bằng `collect_reviews.py`.

## Bàn giao cho TV1 và TV5

Trong `submission/reviews/`: `review_log.csv`, `hash_review.csv`, `errors.json` (10 lỗi luật + 6 lỗi gán nhãn đã xác nhận), `assignments.csv`. Bản gộp lúc 19:08 sau khi TV2, TV3, TV6, TV7 xem lại ảnh.

- `rules.json` và `candidates.json` từ validator đã tích hợp TV2 trên `tv1/complete-lab` (`ffe9b03`) giống hệt bản dùng để review: 10 lỗi luật, 6 ứng viên.
- Tự đo `score_findings.py`: bản gộp đầu F1 lỗi gán nhãn ≈ 0,6. Bản hiện tại F1 tổng ≈ 0,8 · lỗi luật ≈ 1,0 · lỗi gán nhãn ≈ 0,4.
- Lô trên máy TV4 có release ID `lab250_0c34aa159f7a`. Các target trong `errors.json` là mã ảnh, nên TV1 nhập `review_log.csv` vào lô máy tích hợp và gộp lại bằng `merge_review.py` trên `lab250_ebedbc794d29`.

## Lượt xem lại lúc 19:08

Sau khi TV4 nêu các ghi chú chưa khớp loại lỗi, người xem tự mở lại ảnh và sửa trên bàn làm việc: TV2 (`000000018491`), TV6 (`000000025386`) và TV7 (`000000023023`) chuyển sang `category_swap`, TV3 bổ sung ghi chú `000000006012`. F1 lỗi gán nhãn sau lượt này ≈ 0,4.

Nhóm không dùng điểm tự đo để chọn kết luận cho từng ảnh (RULES.md). Kết luận cuối là kết luận người xem ghi.

Ca `000000023023`: TV4 xem lần đầu ghi `class_swap` ("Vật bị ghi nhầm class"), TV7 xem chéo và chốt `category_swap`. Dòng hiện tại chỉ còn tên TV7. TV4 cần ghi lại quan sát của mình (vật là vali hay túi xách) để dòng cuối có tên cả hai người.

## Đã làm

- Bỏ danh sách mã ảnh ghi cứng trong `lab/review_server.py`. Với bản cũ, trên mọi seed khác 2412007 và trên đề ẩn (`img_0001…`), không ca nào có người phụ trách, và TV7 chỉ thấy ca xem chéo nếu ca đó thuộc TV4. Bảng chia giờ đọc từ `assignments.csv` của lô, chưa có thì tự chia đều.
- Thêm `lab/split_review.py` để chia và in bảng phân công.
- Thêm `lab/collect_reviews.py` để thành viên xuất `submission/reviews/TVx.csv` và TV4 nhập vào lô. Công cụ báo xung đột, không ghi đè.
- Thêm `--delivery` cho `review_server.py` để dùng khi `delivery/` của đề ẩn ở gốc repo. Thêm `lab/MO_LAB_WINDOWS.cmd`. Công cụ review tự đặt UTF-8 cho console.
- Thêm `tests/test_tv4_review.py` (9 test). Test cũ trong `tests/test_review_workspace.py` vẫn đạt.

## Đã kiểm trên máy Windows

| Lô | Lệnh tạo | Kết quả |
|---|---|---|
| `runs/r2412007` | `run_lab.py --seeds 2412007` | 10 lỗi luật, 6 ứng viên, 1 hash. Mã ảnh khớp kế hoạch. Release ID ở máy này là `lab250_0c34aa159f7a`, khác `lab250_ebedbc794d29` của máy tích hợp, nên bản `errors.json` chính thức gộp trên máy TV1. |
| `runs/tv4/r2412004` | `inject_release.py --seed 2412004` | 10 lỗi luật, 8 ứng viên, 2 hash. Bảng chia đều 7 người. |
| `runs/tv4/opaque` → `de_an_sim` | `inject_release.py --seed 2412404 --opaque` | 11 lỗi luật, 5 ứng viên, 1 hash. Validate, prepare và split mất khoảng 14 giây. Server với `--delivery` trả ảnh và mask. |
| `runs/tv4/clean` | `inject_release.py --seed 5 --no-faults` | 0 lỗi luật, 0 ứng viên, CSV chỉ có header. |

Các lô `inject_release.py` không ghi vào `runs/lineage.jsonl`.

## Còn chờ

1. TV4 và TV7 thống nhất ca `000000023023`, ghi cả hai tên.
2. TV1 nhập `submission/reviews/review_log.csv` vào lô máy tích hợp, gộp lại và tính QC. TV5 dựng v2 theo `errors.json`.
