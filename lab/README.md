# Chạy bài Day 10 trên macOS

[Quy trình TV1 từ thiết lập đến chốt bài](TV1_GUIDE.md). Nhánh công việc TV1 hiện là `dev`.

Repo và dữ liệu COCO đã được tải vào workspace. Python yêu cầu từ 3.10 và các lệnh chạy từ thư mục gốc. Trên Windows dùng `py` thay `python3` và đặt biến bằng cú pháp PowerShell.

## Bàn làm việc TV1 có lưu kết quả

Trên macOS, nhấp đúp `lab/MO_LAB_TV1.command`. Launcher chuẩn bị các file còn thiếu, giữ kết quả đã lưu rồi mở trình duyệt tại địa chỉ localhost được in trong Terminal. Trên các hệ điều hành khác có thể chạy các lệnh dưới đây từ thư mục gốc.

```sh
python3 lab/tv1.py prepare
python3 lab/review_server.py --run runs/r2412007 --port 8765 --open
```

Màn hình chọn sẵn TV1 và ảnh `000000009891`. Phóng to ảnh, bật mask khi cần, chọn loại lỗi và kết luận, viết ít nhất 20 ký tự mô tả quan sát, đánh dấu đã trực tiếp xem rồi bấm **Lưu kết quả xem ảnh**. Công cụ lưu vào `review_log.csv` của lô và sao lưu CSV cũ trong `review_backups/`. Thành viên khác chọn đúng tên ở phần người đang xem. TV5 có thêm ca kiểm ảnh lệch hash. Khi có kết quả của người khác, công cụ yêu cầu xác nhận trước khi thay kết luận và giữ bản sao cũ.

TV4 dùng nút gộp khi đủ review. TV1 dùng nút kiểm bàn giao sau khi nhận các đầu ra. Dữ liệu hiện tại đã có 1/6 ca gán nhãn, còn 5 ca và 1 ca hash chờ người xem. Mỗi máy lưu CSV trong lô của máy đó. Người làm trên máy khác gửi CSV cho TV4 gộp và chuyển về máy tích hợp theo hướng dẫn TV1. Giữ Terminal chạy khi sử dụng màn hình này. Khi mở lại launcher, công cụ dùng lại server cùng lô nếu đang chạy.

## Chia ảnh và gộp review (TV4)

Bảng chia nằm trong `assignments.csv` của từng lô (`image,kind,owner,cross`), không ghi cứng trong code, nên dùng được cho seed khác và đề ẩn. Chưa có file thì bàn làm việc tự chia đều theo tải: ảnh lệch hash giao TV5, mỗi ca một người xem, ca bất đồng lớp thêm một người xem chéo. Người xem chéo thấy ca đó trong mục "Việc được giao cho tôi". TV4 có thể sửa tay file CSV.

```sh
python3 lab/split_review.py --workdir runs/r2412007        # in bảng chia, không ghi đè file đã có
```

Thành viên xem ảnh trên máy riêng thì xuất phần của mình rồi commit hoặc gửi TV4. TV4 nhập tất cả vào lô. Ca hai người kết luận khác nhau được báo `XUNG ĐỘT` và giữ nguyên để TV4 hỏi lại người xem.

```sh
python3 lab/collect_reviews.py --run runs/r2412007 --export TV3          # → submission/reviews/TV3.csv
python3 lab/collect_reviews.py --run runs/r2412007 --import --dry-run    # TV4 xem trước
python3 lab/collect_reviews.py --run runs/r2412007 --import              # TV4 ghi, có sao lưu
```

**Windows.** Nhấp đúp `lab\MO_LAB_WINDOWS.cmd`, hoặc đặt `$env:PYTHONUTF8=1` trước khi chạy `py scripts/...`. Thiếu biến này, `run_lab.py` và `inject_release.py` dừng giữa chừng vì lỗi in tiếng Việt và để lại `runs/r<seed>` dở dang. Khi đó xoá thư mục dở rồi chạy lại.

**Đề ẩn (delivery ở gốc repo).** Thư mục làm việc tách khỏi `delivery/`. Ba lệnh đầu chạy khoảng 15 giây.

```sh
python3 validator/validate.py delivery --out runs/de_an_work/rules.json --candidates runs/de_an_work/candidates.json
python3 lab/prepare_review.py delivery --workdir runs/de_an_work
python3 lab/split_review.py --workdir runs/de_an_work
python3 lab/review_server.py --run runs/de_an_work --delivery delivery --open
# Sau khi đủ kết luận: bấm "Gộp review" rồi chép sang bộ nộp.
mkdir -p submission/de_an
cp runs/de_an_work/{candidates.json,review_log.csv,errors.json} submission/de_an/
```

## Mở lô luyện tập nhóm T2412

