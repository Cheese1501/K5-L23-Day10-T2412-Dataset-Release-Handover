# Đề ẩn 07 — đang chờ kết luận xem ảnh

TV1 yêu cầu chọn ngẫu nhiên một đề từ thư mục Drive của lớp. Đã liệt kê 20 ZIP và dùng `secrets.choice` chọn **de_an_07.zip** trước khi mở nội dung. Nguồn, thời điểm chọn và SHA-256 ZIP nằm trong [source.json](source.json). Chưa có thông tin giờ bắt đầu và hạn 40 phút chính thức của giảng viên trong phiên này.

## Kết quả đã làm

- Lô `lab250_3c55ac997ebf`, 250 ảnh theo manifest. Validator hiện có chạy thành công và báo 8 lỗi luật, 7 ca gán nhãn cần người xem.
- `errors.json` hiện chỉ có 8 lỗi luật; **chưa phải kết quả chốt sau review**. Không tự coi các ứng viên là lỗi đã xác nhận.
- `review_log.csv` có 7 dòng chờ, chưa có kết luận nào. `hash_review.csv` có một ca chờ TV5 kiểm ảnh.
- `trace.json` có 2 ảnh tier_a, 9 ảnh tier_b và notify A03, A04, Q01, Q03. Chạy công cụ TV6 và đối chiếu độc lập bằng công cụ TV1 cho cùng kết quả. Lớp đổi quy tắc là chair, job guideline cũ v1.2; các cảnh báo là scene_257 và scene_985.
- Đối chiếu 756 file trong delivery với ZIP: kích thước và CRC đều khớp. Không sửa delivery. ZIP và dữ liệu ảnh/mask/nhãn đề ẩn nằm ngoài Git.

## Chia việc xem ảnh

TV1 yêu cầu tự xem toàn bộ các ca còn chờ. Đã chuyển 7 ca gán nhãn (`img_0003`, `img_0018`, `img_0085`, `img_0193`, `img_0197`, `img_0235`, `img_0247`) và ca hash `img_0107` sang TV1. Tải lại bàn review, chọn TV1 để thấy đủ 8 ca. [Gợi ý và hướng dẫn cho từng ca](HUONG_DAN_TV1.md).

Bảng chia cho 7 người trước đó được giữ trong lịch sử Git và bản sao lưu cục bộ. Thành viên khác vẫn cần trực tiếp xem ảnh và đáp ứng yêu cầu cá nhân theo RULES.

Mỗi thành viên trực tiếp xem ảnh, chọn confirmed hoặc rejected và ghi rõ vật nhìn thấy, nguồn nhãn nào sai hoặc lý do không phải lỗi. Ghi chú ít nhất 20 ký tự, kèm tên người xem. Ảnh lệch hash cần mở kiểm nội dung, ghi intact hoặc damaged. Không sao chép kết luận của seed luyện tập sang đề này.

## Mở trên máy thành viên

Pull nhánh dev. Tải đúng [de_an_07.zip](https://drive.google.com/file/d/1mn27OCzswt57T-UWJfwEXCCdLhxvQqVK/view), giải nén để có `delivery/` ở gốc repo. Không chọn lại đề khác. Trên Windows có thể dùng `py -X utf8` thay `python3`.

Các lệnh sau dành cho máy mới chưa có thư mục làm việc. Máy TV1 đã được chuẩn bị và bàn review đang mở ở http://127.0.0.1:8766/.

```sh
python3 validator/validate.py delivery --out runs/de_an_work/rules.json --candidates runs/de_an_work/candidates.json
python3 lab/prepare_review.py delivery --workdir runs/de_an_work
python3 lab/split_review.py --workdir runs/de_an_work
python3 lab/review_server.py --run runs/de_an_work --delivery delivery --port 8766 --open
```

Chọn tên thành viên trên giao diện, xem và lưu kết quả. Khi làm ở máy khác, xuất đúng thư mục review đề ẩn; thay TV3 bằng mã của mình:

```sh
python3 lab/collect_reviews.py --run runs/de_an_work --delivery delivery --reviews submission/de_an/reviews --export TV3
```

TV4 nhận các file rồi kiểm trước khi gộp:

```sh
python3 lab/collect_reviews.py --run runs/de_an_work --delivery delivery --reviews submission/de_an/reviews --import --dry-run
python3 lab/collect_reviews.py --run runs/de_an_work --delivery delivery --reviews submission/de_an/reviews --import
```

Nếu có xung đột thì hỏi lại đúng người xem. Không nhập từ `submission/reviews/` vì đó là các kết luận của lô luyện tập khác.

## Chốt sau khi đủ kết luận

Khi 7 ca đã có kết luận và ghi chú hợp lệ, bấm **Gộp review** trên giao diện. Công cụ chỉ thêm các lỗi semantic được người xem confirmed; các ca rejected được giữ trong log làm bằng chứng. TV1 chép lại `errors.json`, `review_log.csv`, `candidates.json`, `trace.json` từ `runs/de_an_work/` sang thư mục này, cập nhật trạng thái trong README và source.json, kiểm tra rồi commit/push dev.

Không chạy `lab/tv1.py finish` hoặc `check_handover.py` cho đề ẩn: đó là quy trình bàn giao v2 của seed luyện tập. Đề ẩn yêu cầu bốn file errors, candidates, review_log và trace theo SUBMISSION.md. Không có bộ đáp án của đề ẩn trong gói đã nhận; chưa có F1 cho đề này.
