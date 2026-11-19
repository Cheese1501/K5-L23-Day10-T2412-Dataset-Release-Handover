Release: lab250_ebedbc794d29_v2
Parent: lab250_ebedbc794d29
Số ảnh: 242
Số nhãn: 1656
Guideline: v1.2 (J01, J02, J03), v1.3 (J04, J05, J06, J07, J08, J09, J10)
QC v1: 16/250 = 6.4%
Kết luận v1: Hold — vượt ngưỡng 2%
Kết luận v2: Release — tách 8 ảnh lỗi detection/ảnh hỏng sang rework_queue.csv, sửa 4 mục hash/guideline/split ngay trong v2 (chi tiết ở Ghi chú)
Ghi chú:
  - Hash 000000004765: mở ảnh kiểm thấy còn nguyên (hash_review.csv) (hash cũ là hash của 000000006771.jpg, manifest v1 ghi nhầm); giữ ảnh, manifest.csv v2 ghi sha256 tính lại từ file thật.
  - Guideline 000000001353: metadata v1 ghi v1.3, job J01 trong jobs.csv là v1.2; truyvet.csv ghi theo job vì ảnh được gán theo guideline của job.
  - Guideline 000000007574: metadata v1 ghi v1.2, job J04 trong jobs.csv là v1.3; truyvet.csv ghi theo job vì ảnh được gán theo guideline của job.
  - Split scene_701: đưa cả cảnh về train theo đa số ảnh của cảnh; đổi 000000017436 (val → train). Lý do: ảnh cùng cảnh nằm ở hai split làm rò dữ liệu.
  - Rework: tách 8 ảnh khỏi v2 (bbox_drift 1, bbox_out_of_bounds 1, class_swap 2, duplicate_box 2, invalid_class 2); giao lại A01/Q01: 1 ảnh, A01/Q03: 2 ảnh, A02/Q03: 2 ảnh, A05/Q02: 3 ảnh (người gán/người kiểm theo jobs.csv), xem rework_queue.csv.
  - Báo team panoptic (ảnh ở lại v2 vì nhãn detection không sai): 000000002473 (thing_overlap); 000000006012 (instance_merge); 000000018491 (category_swap); 000000023023 (category_swap).
