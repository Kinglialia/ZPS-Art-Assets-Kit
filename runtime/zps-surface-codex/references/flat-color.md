# Flat color — palette atlas, gradient atlas, vertex color

Bề mặt là màu theo vùng vật liệu; hình khối, sáng tối và chiều sâu do mesh, ánh sáng engine và sương/khí quyển. Chất lượng nằm ở **chọn màu và phân vùng**, không ở chi tiết vẽ.

## Chọn biến thể

| Biến thể | Dùng khi | Lưu ý |
|---|---|---|
| Palette atlas | Nhiều asset chung palette; muốn đổi màu bằng thay atlas | Một texture nhỏ chung cho cả bộ, ít material → ít draw call |
| Gradient atlas | Cần chuyển sáng/tối có chủ đích trong một vùng (tán cây, đá, tường) | Hướng gradient do UV; giữ cùng hướng trong bộ |
| Vertex color | Không muốn texture; mesh có đủ đỉnh ở ranh giới màu | Godot: bật Vertex Color → Use as Albedo (+ Is sRGB); gán màu là việc của 3D Artist hoặc DCC |

## Lập atlas

1. Lấy palette từ style sheet (đo bằng `palette_report.py`/`--profile` trên reference cùng loại); mỗi vật liệu một ô, đặt tên ô theo vật liệu.
2. Ô đủ lớn để mipmap không lem sang ô bên: chừa padding giữa ô, kích thước atlas theo tech profile. Kiểm ở khoảng nhìn xa nhất.
3. Gradient: ô kéo dài theo một trục; ghi trục nào là "trên/dưới" để 3D Artist đặt UV đúng.
4. Biến thể mùa/skin: atlas cùng bố cục ô, chỉ đổi màu; không vẽ lại.

## Gán UV vào ô

UV của mỗi vùng thu gọn trong ô màu của nó (gần như một điểm với ô phẳng; trải theo trục với ô gradient). Không cần UV trải đều, không cần tránh chồng giữa các mặt cùng màu. Gán UV là việc của 3D Artist; artist giao atlas + bảng ô.

## Tự kiểm

- `render_model.py` nhiều góc dưới ánh sáng game: vùng vật liệu đọc rõ ở kích thước màn hình; màu không lệch giữa mặt sáng và mặt tối quá mức style.
- So với render asset đã duyệt cùng bộ (`preview.py compare`, `score_variants.py`).
- Không nét, vân, noise, bóng vẽ sẵn nếu style không có (bảng lỗi trong gen craft).
- Ở mip thấp không lem màu ô bên.

## Gotchas

- Gen ảnh để làm atlas thường thêm vân và sáng tối: atlas nên tạo bằng màu đo từ style sheet, không gen.
- Màu đẹp trên ô phẳng có thể quá tối/sáng trên model dưới ánh sáng engine: luôn chọn màu trên render.
- Vertex color phụ thuộc mật độ đỉnh: ranh giới màu cong cần thêm cạnh, đề xuất với 3D Artist thay vì đổi sang texture.
