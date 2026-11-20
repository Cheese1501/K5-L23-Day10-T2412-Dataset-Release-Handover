# Kiểm tra hoàn thành và việc còn lại — T2412

Cập nhật ngày 20/11/2026. Nhóm đã tập hợp code, kết quả luyện tập và đề 07 về **main**, giữ lịch sử đóng góp từ dev. Các nhánh TV2–TV6 không còn bản vá riêng chưa được tích hợp hoặc chưa có bản tương đương.

## Kết quả theo thành viên

| Thành viên | Phần đã bàn giao | Việc còn lại |
|---|---|---|
| TV1 — Lê Quang Khải | Điều phối, lineage, QC, bộ kiểm; xác nhận khuôn mặt; review đề 07 | Chốt tên repo, hạn/kênh nộp; lưu xác nhận nộp và giờ làm đề thực tế |
| TV2 — Nguyễn Đức Anh | Module duplicate_box/thing_overlap; review 000000018491 | Một đóng góp gốc và một cherry-pick cùng thay đổi; cần thêm đóng góp thực tế để đủ hai commit có nội dung |
| TV3 — Hoàng Quang Trường | Kiểm đầu vào validator, crosscheck, 20 test; review 000000006012 | Hiện có một commit gốc được tích hợp; cần thêm một commit có nội dung của mình |
| TV4 — Dương Quốc Huy | Công cụ review, chia/gộp ca; 6 kết luận và errors cuối | Chuẩn bị vấn đáp; giữ đúng người xem trong log |
| TV5 — Đặng Trung Hiếu | Review bbox, hash intact; dựng v2 và README | Chuẩn bị giải thích số ảnh/box, rework và hash |
| TV6 — Nguyễn Nhân Thành Long | Công cụ truy vết, trace 4/3/2; review 000000025386 | Chuẩn bị giải thích tầng A/B và notify |
| TV7 — Hoàng Kim Chi | Xem chéo ghi trong log TV4; kiểm hồ sơ, báo cáo nhóm/cá nhân, bảo mật; kiểm gói trên main | Đã có TV7_VAN_DAP.md; trực tiếp trả lời khi vấn đáp |

## Luyện tập

Đủ 6/6 review confirmed, ảnh hash intact, trace, bảo mật và v2. QC v1 **16/250 = 6,4% → HOLD**. V2 **242 ảnh, 1.656 box, 8 ảnh rework**. Bộ kiểm gốc kiểm lại đạt **17 PASS, 0 FAIL**; 50 kiểm thử code nhóm đạt.

Ca khuôn mặt là 000000004395.jpg, do TV1 trực tiếp xác nhận ngày 20/11/2026. Khi guideline yêu cầu làm mờ, nhóm phải HOLD và báo người phụ trách. Hồ sơ không ghi nhận đã làm mờ hoặc gửi thông báo ngoài thực tế.

Checksum ZIP đã tính lại từ bộ file thực sự lưu trong Git. Khi đóng gói trên máy khác, giữ nguyên bytes handover và đối chiếu .sha256. Không đưa ZIP, runs, data_source hoặc delivery đề ẩn vào Git.

## Đề 07

Đủ errors.json, candidates.json, review_log.csv và trace.json. Review có **6 confirmed/1 rejected**, ảnh hash intact, errors **8 luật + 6 gán nhãn = 14 lỗi**. Trace **2 ảnh tầng A, 9 tầng B, 4 mã người**. Người trực tiếp ghi các kết luận đề 07 là TV1. Chưa có F1 đề ẩn.

TV1 xác nhận thời lượng lớp là 20 phút; chưa có giờ bắt đầu/kết thúc thực tế để xác minh thời lượng đã làm.

## Thủ tục trước khi nộp

1. TV2 và TV3 tự bổ sung đóng góp có nội dung để đáp ứng hai commit mỗi người; không tạo commit rỗng hoặc đếm cherry-pick trùng như công việc khác nhau.
2. TV1 xác nhận tên repo hiện tại được lớp chấp nhận hoặc theo mẫu SUBMISSION.md, cùng hạn và kênh nộp.
3. Mỗi người chuẩn bị vấn đáp: giải thích/sửa một đoạn validator, giải thích review của mình và cách đếm một số trong README v2.
4. Nhóm nộp link theo hướng dẫn lớp, lưu SHA main, thời điểm và xác nhận nộp. Hồ sơ hiện chưa có bằng chứng nộp LMS.

Phần hồ sơ TV7 đã được đối chiếu đầy đủ tại [DOI_CHIEU_YEU_CAU.md](DOI_CHIEU_YEU_CAU.md); [TV7_VAN_DAP.md](TV7_VAN_DAP.md) chuẩn bị ba nội dung vấn đáp bắt buộc. Không còn file nội dung TV7 cần nhận thêm từ thành viên khác.
