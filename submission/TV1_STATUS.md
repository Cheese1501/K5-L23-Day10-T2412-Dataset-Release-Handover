# Tiến độ TV1 — Lê Quang Khải

Cập nhật ngày 19/11/2026. MSHV `2A202603237`. Nhóm T2412 dùng seed `2412007` và lô v1 `lab250_ebedbc794d29`.

Nhánh TV1 từ lượt thiết lập lại là **`tv1/complete-lab`**. [Hướng dẫn thao tác từ chuẩn bị đến chốt bài](../lab/TV1_GUIDE.md)

## Môi trường làm việc đã thiết lập

Mở `lab/MO_LAB_TV1.command` trên macOS hoặc chạy `python3 lab/review_server.py --run runs/r2412007 --port 8765 --open`. Màn hình mở sẵn phần TV1, có ảnh gốc, box, mask, biểu mẫu ghi kết luận và nút lưu CSV. Dùng nút kiểm bàn giao để lấy báo cáo hiện tại. TV1 đã lưu một kết luận. Năm ứng viên còn lại đang chờ thành viên xem ảnh.

Chức năng lưu được kiểm bằng CSV giả lập trong thư mục tạm, gồm trường hợp hai người sửa cùng file và đổi loại lỗi. Chrome đã nhập và lưu một ca thử qua giao diện. Review thật của lô được giữ nguyên trong các bước kiểm thử.

## Công việc điều phối đã thực hiện

- Ghi đủ 7 thành viên, MSHV và vai trò theo ảnh TV1 cung cấp trong `submission/TEAM.md`.
- Ghi nhận TV1 cho biết đội hình 7 người đã được đồng ý. Tài khoản GitHub từng thành viên đang chờ cung cấp.
- Tập hợp code và tài liệu dùng chung trên nhánh `docs/t2412-lab-plan` của fork Cheese1501. Thành viên lấy SHA thực tế sau khi fetch.
- Chạy lại validator trên lô nhóm và lô sạch, so kết quả với bản chuẩn bị. Kết quả khớp.
- Kiểm release ID và SHA-256 của nhãn, mask, panoptic v1. H1 và H2 của bộ kiểm gốc đạt.
- Kiểm lineage và lưu bản sao vào `submission/lineage.jsonl`. Có đúng một event train `R-021` và một HOLD cho v1 nhóm.
- Xác định các đầu ra còn chờ để nhóm tiếp tục theo kế hoạch.
- Nhận kết quả xem ảnh `000000009891` của TV1, bổ sung nguyên ý quan sát người dùng cung cấp và xuất một dòng sang `submission/reviews/TV1.csv` để TV4 gộp.
- Đã đọc lại GUIDE, RULES, SUBMISSION, RUBRIC, CHECKPOINTS và docs/DELIVERY, fetch lại repo đề và các nhánh nhóm. Repo đề ở cùng commit gốc `1ab6ab6`. Nhánh `TV3` ở `1ab6ab6`, nhánh `hieu` ở `b1d4be0`, chưa có output review mới trên các nhánh đó tại lượt kiểm tra.
- Gộp lỗi đã biết bằng script gốc, giữ đủ 5 dòng đang chờ. Xuất checkpoint đang chuẩn bị sang `submission/r2412007/`.
- Thêm lệnh chuẩn bị, nhập CSV người xem, kiểm tiến độ và hoàn thiện v2. Pipeline được kiểm end-to-end trên dữ liệu tổng hợp với bộ kiểm gốc, có kiểm lượt chạy lại.

## Kết quả đã kiểm

