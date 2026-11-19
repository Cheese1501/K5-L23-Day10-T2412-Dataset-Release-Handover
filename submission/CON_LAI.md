# Các bước còn cần người thực hiện — T2412

Nhánh làm việc là `dev`. Ngày 19/11/2026 đã có đủ 6 kết luận gán nhãn và kết quả kiểm ảnh lệch hash. Gói v2 đã dựng, giữ trạng thái HOLD trong lúc chờ bảo mật. Bộ kiểm gốc hiện đạt 16 PASS, 1 FAIL.

## Hoàn tất bảo mật

TV7 hoặc một thành viên trực tiếp mở ảnh trong lô và xác nhận mã ảnh có khuôn mặt nhìn rõ. Có thể dùng bàn làm việc review hoặc mở ảnh gốc trong `runs/r2412007/delivery/images/`. Gửi mã ảnh, tên người xem và chi tiết thấy trên ảnh cho TV1.

Trong `runs/r2412007/security.md`, thay phần ví dụ còn dấu `<<...>>` bằng mã ảnh đã xác nhận và mô tả quan sát. Giữ kết luận tình huống là HOLD và báo người phụ trách. Nhóm đã có nội dung ca USB, năm tình huống và xử lý theo thẩm quyền.

Khi đã có xác nhận, chạy lệnh sau. Công cụ dựng lại v2, đóng gói, kiểm các mục còn lại, ghi release v2 có parent và xuất bài khi bộ kiểm đạt.

```sh
python3 lab/tv1.py finish
python3 scripts/check_handover.py --run runs/r2412007
```

Event HOLD v1 và event ghi nhận phiên bản bàn giao v2 có parent đã có. H14 đạt. README v2 đang HOLD. Khi bảo mật đầy đủ, lệnh finish kiểm lại và xuất gói cuối.

## Danh tính và commit cá nhân

GitHub đã đối chiếu từ tác giả commit của TV1, TV2, TV4 và TV5. TV3, TV6, TV7 cần gửi tên tài khoản để điền `submission/TEAM.md`. TV6 dùng tên Nguyễn Nhân Thành Long theo bản tự khai trong CSV và thông tin TV1 đã gửi.

Mỗi thành viên cần ít nhất hai commit có nội dung thuộc phần mình thực hiện, mang tên và email của mình theo RULES. Nhánh TV2 hiện có một commit đóng góp gốc, nên cần rà lại mốc này. Kết quả review cá nhân có thể được chính thành viên bàn giao và commit bằng tài khoản của họ, kèm phần code hoặc kiểm thử họ thực hiện. Chỉ ghi nhận công việc thực tế.

## Đề ẩn

Repo đề và fork hiện có 0 release công khai tại lượt kiểm ngày 19/11/2026. Nhận `de_an.zip` từ giảng viên, LMS hoặc kênh lớp và làm trong 40 phút theo GUIDE.

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

Khi phần luyện tập đạt bộ kiểm, cập nhật báo cáo và nhật ký AI, kiểm đủ file đã xuất, rồi commit và push vào `dev` theo quy ước nhóm. Hạn và kênh nộp lấy theo giảng viên. Nếu lớp chấm nhánh cụ thể hoặc tên repo cụ thể, TV1 xác nhận thông tin đó trước khi gửi link.

Điểm tự đo hiện tại trên phiên bản review đã gộp là F1 tổng ≈ 0,8, lỗi luật ≈ 1,0, lỗi gán nhãn ≈ 0,6 và truy vết các tầng ≈ 1,0. Chỉ sửa kết luận nhãn dựa trên việc người xem mở lại ảnh và nêu bằng chứng.
