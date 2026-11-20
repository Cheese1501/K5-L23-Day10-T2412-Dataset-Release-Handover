# Bàn giao TV7 — Hoàng Kim Chi

Ngày 20/11/2026 · MSHV 2A202603172 · GitHub Cheese1501 · Nhóm T2412.

## Phần việc hoàn tất

Tôi đã tập hợp báo cáo nhóm theo sáu mục của mẫu REPORT.md, hoàn thiện [báo cáo cá nhân](TV7_REPORT.md), đối chiếu ba mục [bảo mật](r2412007/security.md), kiểm các số liệu review/QC/trace/v2 và tập hợp bài làm về main.

Ca xem chéo 000000023023 được TV4 lưu tên tôi trong review_log.csv. Ví dụ khuôn mặt 000000004395 do TV1 xác nhận; tôi giữ đúng người quan sát trong hồ sơ. Phần bảo mật trả lời HOLD và báo người phụ trách trong tình huống guideline yêu cầu làm mờ.

## Kết quả kiểm bàn giao

| Nội dung | Kết quả |
|---|---|
| Luyện tập | 16 lỗi cuối; 6 confirmed; v1 HOLD 6,4% |
| V2 | 242 ảnh, 1.656 box, 8 ảnh rework |
| Bộ kiểm gốc | 17 PASS, 0 FAIL trên bản sao kiểm chứng; giữ nguyên v1 local |
| Kiểm thử code nhóm | 50 test đạt |
| Trace luyện tập | 4 ảnh tầng A, 3 tầng B, notify A05/Q02 |
| Đề 07 | Đủ bốn file; 14 lỗi, 6 confirmed/1 rejected; trace 2/9/4 |

Tôi đã đối chiếu lỗi gán nhãn với confirmed, kiểm ca rejected không có trong errors, kiểm hash ảnh/nhãn theo manifest và tính lại checksum ZIP theo bộ file trên main. Việc kiểm định dạng không chứng minh mọi nhãn đều đúng.

Lượt chạy lại validator cho 10 lỗi luật và 6 ứng viên, khớp toàn bộ đầu ra đã bàn giao; công cụ truy vết cũng khớp trace.json. Commit `af665fe` giữ bytes gói bàn giao và cập nhật checksum tái lập. Báo cáo và hồ sơ được lưu trong commit tiếp theo của tôi trên main.

## File gửi TV1

- REPORT.md và TV7_REPORT.md.
- r2412007/security.md và check_handover.txt.
- r2412007/handover/lab250_ebedbc794d29_v2.sha256.
- CON_LAI.md để theo dõi các yêu cầu cá nhân và thủ tục nộp.
- prompts.md theo mẫu nhật ký bắt buộc của đề.

TV1 tiếp tục đối chiếu commit của TV2/TV3, chốt tên repo/hạn/kênh nộp và lưu bằng chứng nộp. Tôi chuẩn bị vấn đáp theo phần mình thực hiện.
