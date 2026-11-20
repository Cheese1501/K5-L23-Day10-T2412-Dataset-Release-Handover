# TV1 — Thiết lập, nhận bàn giao và chốt bài T2412

TV1 là Lê Quang Khải, MSHV `2A202603237`. Lô luyện tập dùng seed `2412007`, release ID `lab250_ebedbc794d29`. Công việc từ lượt này ở nhánh `dev`. Các commit mới được push vào nhánh này theo yêu cầu của TV1.

## Tài liệu đề cần đọc

Repo có `GUIDE.md`. File này hướng dẫn đầy đủ Pha 0–6. Các tài liệu đã được đọc và đối chiếu khi thiết lập gồm `RULES.md`, `SUBMISSION.md`, `RUBRIC.md`, `CHECKPOINTS.md`, `docs/DELIVERY.md` và `scripts/README.md`. Bản gốc của các file và script vẫn theo repo đề ở commit `1ab6ab6630f45f762ce57ffdf9ef6fb105ccd908`.

## Lấy nhánh và mở môi trường

Trong clone của fork nhóm, chạy từng dòng sau. Trên máy TV1 hiện tại, fork được đặt tên remote `team`, nên thay `origin` trong lệnh fetch và pull bằng `team`.

```sh
git fetch origin
git switch dev
git pull --ff-only origin dev
python3 lab/tv1.py prepare
python3 lab/review_server.py --run runs/r2412007 --port 8765 --open
```

Khi clone lần đầu, dùng URL fork trong `submission/TEAM.md` và vào thư mục repo trước. Trên macOS có thể nhấp đúp `lab/MO_LAB_TV1.command` để chuẩn bị và mở công cụ. Trên Windows dùng `py` thay `python3`. Máy cần Python từ 3.10, các công cụ lab dùng thư viện chuẩn.

Lệnh `prepare` tải dữ liệu và tạo lô khi máy chưa có, tạo các output còn thiếu, chuẩn bị trang xem ảnh và giữ các kết luận đã lưu. Nếu lô đã tồn tại, nó tiếp tục từ các file hiện có. Khi TV2 hoặc TV3 sửa validator, chạy lại lệnh validator theo GUIDE rồi đối chiếu hàng đợi với TV4.

## Kiểm tiến độ trên máy tích hợp

```sh
python3 lab/tv1.py status
python3 lab/tv1.py status --json-out runs/tv1_checks/readiness.json
```

QC trên màn hình tính từ lỗi luật và các kết luận `confirmed` đã lưu. Sau khi tích hợp đủ review ngày 19/11/2026, có 16 target trên 250 ảnh, tương ứng 6,4%, nên HOLD v1. Điểm tự đo mới nhất có trong `submission/r2412007/report.md`. [Phần còn cần người thực hiện](../submission/CON_LAI.md)

## Nhận kết quả từ thành viên

Mỗi ca gán nhãn gửi theo CSV có cột `image,type,verdict,note`. Trong note cần tên người xem và chi tiết họ thấy trên ảnh. Giữ mã ảnh ở dạng văn bản. TV4 có thể gom các file vào một thư mục trên máy tích hợp, sau đó TV1 dùng lệnh nhận bên dưới với các đường dẫn thực tế.

```sh
python3 lab/tv1.py import-reviews --source submission/reviews/TV1.csv
```

Lệnh này đọc và kiểm trước khi ghi. Nhập lại cùng một dòng sẽ giữ nguyên kết quả. Nếu hai bản có kết luận khác nhau cho cùng ca, công cụ báo cần TV4 chốt. CSV cũ được lưu trong `runs/r2412007/review_backups/`.

TV5 gửi `hash_review.csv` có cột `image,status,reviewer,note`. `status` là `intact` hoặc `damaged`, `reviewer` ghi rõ tên người trực tiếp mở ảnh. Nhận bằng lệnh sau, thay đường dẫn ví dụ bằng file TV5 gửi.

```sh
python3 lab/tv1.py import-hashes --source incoming/hash_review.csv
```

Sau khi nhận các dòng thật, cập nhật danh sách lỗi đã biết bằng script gộp gốc.

```sh
python3 lab/tv1.py merge-known
```

Chức năng này chỉ gộp lỗi luật và các dòng đã `confirmed`, giữ nguyên các ca đang chờ xem. Tránh dùng điểm số để dò từng ca. Chạy tự đo sau khi nhóm chốt một phiên bản đầy đủ theo RULES.

## Truy vết và bảo mật

`trace.json` hiện đã được đối chiếu độc lập từ ticket, nhãn detection và guideline của job. Ticket lô nhóm nói về lớp `cup` và các cảnh `scene_569`, `scene_839`. Kết quả có 4 ảnh tầng A, 3 ảnh tầng B và `notify` là `A05`, `Q02`. TV6 tiếp tục giải thích và kiểm phần của mình khi vấn đáp.

