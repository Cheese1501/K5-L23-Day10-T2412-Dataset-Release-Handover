# Chuẩn bị vấn đáp — Hoàng Kim Chi — TV7

Nhóm T2412 · MSHV 2A202603172 · Seed 2412007.

## 1. Giải thích một đoạn validator

Tôi chọn phần tính và so SHA-256 trong hàm `validate` ở [validator/validate.py](../validator/validate.py). Mỗi ảnh có đường dẫn image, label, mask trong manifest. Chương trình kiểm file ảnh có tồn tại không, rồi đọc bytes của các file đang tồn tại và so hash thật với trường tương ứng trong manifest.

```python
if any(hashlib.sha256(path.read_bytes()).hexdigest() != row[f"{kind}_sha256"]
       for kind, path in paths.items() if path.is_file()):
    errors.add(("wrong_hash", name))
```

`read_bytes()` đọc nội dung thực tế, nên không thể thay bằng kiểm chuỗi hash có 64 ký tự. File thiếu được báo riêng bằng missing_image. Tập `errors` chứa cặp `(type, target)`, giúp tránh lặp cùng một loại lỗi trên cùng ảnh. Validator chỉ lấy dữ liệu từ thư mục delivery truyền vào; hàm `Delivery.file` kiểm đường dẫn sau resolve không được ra ngoài thư mục đó.

Nếu yêu cầu đổi thành chỉ kiểm hash ảnh, tôi giới hạn phép so ở `paths["image"]` với `row["image_sha256"]`, vẫn giữ bước báo file ảnh thiếu. Nếu cần biết chính xác file nào lệch, có thể lưu thêm chi tiết phục vụ review, nhưng đầu ra chấm vẫn giữ cặp wrong_hash/target đúng giao diện. Tôi không thay hash trong v1 để làm biến mất lỗi.

Hash khớp chỉ nói bytes khớp manifest, không nói lớp/box đúng. Ảnh hash lệch phải được người xem mở kiểm nội dung trước khi quyết định giữ với hash mới trong v2 hay chuyển rework.

## 2. Giải thích ca xem chéo của tôi

Ca **000000023023** có tên tôi trong [review_log.csv](r2412007/review_log.csv) do TV4 tổng hợp. Ghi chú gốc của tôi là “Vật bị bị nhầm class”. TV4 ghi chi tiết: vật ở giữa ảnh là túi xách; detection ghi handbag, panoptic ghi suitcase. Kết luận cuối là **category_swap/confirmed**.

category_swap nghĩa là nguồn panoptic ghi sai lớp. class_swap nghĩa là nguồn detection ghi sai lớp. Chỉ thấy hai nguồn khác nhau chưa đủ quyết định bên sai; phải đối chiếu vật trong ảnh. Phần chi tiết handbag/suitcase trong hồ sơ là ghi nhận của TV4, không phải quan sát mới tôi tự bổ sung.

Khi vấn đáp, tôi mở đúng ảnh và vùng đang được đối chiếu để giải thích theo những gì mình thực sự nhìn thấy. Tôi không dùng điểm F1 để chọn lại class_swap hay category_swap.

## 3. Giải thích các số trong README v2

Lô v1 có 250 ảnh. errors.json cuối có 16 target lỗi, mỗi target tính một lần và scene_leak tính một ca theo quy ước. Vì vậy QC v1 là **16/250 × 100 = 6,4%**, vượt ngưỡng 2%, nên HOLD.

Không phải cả 16 lỗi đều làm mất ảnh khỏi v2. Lỗi chỉ ở panoptic được giữ vì sản phẩm bàn giao là detection; hash/guideline/split được xử lý trong v2 nếu đủ điều kiện. Có **8 ảnh khác nhau** thuộc diện rework, nên v2 có **250 − 8 = 242 ảnh**. Các ảnh này phải có trong rework_queue.csv và không còn trong images v2.

**1.656 box** là tổng số dòng nhãn không rỗng trong labels của v2, không phải số ảnh. Tổng này phải bằng tổng cột count của các lớp, không cộng thêm dòng TOTAL lần thứ hai. Ví dụ label_summary.csv ghi person 556 và car 51; tổng mọi lớp là 1.656.

Nguồn đối chiếu: [README.txt](r2412007/handover/lab250_ebedbc794d29_v2/README.txt), [label_summary.csv](r2412007/handover/lab250_ebedbc794d29_v2/label_summary.csv), [rework_queue.csv](r2412007/handover/lab250_ebedbc794d29_v2/rework_queue.csv).

## 4. Bảo mật và truy vết

Tôi giữ dữ liệu dự án trong hệ thống được phép, không chép USB hay gửi email cá nhân để làm tiếp. Chia sẻ tài khoản làm mất khả năng truy vết người thao tác; phải xin cấp quyền riêng.

Ví dụ khuôn mặt là 000000004395.jpg, job J02, guideline v1.2, người gán A05, người kiểm Q02. Người trực tiếp xác nhận ảnh này là TV1. Nếu guideline yêu cầu làm mờ, tôi chọn HOLD và báo người phụ trách; không tự làm mờ/xóa v1 vì sẽ thay dữ liệu và bằng chứng. Hồ sơ không khẳng định đã thực hiện thông báo hoặc làm mờ ngoài thực tế.

Truy vết dùng guideline theo job, không theo metadata ảnh có thể bị sai. Tầng A thuộc cảnh được ticket nêu; tầng B ở cảnh khác, cùng điều kiện guideline cũ và có box của lớp đổi quy tắc. Notify lấy người gán/kiểm của cả hai tầng. Lô nhóm có 4/3 ảnh hai tầng và notify A05/Q02.

R-021 đã train trên v1, nên phát hành v2 không tự sửa trọng số model cũ. Nhóm phải xem lại tác động hoặc train lại trên dữ liệu phù hợp.
