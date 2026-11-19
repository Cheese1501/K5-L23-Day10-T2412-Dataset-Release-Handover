# TV1 xem toàn bộ đề 07

Theo yêu cầu của TV1, đã chuyển cả 8 ca sang TV1: 7 ca đối chiếu nhãn và 1 ca kiểm ảnh lệch hash. Bảng chia cũ được giữ trong lịch sử Git và sao lưu tại review_backups của thư mục làm việc. Hiện đã nhận đủ 7/7 ca nhãn và 1/1 ca hash từ TV1; đã gộp 14 lỗi, gồm 8 lỗi luật và 6 lỗi semantic. Ca img_0197 được cập nhật theo xác nhận bổ sung của TV1 rằng chỉ thấy khung xanh panoptic quanh con chó.

## Cách làm

1. Mở http://127.0.0.1:8766/, tải lại trang và chọn TV1 — Lê Quang Khải.
2. Làm 7 ca gán nhãn và ca hash trong phần việc của mình. Bật/tắt mask để nhìn vật thật; box detection màu cam, box bao segment panoptic màu xanh đứt.
3. Chọn loại lỗi và confirmed/rejected theo điều mình trực tiếp thấy. Với hash chọn intact/damaged. Ghi mô tả ít nhất 20 ký tự, xác nhận đã xem rồi bấm lưu.
4. Khi đủ 7/7 review và 1/1 hash, báo lại TV1/agent để gộp, kiểm và xuất bản cuối. Không dùng nút kiểm bàn giao v2 cho đề ẩn.

## Gợi ý có điều kiện từ nhãn đầu vào

Các thông tin dưới đây lấy từ candidates.json, không phải kết luận xem ảnh hay đáp án.

| Ảnh | Dữ liệu đang bất đồng | Cách quyết định sau khi xem |
|---|---|---|
| img_0003 | Detection cake; panoptic donut | Nếu vật trong vùng là donut: class_swap. Nếu là cake: category_swap. |
| img_0018 | Detection person; panoptic toilet | Nếu vùng đó là người: category_swap. Nếu là toilet: class_swap. |
| img_0085 | Detection donut; panoptic cake | Nếu vật là donut: category_swap. Nếu là cake: class_swap. |
| img_0193 | Detection bird; panoptic kite | Nếu là chim: category_swap. Nếu là diều: class_swap. Vùng nhỏ, cần phóng to. |
| img_0197 | Panoptic dog; công cụ chưa tìm thấy box detection tương ứng | Nếu thấy chó thật và không có box detection bao quanh con chó đó: missing_box. Nếu đã có box hoặc segment đang gán sai vật, không xác nhận missing_box chỉ theo gợi ý máy; ghi rõ điều thấy. |
| img_0235 | Detection dog; panoptic cat | Nếu vật là mèo: class_swap. Nếu là chó: category_swap. |
| img_0247 | Hai nguồn cùng carrot; box detection chỉ phủ khoảng 83% pixel segment | Nếu box cắt mất phần củ cà rốt cần bao: bbox_drift. Nếu phần chênh do segment lẫn vật khác, bị che hoặc khác phạm vi hợp lý, ghi lý do rejected. |
| img_0107 | SHA-256 ảnh không khớp manifest; TV1 đã xác nhận intact | Mở ảnh toàn khung và phóng to. Nếu mở được, không thấy hỏng: intact, mô tả quan sát. Nếu hỏng/mất phần dữ liệu: damaged, mô tả vị trí. Hash lệch tự nó không chứng minh ảnh hỏng. |

class_swap là detection sai lớp; category_swap là panoptic sai lớp. Chọn confirmed khi xác nhận lỗi đang báo. Chọn rejected nếu không thấy lỗi đó và giải thích vì sao. Nếu không phân biệt được vật, để ca chờ và mô tả điều chưa rõ; không chọn đại một loại.

Mẫu ghi chú theo quan sát thực tế: “Vật trong vùng là …; detection ghi …, panoptic ghi …; nguồn … sai.” Không sao chép mẫu thành kết luận nếu chưa xem được vật.

## Những việc còn lại ngoài 8 ca

- Đã gộp kết quả, xuất đủ bốn file bắt buộc, kiểm tính nhất quán và cập nhật báo cáo. Kết quả xem ảnh không có ca nào còn chờ.
- TV2/TV3/TV7 cần rà yêu cầu commit cá nhân; TV3/TV6/TV7 bổ sung tài khoản GitHub. TV1 không thể thay các thành viên thực hiện yêu cầu cá nhân và vấn đáp. Mỗi thành viên vẫn cần trực tiếp xem ảnh theo RULES.
- TV1 xác nhận nhánh được chấm, tên repo theo quy định lớp và nộp đúng kênh/hạn. Repo hiện mặc định main, bài làm nằm trên dev.
- Theo SUBMISSION.md và GUIDE.md, kết quả đề ẩn phải được commit/push trong repo public. Nhánh làm việc theo yêu cầu TV1 là dev; không đưa ZIP hoặc delivery vào Git.