| Kiểm tra | Kết quả trực tiếp |
|---|---|
| QC lỗi luật của lô nhóm | 10 target / 250 ảnh = 4,0%. |
| QC đã biết sau khi nhận TV1 | 11 target / 250 ảnh = 4,4%, v1 HOLD. Tử số còn có thể đổi khi nhận đủ review. |
| Ứng viên gán nhãn | 6 ca trên 6 ảnh, TV1 đã lưu 1 ca `class_swap/confirmed`. Còn 5 ca chờ người xem. |
| Ảnh lệch hash | 1 ảnh, trạng thái kiểm nội dung đang trống. |
| Lô sạch | 0 lỗi luật, 0 ứng viên. |
| Truy vết chạy lại | 4 ảnh tầng A, 3 ảnh tầng B, 2 người cần báo. TV6 cần tự kiểm và bàn giao bản của mình. |
| Impact | `R-021: affected=True action=review_or_retrain`. |
| Bộ kiểm gốc trên `runs/r2412007` | 2 PASS, 2 FAIL. H2 ghi nhận 11 lỗi. H3 còn các dòng chưa xem. H4 thiếu thư mục v2 chính thức, nên bộ kiểm dừng tại đó. |
| Bản nháp v2 đã chuẩn bị trước | 14 PASS, 3 FAIL tại H3, H14, H17. Đây là kết quả trên gói nháp. |
| Kiểm code | Biên dịch Python đạt. Ba test MetricsTest có sẵn đạt. |
| Kiểm luồng TV1 và lưu review | 9 kiểm thử review, 5 kiểm thử điều phối và 3 MetricsTest đạt. Bộ kiểm gốc đạt 17/17 trên lô tổng hợp trong kiểm thử, gồm lượt chạy lại. Lô thật dừng ở đầu vào người xem còn thiếu. |
| Đề ẩn trên GitHub | Repo đề và fork cùng có 0 release công khai tại lượt kiểm tra ngày 19/11/2026. |

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
git switch tv1/complete-lab
git pull --ff-only origin tv1/complete-lab
git rev-parse HEAD
```

Nếu máy đang có thay đổi chưa commit, kiểm `git status` và lưu công việc trước khi chuyển nhánh. Trên máy TV1 hiện tại, `origin` trỏ về repo đề, remote `team` mới trỏ về fork Cheese1501. Máy TV1 dùng `git fetch team` và `git pull --ff-only team tv1/complete-lab` khi cây làm việc phù hợp. Nhánh cũ `docs/t2412-lab-plan` là nền dùng chung trước lượt này.

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

TV1 đã xem ảnh `000000009891`, chọn `class_swap/confirmed` và cung cấp quan sát rằng detection cam ghi `bus`, nhưng vật thực tế là `car`. Dòng gốc ở `runs/r2412007/review_log.csv`. Bản bàn giao riêng có một dòng ở [reviews/TV1.csv](reviews/TV1.csv).

TV4 lấy dòng trong `submission/reviews/TV1.csv` để gộp vào review của nhóm theo mã ảnh và loại lỗi, đối chiếu nếu đã có nhận xét khác cho cùng ảnh. Giữ các dòng của thành viên khác trong file tổng hợp. Sau khi đủ cả hàng đợi, chạy `merge_review.py` theo hướng dẫn của lab để tạo `errors.json` cuối. Nhận xét box chưa ôm sát trong ghi chú được giữ nguyên theo TV1, còn loại lỗi đã xác nhận của ca này là `class_swap`.

Các thành viên dùng AI để phân tích code, lệnh và kế hoạch. Kết luận `confirmed` hoặc `rejected` lấy từ người đã xem ảnh theo RULES.md.

## Thứ tự TV1 tiếp tục

1. Nhận tài khoản GitHub của cả nhóm, kiểm quyền truy cập fork để mọi người lấy code và commit phần của mình.
2. Nhận phiên bản luật và danh sách ứng viên được TV2, TV3 xác nhận. Cho TV4 biết SHA dùng chung.
3. Đã xuất kết quả xem ảnh TV1 vào `submission/reviews/TV1.csv`. TV4 nhận file này từ nhánh chung để gộp.
4. Nhận `errors.json` đã gộp và `hash_review.csv`, tính lại QC v1. Chuyển tử số, mẫu số và quyết định cho TV5, TV7.
5. Nhận v2, trace và bảo mật. Chạy `check_handover.py` trên đường dẫn chính thức.
6. Khi nhóm chốt v2 và các mục khác đạt, ghi event release có parent một lần, rồi chạy lại bộ kiểm.
7. Khi 0 FAIL, chạy `export_submission.py`, kiểm những file được xuất, commit và push bộ bài luyện tập.
8. Khi giảng viên phát đề ẩn, điều phối 40 phút theo bản kế hoạch lưu trong lịch sử Git và nộp theo kênh lớp. [Kế hoạch T2412](https://github.com/Cheese1501/K5-L23-Day10-T2412-Dataset-Release-Handover/blob/b1d4be082fb6bd284daadc20882edf5058ce9738/lab/KE_HOACH_T2412.md)

Hiện trạng bàn giao là chờ review và các đầu ra chính thức. Event release v2 và việc xuất bộ bài cuối phụ thuộc các bước 4–6.

Các output đang có đã được xuất thành checkpoint trong `submission/r2412007/`. Bản này còn review trống và bảo mật đang soạn. Bộ v2 và điểm F1 sau review được bổ sung khi đủ đầu vào. Dùng `python3 lab/tv1.py status` để kiểm thực tế và `python3 lab/tv1.py finish` khi đủ kết quả.

## Tin nhắn TV1 có thể gửi nhóm

```text
T2412 dùng seed 2412007. Nhánh tích hợp TV1 hiện tại là tv1/complete-lab trên fork Cheese1501.
Mọi người fetch nhánh, ghi SHA và đọc lab/TV1_GUIDE.md trước khi bàn giao.

TV2 Đức Anh và TV3 Trường kiểm validator và danh sách ứng viên.
TV4 Huy tổng hợp review của cả nhóm rồi giao errors.json.
TV5 Hiếu kiểm ảnh lệch hash và dựng v2 sau khi có errors.json cuối.
TV6 Long kiểm trace theo ticket, guideline của job và nhãn detection.
TV7 Chi chốt bảo mật, ví dụ ảnh khuôn mặt và báo cáo số liệu.
TV1 Khải kiểm lineage, QC, nhận các đầu ra và chạy bộ kiểm cuối.

Khi bàn giao, gửi tên file, seed, SHA code, kết quả đã kiểm và phần còn vướng.
Gửi thêm tài khoản GitHub để cập nhật TEAM.md.
```
