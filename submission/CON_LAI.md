# Các bước còn cần người thực hiện — T2412

Nhánh làm việc là `dev`. Ngày 20/11/2026 đã hoàn tất phần luyện tập, đủ 6 kết luận gán nhãn, kiểm hash và bảo mật. Bộ kiểm gốc hiện đạt 17 PASS, 0 FAIL.

## Bảo mật đã hoàn tất

Ngày 20/11/2026, TV1 — Lê Quang Khải xác nhận trực tiếp đã xem ảnh `000000004395.jpg` và vẫn thấy rõ mặt người. Đã ghi nguyên văn xác nhận vào `security.md`, chạy `python3 lab/tv1.py finish`, đóng gói lại và xuất bài. Bộ kiểm gốc đạt **17 PASS, 0 FAIL**; log ở `r2412007/check_handover.txt`.

V1 vẫn HOLD vì QC 6,4%. README v2 ghi Release theo việc tách lỗi detection của bài lab. Trong tình huống bảo mật mà guideline yêu cầu làm mờ, câu trả lời vẫn là HOLD và báo người phụ trách; chưa có thao tác làm mờ ảnh hay gửi thông báo ngoài thực tế.

## Danh tính và commit cá nhân

GitHub đã đối chiếu từ tác giả commit của TV1, TV2, TV3, TV4 và TV5. TV3 là truonghoangg25. TV1 đã xác nhận ngày 20/11/2026: TV6 longnguyen3204, TV7 Cheese1501; TEAM.md đã cập nhật đủ tài khoản của 7 người. TV6 dùng tên Nguyễn Nhân Thành Long theo bản tự khai trong CSV và thông tin TV1 đã gửi.

Mỗi thành viên cần ít nhất hai commit có nội dung thuộc phần mình thực hiện, mang tên và email của mình theo RULES. Nhánh TV2 hiện có một commit đóng góp gốc, nên cần rà lại mốc này. Kết quả review cá nhân có thể được chính thành viên bàn giao và commit bằng tài khoản của họ, kèm phần code hoặc kiểm thử họ thực hiện. Chỉ ghi nhận công việc thực tế.

## Đề ẩn

TV1 đã cung cấp thư mục Drive của lớp. Đã chọn ngẫu nhiên `de_an_07.zip` từ 20 đề, tải và chạy bằng công cụ hiện có. Bộ [de_an/](de_an/README.md) đã có đủ 7/7 kết luận của TV1 (6 confirmed, 1 rejected) và 1/1 kết quả hash intact. Đã gộp 14 lỗi (8 lỗi luật, 6 lỗi gán nhãn), xuất đủ bốn file bắt buộc và kiểm tính nhất quán. Trace có 2 ảnh tầng A, 9 tầng B. Không còn ca chờ người xem. Chưa có F1 đề ẩn vì không có đáp án. Thời gian đề ẩn là **20 phút** theo thông tin TV1 cung cấp ngày 20/11/2026, áp dụng thay thời lượng 40 phút trong tài liệu mẫu. Chưa được cung cấp giờ bắt đầu/kết thúc thực tế nên chưa xác minh thời lượng đã làm.

Giải nén theo hướng dẫn lớp để có `delivery/` ở gốc repo. Tạo thư mục `submission/de_an/` trước khi chép kết quả. Dùng validator và công cụ của nhóm.

```sh
python3 validator/validate.py delivery --out runs/de_an_work/rules.json --candidates runs/de_an_work/candidates.json
python3 lab/prepare_review.py delivery --workdir runs/de_an_work
python3 lab/split_review.py --workdir runs/de_an_work
python3 lab/review_server.py --run runs/de_an_work --delivery delivery --port 8766 --open
```

Cả nhóm trực tiếp xem ảnh theo bảng chia. Khi đủ review, chạy các lệnh sau và chép `candidates.json` cùng `review_log.csv` từ `runs/de_an_work/` sang `submission/de_an/`.

