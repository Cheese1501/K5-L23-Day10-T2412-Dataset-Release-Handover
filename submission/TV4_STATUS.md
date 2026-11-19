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
| `000000023023` category_swap | TV4, xem chéo TV7 | `confirmed` |
| `000000023781` bbox_drift | TV5 | `confirmed` (từ `submission/reviews/TV5.csv`) |
| `000000025386` class_swap | TV6 | `confirmed` |
| `000000004765` hash | TV5 | `intact` (từ `submission/reviews/TV5_hash.csv`) |

TV2, TV3, TV6, TV7 và TV4 tự xem ảnh và nhập trên bàn làm việc review ở máy TV4. TV1 và TV5 gửi file riêng, TV4 nhập bằng `collect_reviews.py`.

## Bàn giao cho TV1 và TV5

Trong `submission/reviews/`: `review_log.csv`, `hash_review.csv`, `errors.json` (10 lỗi luật + 6 lỗi gán nhãn đã xác nhận), `assignments.csv`. Bản gộp lúc 20:29 sau lượt xem lại thứ hai.

- `rules.json` và `candidates.json` từ validator đã tích hợp TV2 trên `tv1/complete-lab` (`ffe9b03`) giống hệt bản dùng để review: 10 lỗi luật, 6 ứng viên.
- Tự đo `score_findings.py` bản cuối 20:29: F1 tổng ≈ 0,8 · lỗi luật ≈ 1,0 · lỗi gán nhãn ≈ 0,6. Các bản trước: gộp đầu ≈ 0,6, bản 19:08 ≈ 0,4. Số này dùng cho REPORT của TV7. Kết luận không được chỉnh theo điểm.
- Lô trên máy TV4 có release ID `lab250_0c34aa159f7a`. Các target trong `errors.json` là mã ảnh, nên TV1 nhập `review_log.csv` vào lô máy tích hợp và gộp lại bằng `merge_review.py` trên `lab250_ebedbc794d29`.

## Các lượt xem lại

- **19:08.** TV4 nêu các ghi chú chưa khớp loại lỗi. TV2, TV6, TV7 mở lại ảnh và chuyển ca của mình sang `category_swap`. TV3 bổ sung ghi chú.
- **20:29.** TV2, TV3, TV4, TV6 mở lại ảnh và ghi rõ vật thấy được và nguồn ghi sai. TV6 đổi `000000025386` sang `class_swap` (vật là ghế, detection ghi keyboard). Ca `000000023023` giữ cả TV4 và người xem chéo TV7.

Nhóm không dùng điểm tự đo để chọn kết luận cho từng ảnh (RULES.md). Kết luận cuối là kết luận người xem ghi.

## Kiểm với công cụ dựng v2 của TV5

Chạy `lab/build_handover.py` của nhánh `hieu` (`01f1011`) trên bản sao lô với `errors.json`, `review_log.csv`, `hash_review.csv` bản 20:29, rồi chạy `pack_release.py` và `check_handover.py`. Lineage HOLD và release chỉ được ghi vào bản sao.

- v2 có 242 ảnh, 1.656 nhãn, 8 ảnh chuyển rework, QC v1 16/250 = 6,4% ⇒ Hold.
- H1–H15 đạt. H16 (trace của TV6) và H17 (security của TV7) không có trong bản sao, nên chưa kiểm.

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

1. TV1 nhập `submission/reviews/review_log.csv` vào lô máy tích hợp, gộp lại và tính QC. TV5 dựng v2 theo `errors.json`.
