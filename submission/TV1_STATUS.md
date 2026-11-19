# Tiến độ TV1 — Lê Quang Khải

Cập nhật ngày 19/11/2026. MSHV `2A202603237`. Nhóm T2412 dùng seed `2412007` và lô v1 `lab250_ebedbc794d29`.

## Công việc điều phối đã thực hiện

- Ghi đủ 7 thành viên, MSHV và vai trò theo ảnh TV1 cung cấp trong `submission/TEAM.md`.
- Ghi nhận TV1 cho biết đội hình 7 người đã được đồng ý. Tài khoản GitHub từng thành viên đang chờ cung cấp.
- Tập hợp code và tài liệu dùng chung trên nhánh `docs/t2412-lab-plan` của fork Cheese1501. Thành viên lấy SHA thực tế sau khi fetch.
- Chạy lại validator trên lô nhóm và lô sạch, so kết quả với bản chuẩn bị. Kết quả khớp.
- Kiểm release ID và SHA-256 của nhãn, mask, panoptic v1. H1 và H2 của bộ kiểm gốc đạt.
- Kiểm lineage và lưu bản sao vào `submission/lineage.jsonl`. Có đúng một event train `R-021` và một HOLD cho v1 nhóm.
- Xác định các đầu ra còn chờ để nhóm tiếp tục theo kế hoạch.

## Kết quả đã kiểm

| Kiểm tra | Kết quả trực tiếp |
|---|---|
| QC lỗi luật của lô nhóm | 10 target / 250 ảnh = 4,0%, quyết định v1 HOLD. Sau khi gộp review cần tính lại tử số. |
| Ứng viên gán nhãn | 6 ca trên 6 ảnh, cả 6 dòng review đang chờ kết luận của thành viên. |
| Ảnh lệch hash | 1 ảnh, trạng thái kiểm nội dung đang trống. |
| Lô sạch | 0 lỗi luật, 0 ứng viên. |
| Truy vết chạy lại | 4 ảnh tầng A, 3 ảnh tầng B, 2 người cần báo. TV6 cần tự kiểm và bàn giao bản của mình. |
| Impact | `R-021: affected=True action=review_or_retrain`. |
| Bộ kiểm gốc trên `runs/r2412007` | 2 PASS, 2 FAIL. H3 chờ review. H4 thiếu thư mục v2 chính thức, nên bộ kiểm dừng tại đó. |
| Bản nháp v2 đã chuẩn bị trước | 14 PASS, 3 FAIL tại H3, H14, H17. Đây là kết quả trên gói nháp. |
| Kiểm code | Biên dịch Python đạt. Ba test MetricsTest có sẵn đạt. |

Các lệnh TV1 đã chạy trên máy tích hợp, từ thư mục gốc repo.

```sh
python3 -m py_compile validator/validate.py lab/*.py
python3 -m unittest discover -s tests -k MetricsTest -v
python3 validator/validate.py runs/r2412007/delivery --out runs/tv1_checks/rules.json --candidates runs/tv1_checks/candidates.json
python3 validator/validate.py runs/practice-demo/clean/delivery --out runs/tv1_checks/clean_rules.json --candidates runs/tv1_checks/clean_candidates.json
python3 lab/trace_ticket.py runs/r2412007/delivery --out runs/tv1_checks/trace.json
python3 scripts/lineage.py impact --release-id lab250_ebedbc794d29
python3 scripts/check_handover.py --run runs/r2412007
```

Log cục bộ ở `runs/tv1_checks/check_handover.txt`. Người mới dùng các bước tạo lô trong `lab/README.md`. Thư mục lô sạch trên máy này ở `runs/practice-demo/clean`, còn lệnh tạo mới trong hướng dẫn dùng `runs/clean`.

## Bản code chung để thành viên lấy về

Trong clone của fork nhóm, `origin` trỏ về Cheese1501, dùng các lệnh sau.

```sh
git fetch origin
git switch docs/t2412-lab-plan
git pull --ff-only origin docs/t2412-lab-plan
git rev-parse HEAD
```

Nếu máy đang có thay đổi chưa commit, kiểm `git status` và lưu công việc trước khi chuyển nhánh. Trên máy TV1 hiện tại, `origin` trỏ về repo đề, remote `team` mới trỏ về fork Cheese1501. Máy TV1 dùng `git fetch team` và `git pull --ff-only team docs/t2412-lab-plan` khi cây làm việc phù hợp.

