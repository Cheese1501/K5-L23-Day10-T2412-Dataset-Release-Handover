# Báo cáo nhóm T2412

Seed luyện tập: **2412007**. Lô v1: `lab250_ebedbc794d29`. Lô bàn giao: `lab250_ebedbc794d29_v2`. Nhóm tập hợp bài làm trên nhánh **main**, ngày 20/11/2026.

## 1. Số liệu luyện tập

| Lô | Lỗi luật | Ứng viên | F1 luật | F1 gán nhãn | F1 tổng |
|---|---:|---:|---:|---:|---:|
| Seed 2412007, sau review | 10 | 6 | ≈ 1,0 | ≈ 0,6 | ≈ 0,8 |
| Seed 11, chỉ báo lỗi luật | 13 | 3 | ≈ 1,0 | Chưa đo sau review | ≈ 0,8 |
| Seed 22, chỉ báo lỗi luật | 9 | 6 | ≈ 1,0 | Chưa đo sau review | ≈ 0,7 |
| Lô sạch, 50 ảnh khác bộ luyện tập | 0 | 0 | Không ghi điểm | Không có review | Không ghi điểm |

F1 là số làm tròn từ chế độ học viên; báo cáo sau review ở [r2412007/report.md](r2412007/report.md). Số ứng viên seed 22 được ghi ở lượt kiểm hồi quy, tách với lần tự đo baseline chỉ báo lỗi luật.

Nhóm ghép lớp qua tên, chuyển box sang pixel rồi so IoU và phần pixel mask nằm trong box. Với bất đồng lớp, ngưỡng hiện dùng gồm IoU từ 0,56, phủ mask từ 78% và chênh điểm ghép ít nhất 0,08 so với cặp cạnh tranh. Segment thiếu box phải có ít nhất 170 pixel và hai chiều bbox từ 10 pixel. Nhóm chọn ngưỡng để hàng đợi có thể xem hết, kiểm trên lô sạch và seed độc lập, không dùng đáp án riêng để chỉnh ngưỡng. Lượt chạy lại validator hiện tại trên lô sạch 50 ảnh ngày 20/11/2026 tiếp tục cho 0 lỗi luật và 0 ứng viên.

Lô luyện tập có **6 confirmed, 0 rejected**; errors cuối gồm **10 lỗi luật + 6 lỗi gán nhãn = 16 target**. TV5 mở ảnh lệch hash 000000004765 và xác nhận intact. Bằng chứng ở [review_log.csv](r2412007/review_log.csv) và [hash_review.csv](r2412007/hash_review.csv).

V2 có **242 ảnh, 1.656 box và 8 ảnh rework**. Nhóm giữ ảnh chỉ sai panoptic; chuyển ảnh lỗi detection sang rework đúng người theo jobs.csv; ghi hash thật, guideline theo job và split thống nhất theo cảnh. Chi tiết ở [README v2](r2412007/handover/lab250_ebedbc794d29_v2/README.txt). Kiểm lại bằng bộ kiểm gốc trên bản sao kiểm chứng ngày 20/11/2026 đạt **17 PASS, 0 FAIL**; 50 kiểm thử code nhóm đạt. PASS xác nhận các yêu cầu được bộ kiểm kiểm tra, không bảo đảm mọi kết luận nhãn đều đúng.

Đề ẩn nhóm làm là **đề 07**, lô lab250_3c55ac997ebf: 8 lỗi luật, 7 ứng viên, review 6 confirmed/1 rejected; errors cuối 14 lỗi. Trace có 2 ảnh tầng A, 9 tầng B và 4 mã người. Bốn file bắt buộc ở [de_an/](de_an/). Chưa có F1 đề ẩn vì nhóm chưa nhận đáp án. TV1 xác nhận thời lượng lớp áp dụng là 20 phút; hồ sơ chưa có giờ bắt đầu/kết thúc để đối chiếu thời lượng thực tế.

## 2. Vì sao báo hết ứng viên làm F1 giảm?

Ứng viên là tín hiệu bất đồng giữa hai nguồn nhãn, có thể do che khuất, crowd hoặc cách gán tự nhiên khác nhau. Báo mọi ứng viên thành lỗi có thể tăng false positive, giảm precision và kéo F1 xuống. Báo cả class_swap và category_swap cho cùng một bất đồng còn có thể thêm một loại lỗi sai.