```sh
RUN=runs/r2412007
open "$RUN/review.html"
```

`rules.json` và `errors.json` trên máy này hiện chỉ có lỗi luật. `draft/` chứa gói v2 đang chờ nhóm chốt và `check-draft.txt` là kết quả kiểm gói nháp. Các lô thử trước khi chốt nhóm nằm trong `runs/practice-demo/` với lineage riêng.

## Tạo lại lô T2412 trên máy thành viên

Seed `2412007` lấy từ ví dụ `2412 × 1000 + 7` trong GUIDE.md. Lần chạy đầu tiên của `run_lab.py` gắn training run R-021 với lô luyện tập. Nếu máy đã có `runs/r2412007/delivery/`, mở hàng đợi ở mục trên.

```sh
SEED=2412007
RUN="runs/r$SEED"
python3 scripts/download_public.py
python3 scripts/run_lab.py --seeds "$SEED"
python3 validator/validate.py "$RUN/delivery" --out "$RUN/rules.json" --candidates "$RUN/candidates.json"
python3 lab/trace_ticket.py "$RUN/delivery" --out "$RUN/trace.json"
python3 lab/prepare_review.py "$RUN/delivery" --workdir "$RUN"
open "$RUN/review.html"
```

Chia lượt xem cho cả nhóm. Trong `review_log.csv`, mỗi ca cần `confirmed` hoặc `rejected`, ghi chú ít nhất 20 ký tự nêu người xem và chi tiết thấy trên ảnh. Với bất đồng lớp, ghi `class_swap` nếu detection sai hoặc `category_swap` nếu panoptic sai. Trong `hash_review.csv`, ghi `intact` nếu mở được ảnh và nội dung đúng, hoặc `damaged` nếu ảnh hỏng, kèm người xem và lý do. Lệnh chuẩn bị review giữ nguyên CSV có sẵn.

Hoàn tất `$RUN/security.md` với tên một ảnh mà nhóm đã mở và thấy rõ mặt người. Nếu chưa có file trên máy thành viên, dùng [mẫu bảo mật](../templates/security.md) để viết ba mục.

## Chốt lô và kiểm

Sau khi hoàn thành review, chạy các lệnh sau rồi đọc `errors.json` và báo cáo điểm.

```sh
python3 scripts/merge_review.py --rules "$RUN/rules.json" --review "$RUN/review_log.csv" --out "$RUN/errors.json"
python3 scripts/score_findings.py --run "$RUN"
python3 lab/build_handover.py --run "$RUN"
RID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["release_id"])' "$RUN/delivery/release.json")
V2="$RUN/handover/${RID}_v2"
python3 scripts/pack_release.py "$V2"
```

Mở `$V2/README.txt` kiểm số liệu và quyết định. Nếu QC v1 vượt 2%, ghi HOLD và chạy impact. Nếu lineage đã có event HOLD cho release ID đó, chạy riêng lệnh impact và bộ kiểm.

```sh
python3 scripts/lineage.py --root "$(dirname "$RUN")" record --event decision --release-id "$RID" --decision HOLD
python3 scripts/lineage.py --root "$(dirname "$RUN")" impact --release-id "$RID"
python3 scripts/check_handover.py --run "$RUN"
```

Nếu kiểm tra chỉ còn H14 vì thiếu event phát hành và nhóm đã chốt v2, ghi release rồi kiểm lại. Trường hợp QC v1 từ 2% trở xuống, hỏi giảng viên về H14: GUIDE quy định Release trong ngưỡng còn bộ kiểm hiện yêu cầu HOLD cho v1 luyện tập.

```sh
python3 scripts/lineage.py --root "$(dirname "$RUN")" record --event release --release-id "${RID}_v2" --parent "$RID"
python3 scripts/check_handover.py --run "$RUN"
```

## Nộp

Fork public của nhóm là `Cheese1501/K5-L23-Day10-T2412-Dataset-Release-Handover`. Đối chiếu tên repo với quy ước giảng viên công bố trước khi nộp. Điền danh sách thành viên trong [TEAM.md](../submission/TEAM.md), cập nhật [REPORT.md](../submission/REPORT.md) sau review và bổ sung [prompts.md](../submission/prompts.md) sau khi nhóm kiểm lại. Khi bộ kiểm đạt, xuất lô chính thức bằng `python3 scripts/export_submission.py --run "$RUN"`. Mỗi thành viên cần ít nhất hai commit mang danh tính của mình.

Khi giảng viên phát `de_an.zip`, làm trong thời gian 40 phút theo Pha 6 và nộp `errors.json`, `candidates.json`, `review_log.csv`, `trace.json` trong `submission/de_an/`. Push lên repo nhóm và nộp link theo hướng dẫn của lớp. [Yêu cầu nộp bài](../SUBMISSION.md)
