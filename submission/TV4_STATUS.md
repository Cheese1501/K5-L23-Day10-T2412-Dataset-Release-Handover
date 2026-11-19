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
| `000000018491` class_swap | TV2 | `confirmed` |
| `000000006012` instance_merge | TV3 | `confirmed` |
| `000000023023` class_swap | TV4, xem chéo TV7 | `confirmed` |
| `000000023781` bbox_drift | TV5 | `confirmed` (từ `submission/reviews/TV5.csv`) |
| `000000025386` class_swap | TV6 | `confirmed` |
| `000000004765` hash | TV5 | `intact` (từ `submission/reviews/TV5_hash.csv`) |

TV2, TV3, TV6, TV7 và TV4 tự xem ảnh và nhập trên bàn làm việc review ở máy TV4. TV1 và TV5 gửi file riêng, TV4 nhập bằng `collect_reviews.py`.

## Bàn giao cho TV1 và TV5

Trong `submission/reviews/`: `review_log.csv`, `hash_review.csv`, `errors.json` (10 lỗi luật + 6 lỗi gán nhãn đã xác nhận), `assignments.csv`.

- `rules.json` và `candidates.json` từ validator đã tích hợp TV2 trên `tv1/complete-lab` (`ffe9b03`) giống hệt bản dùng để review: 10 lỗi luật, 6 ứng viên.
- Tự đo `score_findings.py`: F1 tổng ≈ 0,8 · lỗi luật ≈ 1,0 · lỗi gán nhãn ≈ 0,6.
- Lô trên máy TV4 có release ID `lab250_0c34aa159f7a`. Các target trong `errors.json` là mã ảnh, nên TV1 nhập `review_log.csv` vào lô máy tích hợp và gộp lại bằng `merge_review.py` trên `lab250_ebedbc794d29`.

## Cần người xem rà lại

F1 lỗi gán nhãn ≈ 0,6 nên có kết luận chưa khớp ảnh. Các ghi chú dưới đây chưa đủ để đối chiếu loại lỗi. Người xem tự mở lại ảnh và sửa trên bàn làm việc. TV4 không tự đổi kết luận của người khác.

| Ảnh | Điểm cần làm rõ |
|---|---|
| `000000018491` (TV2) | Detection ghi person, panoptic ghi toilet. Vật là người thì panoptic sai (`category_swap`). Vật là bồn cầu thì detection sai (`class_swap`). |
| `000000025386` (TV6) | Ghi chú nói box chỉ phủ 1/3, đó là box lệch, không phải sai lớp. Cần ghi vật là ghế hay bàn phím. |
| `000000023023` (TV4, TV7) | Cần ghi vật là vali hay túi xách. |
| `000000006012` (TV3) | `instance_merge` là mask panoptic gộp hai vật làm một segment. Ghi chú đang nói về box. |

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

1. TV2, TV3, TV4/TV7, TV6 rà lại các ca ở bảng trên. Nếu kết luận đổi, TV4 gộp lại và giao `errors.json` mới cho TV1 và TV5.
