# Asset mẫu của bộ

Dùng chung cho Asset 2D, UI Art và 2D Review. Asset mẫu là asset **đã được AD hoặc user duyệt**, làm thước đo đồng bộ cho các asset còn lại cùng bộ: góc nhìn, độ dày nét, mức chi tiết, hướng sáng, scale, khoảng đệm. Với UI, mẫu là hướng visual hoặc màn hình đã được chọn.

## Khi chưa có mẫu

- **Làm luôn cả bộ** rồi trình cả bộ để duyệt một lần. Chỉ làm mẫu trước khi user yêu cầu.
- **Asset đầu tiên hoặc asset lẻ:** so với brief và style sheet; ghi đồng bộ bộ là `not_checked`.
- **Cả bộ làm cùng lúc:** đặt tất cả cạnh nhau cùng kích thước hiển thị (`preview.py compare` hoặc `sheet`) và kiểm đồng bộ **trong bộ**.

## Khi đã có mẫu

So từng asset với mẫu ở cùng kích thước và nền. Không so với concept hay reference cảnh thay cho mẫu.

## Ghi mẫu sau khi duyệt

Khi AD hoặc user duyệt một asset hoặc cả bộ, ghi asset mẫu (cả bộ được duyệt thì chọn một asset tiêu biểu). Lưu ở phía project, không bao giờ trong thư mục skill:

| Tình huống | Ghi ở đâu |
|---|---|
| Project có style sheet hoặc tài liệu Art Style | Mục Ghi chú sản xuất của style sheet |
| Project chưa có style sheet | File `_mau.md` đặt cạnh bộ asset |
| Gọi global, không có project | Ghi trong kết quả giao; lần sau user gửi lại ảnh mẫu |

Nội dung ghi: tên bộ, file mẫu và version, người duyệt, ngày, phạm vi (ví dụ "mẫu cho nét và mức chi tiết, chưa chốt palette").

Trước khi làm thêm hoặc review một bộ, tìm mẫu theo đúng thứ tự trong bảng trên.