Lô sạch có 0 ứng viên với ngưỡng hiện tại. Lô luyện tập có 6 confirmed nhưng F1 gán nhãn chỉ ≈ 0,6; số confirmed không chứng minh mọi phân loại đều đúng. Ở đề 07, nhóm loại img_0247 khỏi errors sau khi người xem rejected vì box detection ôm sát vật, khung panoptic bị dư. Nhóm chỉ gộp confirmed có ghi chú quan sát, không sửa từng ca bằng cách dò điểm.

## 3. Quyết định và lineage

QC v1 là **16/250 = 6,4%**, vượt ngưỡng 2%, nên **HOLD**. Mỗi target tính một lần; scene_leak tính một ca theo quy ước bài. [Lineage](lineage.jsonl) giữ train R-021, HOLD v1 và release v2 có đúng parent. HOLD được ghi từ lúc đã biết ít nhất 10 lỗi luật; QC cuối tăng lên 16 lỗi sau review.

R-021 đã học từ v1. Thay dataset không tự thay trọng số model, nên cần xem lại đánh giá hoặc train lại run bị ảnh hưởng. Impact là `R-021: affected=True action=review_or_retrain`.

V2 được Release theo xử lý lỗi detection của bài lab. Trong tình huống bảo mật mà guideline yêu cầu làm mờ khuôn mặt, nhóm vẫn phải HOLD và báo người phụ trách; đạt kiểm bàn giao không thay cho phê duyệt bảo mật.

## 4. Hash chứng minh gì, không chứng minh gì?

SHA-256 đối chiếu bytes của file với manifest, giúp phát hiện file thay đổi. Hash khớp không chứng minh lớp/box đúng, dữ liệu được phép sử dụng hay nguồn manifest đáng tin.

Ảnh 000000004765 được TV5 xác nhận nguyên vẹn nên giữ, manifest v2 ghi hash thật. Nhóm không sửa v1 hoặc sửa tay nhãn đã giao. [Checksum ZIP](r2412007/handover/lab250_ebedbc794d29_v2.sha256) được tính theo đúng các file bàn giao trên main; ZIP giữ ngoài Git. Quy tắc .gitattributes giữ nguyên bytes thư mục bàn giao khi checkout trên các hệ điều hành.

## 5. Truy vết

Nhóm đọc ticket/changelog để xác định cảnh được báo, lớp đổi quy tắc và guideline cũ. Ảnh đủ điều kiện phải thuộc job dùng guideline cũ và có ít nhất một box detection của lớp đổi quy tắc. Tầng A gồm ảnh trong cảnh ticket nêu; tầng B gồm ảnh ở cảnh khác cùng điều kiện. Notify là tập người gán/kiểm của các job liên quan.

Guideline lấy theo jobs.csv vì phiên bản ở metadata từng ảnh có thể chính là lỗi guideline_mismatch. Với seed 2412007, [trace.json](r2412007/trace.json) có **4 ảnh tầng A, 3 ảnh tầng B, notify A05 và Q02**; F1 làm tròn từng khóa đều ≈ 1,0. Hai công cụ truy vết cho cùng kết quả.

## 6. Bug hoặc điểm chưa rõ trong lab

Trên Windows, run_lab.py gọi tiến trình con không kế thừa tùy chọn -X utf8 của tiến trình cha. Nhóm gặp UnicodeEncodeError khi in thông báo sau khi đã tạo delivery. Cách chạy phù hợp là đặt `$env:PYTHONUTF8 = '1'`; không sửa script gốc để vượt kiểm.

CRLF/LF của manifest.json và metadata.json làm ID lô tạo trên Windows khác máy tích hợp dù cùng seed. Nhóm giữ nguyên v1 local, dùng bản sao riêng để kiểm tương thích lô LF. Checksum ZIP được tính lại theo bytes lưu trong Git; ảnh/nhãn và các giá trị hash trong manifest không đổi.

Đội hình 7 người đã được TV1 xác nhận được chấp thuận; TEAM đủ tên, MSHV và GitHub. Phần kỹ thuật TV1–TV6 đã tập hợp về main. TV2 cần đối chiếu yêu cầu hai commit có nội dung khác nhau: bản gốc và cherry-pick cùng thay đổi không tính là hai đóng góp. TV3 hiện có một commit gốc được tích hợp. Nhóm còn cần xác nhận tên repo theo quy ước lớp, hạn/kênh nộp, giờ làm đề thực tế và lưu bằng chứng nộp.
