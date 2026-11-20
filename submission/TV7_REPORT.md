# Báo cáo cá nhân — Hoàng Kim Chi — TV7

Nhóm T2412 · MSHV **2A202603172** · GitHub **Cheese1501** · Seed **2412007**.

## 1. Những việc tôi đã thực hiện

Tôi đối chiếu các pha với GUIDE, RULES, RUBRIC và mẫu bài nộp; chuẩn bị môi trường, tải 250 ảnh luyện tập và 50 ảnh lô sạch, kiểm cấu trúc delivery và liên kết R-021. Tôi rà các nhánh thành viên, tập hợp phần đã bàn giao về main và hoàn thiện báo cáo nhóm theo số liệu trong các file đầu ra.

Phần bảo mật được trình bày theo ba tình huống của mẫu: USB, năm việc được/không được và khuôn mặt. Tôi giữ thông tin người thực sự xem ảnh trong bằng chứng, không đứng tên thay người khác. Ví dụ khuôn mặt `000000004395.jpg` do TV1 — Lê Quang Khải xác nhận ngày 20/11/2026.

## 2. Đầu vào tôi nhận từ các thành viên

| Người bàn giao | Đầu vào tôi sử dụng |
|---|---|
| TV1 | Lineage, quyết định QC, kết quả bộ kiểm, xác nhận ảnh khuôn mặt |
| TV2, TV3 | Validator, ngưỡng đối chiếu, số lỗi luật và ứng viên trên các lô |
| TV4 | review_log.csv và errors.json sau khi tổng hợp kết luận của nhóm |
| TV5 | hash_review.csv, v2, thống kê ảnh/box, README và checksum |
| TV6 | trace.json và tiêu chí truy vết theo guideline của job |

Tôi sử dụng báo cáo tự đo sau review, không lấy các con số của bản nháp 244 ảnh làm số cuối. V2 bàn giao có 242 ảnh và 1.656 box; 8 ảnh được chuyển rework.

## 3. Phần việc phối hợp và xem chéo

Ca xem chéo của tôi được TV4 lưu trong dòng ảnh `000000023023` của [review_log.csv](r2412007/review_log.csv), với ghi chú gốc: “Vật bị bị nhầm class”. Kết luận tổng hợp là category_swap/confirmed; TV4 ghi vật ở giữa ảnh là túi xách, detection handbag đúng và panoptic suitcase sai. Tôi giữ nguyên ghi chú đã bàn giao; phần mô tả chi tiết nguồn nhãn được ghi rõ là quan sát của TV4.

Tôi phụ trách tổng hợp báo cáo và bảo mật. Việc xác nhận các review khác, ảnh hash và ca khuôn mặt được giữ đúng người thực hiện trong CSV và security.md. Với đề 07, người trực tiếp ghi nhận bảy ca là TV1.

## 4. Kết quả và cách kiểm

- Luyện tập: 10 lỗi luật, 6 ứng viên, 6 confirmed; errors cuối 16 target; QC 16/250 = 6,4%, v1 HOLD.
- F1 làm tròn: luật ≈ 1,0; gán nhãn ≈ 0,6; tổng ≈ 0,8, lấy từ report.md của lô.
- Trace: 4 ảnh tầng A, 3 ảnh tầng B, notify A05/Q02.
- V2: 242 ảnh, 1.656 box, 8 ảnh rework; các số được đối chiếu manifest, label_summary và rework_queue.
- Đề 07: 14 lỗi cuối, review 6 confirmed/1 rejected; trace 2/9 ảnh hai tầng, 4 mã người. Chưa có F1 đề ẩn.

Tôi kiểm các lỗi gán nhãn trong errors có dòng confirmed tương ứng, loại ca rejected khỏi danh sách lỗi, đối chiếu ba khóa trace và kiểm hash file bàn giao. Nhóm dùng bộ kiểm gốc cho luyện tập; kết quả bàn giao và giới hạn của việc kiểm được ghi trong REPORT.md.

## 5. Những điểm cần lưu ý

Hash chỉ kiểm tính nhất quán bytes, không chứng minh nhãn đúng. Khi hai nguồn bất đồng lớp, phải nhìn vật để xác định bên sai. Guideline lấy theo job, vì metadata từng ảnh có thể ghi lệch. R-021 cần được xem lại hoặc train lại dù đã có v2, vì dữ liệu mới không tự thay model cũ.

Với dữ liệu dự án thật, tôi không tự mang lô ra USB, gửi email cá nhân, chia sẻ tài khoản hoặc đưa dữ liệu lên dịch vụ ngoài. Nếu guideline yêu cầu làm mờ mà ảnh còn rõ mặt, tôi giữ HOLD và báo người phụ trách; không tự sửa/xóa v1.

Các thủ tục còn lại gồm đối chiếu commit cá nhân của TV2/TV3, xác nhận tên repo, hạn/kênh nộp và lưu xác nhận nộp của nhóm. Tôi không xác nhận thay các thành viên về đóng góp hoặc giờ làm đề thực tế.

Tôi đã bổ sung [bảng đối chiếu từng yêu cầu](DOI_CHIEU_YEU_CAU.md) và [chuẩn bị vấn đáp](TV7_VAN_DAP.md), gồm giải thích đoạn so SHA-256, ca xem chéo và cách đếm 242 ảnh/1.656 box. Lượt chạy lại lô sạch 50 ảnh cho 0 lỗi luật và 0 ứng viên. Hồ sơ nội dung của TV7 được hoàn thiện độc lập từ các đầu ra đã có.

## 6. Bàn giao cho TV1

- Người bàn giao: Hoàng Kim Chi, TV7.
- Người nhận: Lê Quang Khải, TV1.
- Seed: 2412007; lô cha lab250_ebedbc794d29; v2 lab250_ebedbc794d29_v2.
- File: REPORT.md, TV7_REPORT.md, TV7_STATUS.md, r2412007/security.md và prompts.md theo quy định ghi nhật ký của đề.
- Kết quả đã đối chiếu: QC, review, trace, số ảnh/box/rework và checksum trong bộ bài trên main.
- Việc TV1 tiếp tục: đối chiếu hồ sơ cá nhân, xác nhận thủ tục lớp, nộp bài và lưu mã commit/thời điểm/xác nhận nộp.