Code được chia sẻ gồm `validator/validate.py`, `lab/prepare_review.py`, `lab/trace_ticket.py` và `lab/build_handover.py`. Dùng hướng dẫn `lab/README.md` để tạo lại dữ liệu. Các output trong `runs/` được tạo trên máy tích hợp hoặc chuyển theo đúng seed qua kênh nội bộ nhóm.

## TV1 đang nhận bàn giao từ ai

| Thành viên | Đầu ra cần giao | TV1 làm tiếp sau khi nhận |
|---|---|---|
| TV2 — Nguyễn Đức Anh | `rules.json` và kết quả kiểm luật trên code chung, seed phụ và lô sạch. | Đối chiếu đủ lỗi luật trong `errors.json` mà TV4 gộp. |
| TV3 — Hoàng Quang Trường | `candidates.json` và số ứng viên trên lô sạch. | Xác nhận TV4 chia đủ danh sách theo phiên bản này. |
| TV4 — Dương Quốc Huy | `review_log.csv`, `errors.json` đã gộp từ kết quả xem ảnh thực tế. | Tính lại QC v1, đối chiếu HOLD, chuyển file cho TV5. |
| TV5 — Đặng Trung Hiếu | `hash_review.csv`, thư mục `handover/<release_id>_v2/` và `.sha256`. | Kiểm số liệu, bộ kiểm gốc và quan hệ v1 → v2. |
| TV6 — Nguyễn Thành Thành Long | `trace.json` và tiêu chí truy vết theo guideline của job. | Kiểm H16 và chuyển số liệu cho TV7. |
| TV7 — Hoàng Kim Chi | `security.md` có ví dụ ảnh đã xem, báo cáo và nhật ký AI cập nhật. | Kiểm H17, tính nhất quán số liệu và bộ bài nộp. |

## Việc TV1 cần tự làm trên ảnh

TV1 được giao ảnh `000000009891`. Mở `runs/r2412007/review.html`, phóng to vùng bất đồng, rồi gửi TV4 tên vật nhìn thấy, detection và panoptic ghi lớp gì, loại lỗi cùng kết luận. Ghi chú phải thể hiện quan sát của người xem. Dòng review hiện đang chờ TV1 cung cấp quan sát.

Các thành viên dùng AI để phân tích code, lệnh và kế hoạch. Kết luận `confirmed` hoặc `rejected` lấy từ người đã xem ảnh theo RULES.md.

## Thứ tự TV1 tiếp tục

1. Nhận tài khoản GitHub của cả nhóm, kiểm quyền truy cập fork để mọi người lấy code và commit phần của mình.
2. Nhận phiên bản luật và danh sách ứng viên được TV2, TV3 xác nhận. Cho TV4 biết SHA dùng chung.
3. Xem ảnh TV1 được giao và gửi kết quả cho TV4.
4. Nhận `errors.json` đã gộp và `hash_review.csv`, tính lại QC v1. Chuyển tử số, mẫu số và quyết định cho TV5, TV7.
5. Nhận v2, trace và bảo mật. Chạy `check_handover.py` trên đường dẫn chính thức.
6. Khi nhóm chốt v2 và các mục khác đạt, ghi event release có parent một lần, rồi chạy lại bộ kiểm.
7. Khi 0 FAIL, chạy `export_submission.py`, kiểm những file được xuất, commit và push bộ bài luyện tập.
8. Khi giảng viên phát đề ẩn, điều phối 40 phút theo `lab/KE_HOACH_T2412.md` và nộp theo kênh lớp.

Hiện trạng bàn giao là chờ review và các đầu ra chính thức. Event release v2 và việc xuất bộ bài cuối phụ thuộc các bước 4–6.

## Tin nhắn TV1 có thể gửi nhóm

```text
T2412 dùng seed 2412007, nhánh docs/t2412-lab-plan trên fork Cheese1501.
Mọi người fetch nhánh, ghi SHA và đọc lab/KE_HOACH_T2412.md trước khi làm.

TV2 Đức Anh và TV3 Trường kiểm validator và danh sách ứng viên.
TV4 Huy tổng hợp review của cả nhóm rồi giao errors.json.
TV5 Hiếu kiểm ảnh lệch hash và dựng v2 sau khi có errors.json cuối.
TV6 Long kiểm trace theo ticket, guideline của job và nhãn detection.
TV7 Chi chốt bảo mật, ví dụ ảnh khuôn mặt và báo cáo số liệu.
TV1 Khải kiểm lineage, QC, nhận các đầu ra và chạy bộ kiểm cuối.

Khi bàn giao, gửi tên file, seed, SHA code, kết quả đã kiểm và phần còn vướng.
Gửi thêm tài khoản GitHub để cập nhật TEAM.md.
```