`security.md` đã có bản soạn thảo. TV7 cần ghi tên một ảnh trong lô mà người trong nhóm đã trực tiếp xem và xác nhận thấy rõ khuôn mặt. Kết luận tình huống theo đề là HOLD và báo người phụ trách. Sau khi nhận bản của TV7, chép về `runs/r2412007/security.md` trên máy tích hợp rồi chạy status.

## Chốt gói v2 khi đủ đầu vào

```sh
python3 lab/tv1.py finish
```

Lệnh này thực hiện chuỗi công việc sau.

1. Kiểm đủ các kết luận xem ảnh, kết quả kiểm ảnh lệch hash, trace và nội dung bảo mật đã điền.
2. Gộp bằng `scripts/merge_review.py`, đối chiếu errors với log và ghi quyết định v1 trong lineage nếu chưa có.
3. Dựng v2 bằng công cụ của nhóm, đóng gói bằng `scripts/pack_release.py` rồi kiểm bằng `scripts/check_handover.py` gốc.
4. Nếu chỉ còn H14 do thiếu event release và v1 thuộc diện HOLD, ghi event v2 có parent, kiểm lại toàn bộ.
5. Khi bộ kiểm đạt, xuất thư mục v2 và các file bài nộp theo logic `scripts/export_submission.py`.

Nếu còn đầu vào từ người xem, lệnh in rõ danh sách rồi dừng trước bước dựng hoặc release v2. Lượt chạy lại lưu bản v2 hiện có vào `tv1_backups/` trước khi dựng lại. Event quyết định và release được kiểm để tránh ghi trùng. Trong thời gian đóng gói, biểu mẫu lưu ảnh chờ lượt hoàn thiện kết thúc để bộ gói dùng cùng đầu vào.

Sau khi chốt đầy đủ, tự đo một lần bằng chế độ học viên và cập nhật báo cáo.

```sh
python3 scripts/score_findings.py --run runs/r2412007
python3 scripts/check_handover.py --run runs/r2412007
git status --short
```

TV1 đối chiếu số liệu báo cáo với README v2 và file thật. Commit các file trong `submission/` cùng code cần nộp, rồi push nhánh `dev`. Giữ `runs/`, `data_source/`, ZIP và secret ngoài Git.

## Trạng thái bàn giao và việc còn lại

| Người | Việc còn cần | File nhận |
|---|---|---|
| TV2 — Nguyễn Đức Anh | Đã tích hợp hai hàm và review ảnh. Rà mốc hai commit có nội dung. | Code và CSV review đã có |
| TV3 — Hoàng Quang Trường | Đã có review và commit code 0139ad5; GitHub truonghoangg25. Cần thêm một commit có nội dung. | Code, 20 test và review đã tích hợp |
| TV4 — Dương Quốc Huy | Đã tổng hợp đủ 6/6 ca và hỗ trợ công cụ. | `review_log.csv` đã tích hợp |
| TV5 — Đặng Trung Hiếu | Đã có code dựng v2, review ảnh và xác nhận hash intact. | V2 đã đóng gói và kiểm đạt 17/17 |
| TV6 — Nguyễn Nhân Thành Long | Đã có review và trace, H16 đạt. Chờ xác nhận GitHub. | CSV và trace đã tích hợp |
| TV7 — Hoàng Kim Chi | Đã xem chéo ca TV4 theo log. TV1 đã bổ sung xác nhận khuôn mặt và hoàn tất bảo mật. Chờ GitHub. | `security.md` đã kiểm đạt H17 |
| Cả nhóm | Cung cấp GitHub để điền TEAM, có ít nhất hai commit có nội dung dưới tên và email của mình. | Thông tin tài khoản và lịch sử Git |
| Giảng viên hoặc coach | Đã có đề 07 từ link Drive TV1 gửi. Cần xác nhận thời gian, tên repo, nhánh chấm và kênh/hạn nộp. | Thông báo lớp |

AI đã chuẩn bị code, lệnh và phần kiểm tra tự động. Mọi kết luận ảnh có tên thành viên lấy từ thông tin người đó trực tiếp cung cấp.

## Đề ẩn và việc nộp

Khi nhận đề, làm 40 phút theo Pha 6 trong GUIDE. Dùng validator và công cụ xem ảnh của nhóm theo quy định của lớp. Bốn file đầu ra nằm ở `submission/de_an/`. Ghi rõ ngày giờ, mã commit và đường dẫn đã nộp sau khi hoàn thành.

Qua kiểm tra GitHub ngày 19/11/2026, cả repo đề và fork đều có 0 release công khai. Nhóm cần theo dõi kênh giảng viên công bố.

## Bản submission hiện có

`submission/r2412007/` đã xuất các file thật bằng script gốc và đạt 17 PASS, 0 FAIL ngày 20/11/2026. Có errors, candidates, đủ review/hash, trace, bảo mật với xác nhận ảnh 000000004395 của TV1 và gói v2 có 242 ảnh, 1.656 nhãn. Log kiểm nằm ở `submission/r2412007/check_handover.txt`. V1 vẫn HOLD; README v2 ghi Release theo xử lý lỗi detection của bài lab. Phần bảo mật ghi HOLD và báo người phụ trách trong tình huống guideline yêu cầu làm mờ.
