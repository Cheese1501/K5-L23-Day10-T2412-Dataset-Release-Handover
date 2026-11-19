# Tiến độ TV1 — Lê Quang Khải

Cập nhật ngày 20/11/2026. Nhánh tích hợp và push là **dev**. Seed luyện tập **2412007**, release cha **lab250_ebedbc794d29**.

## Hiện trạng

- Đã hợp nhất các nhánh TV4 và TV6 thông qua nhánh `TV6`, sau đó hợp nhất `hieu` của TV5. Giữ lịch sử commit và đủ nhật ký AI của các thành viên.
- Đã nhận 6/6 kết luận gán nhãn do người xem cung cấp. Ca TV6 dùng ghi chú mới nhất trong `submission/reviews/TV6.csv`. Giữ nguyên phân loại `class_swap` của ca này.
- Đã nhận kết quả `intact` cho ảnh lệch hash `000000004765` từ TV5.
- Danh sách lỗi cuối của đợt review này có 16 target trên 250 ảnh, tương ứng 6,4%, v1 HOLD.
- Truy vết chạy lại bằng công cụ TV6 có 4 ảnh tầng A, 3 ảnh tầng B và notify `A05`, `Q02`.
- V2 đã dựng tại `runs/r2412007/handover/lab250_ebedbc794d29_v2/`, có 242 ảnh, 1.656 nhãn, 8 ảnh rework. Đã đóng gói lại và kiểm đạt; README v2 ghi Release theo xử lý lỗi detection của bài lab. Ca bảo mật vẫn nêu HOLD theo tình huống guideline yêu cầu làm mờ.
- Đã xuất các output đang có bằng script gốc sang `submission/r2412007/`, gồm thư mục v2 và checksum. ZIP giữ trong `runs/`.
- 30 kiểm thử đạt sau hợp nhất, gồm validator TV2, công cụ TV4, điều phối TV1, lưu review và MetricsTest.
- GitHub của TV1, TV2, TV4, TV5 đã được đối chiếu bằng API tác giả commit công khai. TV3, TV6, TV7 chờ xác nhận tài khoản. Tên TV6 đã cập nhật theo thông tin tự khai và ảnh TV1 gửi.

## Bộ kiểm gốc

`scripts/check_handover.py` trên lô tích hợp trả **17 PASS, 0 FAIL**.

| Mục | Kết quả |
|---|---|
| H1–H13 | PASS, gồm v1 nguyên vẹn, đủ review, lỗi, file v2, rework, ownership, manifest, thống kê, split và QC. |
| H14 | PASS, đã ghi nhận phiên bản bàn giao v2 có parent. README v2 ghi Release; v1 vẫn HOLD. |
| H15 | PASS, đóng gói tái lập khớp checksum. |
| H16 | PASS, trace có ảnh và người hợp lệ. |
| H17 | PASS, TV1 xác nhận ngày 20/11/2026 rằng đã xem ảnh 000000004395 và còn thấy rõ mặt người; security.md đã hoàn tất. |

## Tự đo sau khi gộp đầy đủ review

- F1 tổng ≈ 0,8.
- F1 lỗi luật ≈ 1,0.
- F1 lỗi gán nhãn ≈ 0,6.
- F1 tier_a, tier_b và notify đều ≈ 1,0.

Kết quả lấy từ một lượt chạy `scripts/score_findings.py --run runs/r2412007` sau khi gộp đủ review. Báo cáo gốc ở `submission/r2412007/report.md`. Các kết luận nhãn là do người xem ghi nhận trong CSV.

## Các bước còn lại

[Hướng dẫn cụ thể cho những phần còn cần người thực hiện](CON_LAI.md)

1. Đã hoàn tất xác nhận ảnh khuôn mặt và security.md bằng phản hồi trực tiếp của TV1.
2. Đã chạy `python3 lab/tv1.py finish`, dựng lại, kiểm đạt và xuất gói cuối sang submission. Bộ kiểm đạt 17/17; log ở `r2412007/check_handover.txt`.
3. TV3, TV6, TV7 gửi tài khoản GitHub. Cả nhóm rà yêu cầu hai commit có nội dung mỗi người.
4. Đã nhận link Drive của lớp, chọn ngẫu nhiên đề 07 và chuẩn bị bộ ban đầu trong `submission/de_an/`: 8 lỗi luật, 7 ca gán nhãn chưa có kết luận, trace 2/9 ảnh hai tầng. Hoàn tất review bằng mắt và xuất lại kết quả. Hướng dẫn và bảng chia trong `de_an/README.md`. Thời gian 40 phút theo công bố của giảng viên.
5. Nộp link theo hạn và kênh lớp công bố.

## Lệnh dùng trên máy tích hợp

```sh
python3 lab/tv1.py status
python3 scripts/check_handover.py --run runs/r2412007
python3 lab/tv1.py finish
```

Lệnh finish đã chạy thành công ngày 20/11/2026. Bản dựng v2 trước đó đã được giữ trong tv1_backups. Mọi kết quả review đã lưu được giữ làm đầu vào. ZIP mới có SHA-256 `f6b3baf26c2a20e58a9b2203671b3ea2ea17e2e6653a7193aaad5c577a09ec83`.

## Nguồn bàn giao

| Thành viên | Nguồn đã hợp nhất |
|---|---|
| TV2 | `b5b5c8d`, hai module được tích hợp qua `ffe9b03` |
| TV4 | `07d5e0b`, công cụ và bảng tổng hợp 6 review |
| TV5 | `01f1011`, dựng v2 và review/hash |
| TV6 | `bafecc9`, công cụ trace và ghi chú review mới |

README công cụ tại `lab/README.md` và `lab/TV1_GUIDE.md`. Bộ bài luyện tập tại `submission/r2412007/` đã đạt bộ kiểm gốc 17 PASS, 0 FAIL. Kết quả này xác nhận yêu cầu định dạng và bàn giao được bộ kiểm kiểm tra; không bảo đảm mọi kết luận nhãn đều đúng.
