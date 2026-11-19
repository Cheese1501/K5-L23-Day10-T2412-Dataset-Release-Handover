# Tiến độ TV1 — Lê Quang Khải

Cập nhật ngày 19/11/2026. Nhánh tích hợp và push là **dev**. Seed luyện tập **2412007**, release cha **lab250_ebedbc794d29**.

## Hiện trạng

- Đã hợp nhất các nhánh TV4 và TV6 thông qua nhánh `TV6`, sau đó hợp nhất `hieu` của TV5. Giữ lịch sử commit và đủ nhật ký AI của các thành viên.
- Đã nhận 6/6 kết luận gán nhãn do người xem cung cấp. Ca TV6 dùng ghi chú mới nhất trong `submission/reviews/TV6.csv`. Giữ nguyên phân loại `class_swap` của ca này.
- Đã nhận kết quả `intact` cho ảnh lệch hash `000000004765` từ TV5.
- Danh sách lỗi cuối của đợt review này có 16 target trên 250 ảnh, tương ứng 6,4%, v1 HOLD.
- Truy vết chạy lại bằng công cụ TV6 có 4 ảnh tầng A, 3 ảnh tầng B và notify `A05`, `Q02`.
- V2 đã dựng tại `runs/r2412007/handover/lab250_ebedbc794d29_v2/`, có 242 ảnh, 1.656 nhãn, 8 ảnh rework. Đang giữ trạng thái HOLD để chờ mục bảo mật và kiểm cuối.
- Đã xuất các output đang có bằng script gốc sang `submission/r2412007/`, gồm thư mục v2 và checksum. ZIP giữ trong `runs/`.
- 30 kiểm thử đạt sau hợp nhất, gồm validator TV2, công cụ TV4, điều phối TV1, lưu review và MetricsTest.
- GitHub của TV1, TV2, TV4, TV5 đã được đối chiếu bằng API tác giả commit công khai. TV3, TV6, TV7 chờ xác nhận tài khoản. Tên TV6 đã cập nhật theo thông tin tự khai và ảnh TV1 gửi.

## Bộ kiểm gốc

`scripts/check_handover.py` trên lô tích hợp trả **16 PASS, 1 FAIL**.

| Mục | Kết quả |
|---|---|
| H1–H13 | PASS, gồm v1 nguyên vẹn, đủ review, lỗi, file v2, rework, ownership, manifest, thống kê, split và QC. |
| H14 | PASS, đã ghi nhận phiên bản bàn giao v2 có parent. README của v2 vẫn giữ HOLD. |
| H15 | PASS, đóng gói tái lập khớp checksum. |
| H16 | PASS, trace có ảnh và người hợp lệ. |
| H17 | Chờ ví dụ ảnh có khuôn mặt rõ do người trong nhóm xác nhận trong security.md. |

## Tự đo sau khi gộp đầy đủ review

- F1 tổng ≈ 0,8.
- F1 lỗi luật ≈ 1,0.
- F1 lỗi gán nhãn ≈ 0,6.
- F1 tier_a, tier_b và notify đều ≈ 1,0.

Kết quả lấy từ một lượt chạy `scripts/score_findings.py --run runs/r2412007` sau khi gộp đủ review. Báo cáo gốc ở `submission/r2412007/report.md`. Các kết luận nhãn là do người xem ghi nhận trong CSV.

## Các bước còn lại

[Hướng dẫn cụ thể cho những phần còn cần người thực hiện](CON_LAI.md)

1. TV7 hoặc người trong nhóm trực tiếp xác nhận mã ảnh có khuôn mặt nhìn rõ và quan sát cụ thể.
2. Cập nhật `runs/r2412007/security.md`, chạy `python3 lab/tv1.py finish` để dựng lại, kiểm, ghi release có parent và xuất gói khi đủ điều kiện.
3. TV3, TV6, TV7 gửi tài khoản GitHub. Cả nhóm rà yêu cầu hai commit có nội dung mỗi người.
4. Nhận đề ẩn từ giảng viên và làm trong 40 phút theo GUIDE. Hai repo hiện có 0 release công khai tại lượt kiểm này.
5. Nộp link theo hạn và kênh lớp công bố.

## Lệnh dùng trên máy tích hợp

```sh
python3 lab/tv1.py status
python3 scripts/check_handover.py --run runs/r2412007
python3 lab/tv1.py finish
```

Lệnh finish hiện dừng nếu security.md còn phần chờ người xem. Bản dựng v2 đang có được lưu lại trong tv1_backups khi chạy dựng lại. Mọi kết quả review đã lưu được giữ làm đầu vào.

## Nguồn bàn giao

| Thành viên | Nguồn đã hợp nhất |
|---|---|
| TV2 | `b5b5c8d`, hai module được tích hợp qua `ffe9b03` |
| TV4 | `07d5e0b`, công cụ và bảng tổng hợp 6 review |
| TV5 | `01f1011`, dựng v2 và review/hash |
| TV6 | `bafecc9`, công cụ trace và ghi chú review mới |

README công cụ tại `lab/README.md` và `lab/TV1_GUIDE.md`. Bộ bài luyện tập tại `submission/r2412007/` là bản đang chuẩn bị, chờ mục H17 được hoàn tất.