```sh
python3 scripts/merge_review.py --rules runs/de_an_work/rules.json --review runs/de_an_work/review_log.csv --out submission/de_an/errors.json
python3 scripts/trace_query.py delivery --out submission/de_an/trace.json
```

Bộ bài đề ẩn có đủ `errors.json`, `candidates.json`, `review_log.csv` và `trace.json`. Mọi lỗi gán nhãn được báo phải có bằng chứng xem ảnh. Giữ `delivery/`, `runs/`, `data_source/` và ZIP ngoài Git.

## Nộp bài

Phần luyện tập đã kiểm đạt, cập nhật báo cáo và nhật ký AI, xuất file vào `submission/`. Các thay đổi được commit và push vào `dev` theo quy ước nhóm. Hạn và kênh nộp lấy theo giảng viên. Theo TV1, dev dùng hoàn thiện/kiểm thử; khi nộp chính thức sẽ hoàn thiện main. Cần chốt tên repo, hạn/kênh nộp và lưu xác nhận nộp.

Điểm tự đo hiện tại trên phiên bản review đã gộp là F1 tổng ≈ 0,8, lỗi luật ≈ 1,0, lỗi gán nhãn ≈ 0,6 và truy vết các tầng ≈ 1,0. Chỉ sửa kết luận nhãn dựa trên việc người xem mở lại ảnh và nêu bằng chứng.

## Thứ tự chốt bài tiếp theo

1. **Đồng bộ dev mới:** lịch sử dev đã sửa danh tính TV1 thành kasdie. Thành viên có công việc chưa push giữ lại bản riêng trước khi đồng bộ; không merge lại dev cũ. Có thể clone nhánh dev vào thư mục mới để làm tiếp mà không xóa thư mục cũ.
2. **TV2:** bổ sung một đóng góp độc lập có nội dung; hai SHA hiện thấy là bản gốc và cherry-pick cùng một bản vá, không nên xem là hai việc khác nhau.
3. **TV3:** commit `0139ad5` đã được kiểm tra và tích hợp; cần thêm một commit có nội dung của chính thành viên để đủ hai. Không tạo commit rỗng để đủ số.
4. **TV7 — Cheese1501:** gửi các commit thực tế của mình. Chưa đối chiếu được tác giả commit trên lịch sử dev; TV1 đã làm bảo mật không thay cho yêu cầu đóng góp cá nhân của TV7.
5. **TV6 — longnguyen3204:** đã xác nhận tài khoản qua TV1. Ba commit gốc đã có, không cần tạo thêm chỉ để tăng số lượng. TV1/TV4/TV5 cũng đã đủ mốc số lượng.
6. **TV1:** đã xác nhận dev dùng hoàn thiện/kiểm thử; khi nộp chính thức sẽ hoàn thiện main. Thời gian đề ẩn là 20 phút. Còn xác nhận tên repo hiện tại có được chấp nhận và hạn/kênh nộp. Hiện chỉ push dev; chưa chuyển bài sang main hoặc đổi tên repo.
7. **Cả nhóm:** chuẩn bị vấn đáp ba nội dung ở RUBRIC: giải thích/sửa một đoạn validator, giải thích dòng review và một số liệu README v2. Dựa trên quan sát và đóng góp thật của từng người.
8. **TV1:** sau khi nhận đủ hồ sơ và commit cá nhân, nộp link đúng nhánh theo hướng dẫn lớp; lưu mã commit, thời điểm và xác nhận nộp. Chưa có bằng chứng nộp LMS trong phiên này.

Phần kỹ thuật hiện không có ca xem ảnh còn chờ: luyện tập đạt 17/17, đề 07 đủ bốn file và đã kiểm nhất quán. F1 đề ẩn chưa có vì chưa có đáp án của giảng viên; không tự suy ra điểm từ kiểm định dạng.
