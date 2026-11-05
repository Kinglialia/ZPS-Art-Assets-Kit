# UI QA theo rủi ro

Chọn kiểm theo đầu ra và rủi ro; không thay kiểm thị giác bằng tên file hay exit code. Ghi kiểm bắt buộc và kiểm bổ sung; không tự hạ kiểm bắt buộc khi thiếu công cụ.

| Rủi ro | Trường hợp đại diện | Công cụ |
|---|---|---|
| Tràn chữ | Chuỗi dài nhất, tiếng Việt có dấu, fallback, scale biên | Render với chuỗi thật |
| HUD khó đọc | Nền sáng/tối/bận, khung chuyển động | `preview.py compare` trên ảnh nền game |
| Layout vỡ | Tỷ lệ hẹp/rộng trong phạm vi, safe area | Render ở các tỷ lệ cam kết |
| Frame/asset lỗi | 9-slice ở min/max size, alpha trên nền sáng/tối, crop | `preview.py sheet`, `inspect_image.py` |
| Chạm nhầm | Hành động sát nhau, che khuất bởi tay | Đo vùng chạm sau scale |
| Nguồn không dùng được | Đổi chữ dài, thay icon, resize một component rồi xuất lại | Ghi kết quả xuất lại |
| Bàn giao thiếu | Người nhận dựng lại một component chỉ từ nguồn + đặc tả | Tự rà ghi rõ là tự rà |

Không bắt task icon đơn lẻ chạy test layout; ghi lý do N/A. Một mẫu đạt không xác nhận mọi kích thước hay trạng thái.

**Kết quả:** pass / fail / not_checked / not_applicable (có lý do). **Mức độ:** blocker / major / minor theo [mẫu review](../../.art-production-support/templates/review.md). Duyệt là trạng thái riêng.

**Hiệu lực:** mỗi kiểm ghi bản, môi trường, kích thước, dữ liệu, tiêu chí, bằng chứng. Đổi layout, token, font, asset hay thiết lập render → đánh dấu các kiểm bị ảnh hưởng là cần chạy lại; PASS cũ không là bằng chứng hiện tại.

Ba mức xác nhận tách riêng: đã kiểm thiết kế; đã đối chiếu trong Godot; đã thử trên thiết bị. Không dùng mức này để xác nhận mức khác. Phần Godot/thiết bị chưa làm ghi rõ ai làm tiếp, không tính là PASS.
