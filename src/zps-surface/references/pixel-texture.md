# Pixel texture trên model

Texel to và rõ, palette giới hạn, không làm mịn. Nhất quán quan trọng hơn chi tiết.

## Nguyên tắc

- **Texel density cố định cho cả game** (ví dụ N texel mỗi mét): mọi asset dùng cùng giá trị; đo bằng `inspect_model.py --texture-size` và chỉnh kích thước texture/UV cho khớp. Lệch density là lỗi dễ thấy nhất của style này.
- **Palette giới hạn** lấy từ style sheet; không thêm màu trung gian do resize hay blur.
- **Không resample mượt**: tạo ở đúng độ phân giải đích hoặc thu nhỏ bằng Nearest; không bilinear/Lanczos.
- **UV bám lưới texel**: cạnh UV island nằm trên ranh giới texel để pixel không bị cắt chéo; 3D Artist đặt UV theo lưới.
- **Filter Nearest, không mipmap** (hoặc mipmap có kiểm) trên material; xem tech profile.

## Quy trình

1. Chốt texel density, kích thước texture, palette với AD/tech profile.
2. Tạo nguồn ở độ phân giải đích. Nếu gen ảnh lớn rồi thu nhỏ: thu bằng Nearest, rồi lượng tử về palette (`palette_report.py` để kiểm màu ngoài palette), sửa tay cụm pixel lỗi.
3. Gắn lên model, `render_model.py` ở khoảng nhìn game; `preview.py sheet --nearest` cho texture phẳng.

## Tự kiểm

- Mọi asset cùng texel density (sai lệch nhỏ so với chuẩn).
- Không màu ngoài palette, không pixel mờ/viền nhòe.
- Cụm pixel đọc được hình ở khoảng nhìn game; không nhiễu pixel lẻ.

## Gotchas

- Ảnh gen thu nhỏ thường ra pixel nhiễu và màu trung gian: phải lượng tử palette và dọn cụm.
- Mipmap làm pixel nhòe ở xa: quyết định theo tech profile và kiểm ở khoảng xa nhất.
