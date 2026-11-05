# Tileable, trim sheet, decal, triplanar

Cho môi trường và kiến trúc: ít texture, dùng chung cho nhiều mesh, chi tiết riêng bằng decal.

## Chọn cách

| Cách | Dùng khi | Lưu ý |
|---|---|---|
| Tileable | Bề mặt lớn liên tục: đất, tường, sàn, mái | Lặp phải không lộ; texel density thống nhất giữa asset |
| Trim sheet | Viền, nẹp, gờ, ván, ống lặp theo một trục | UV đặt theo dải của trim; quy ước dải ghi trong bảng giao |
| Decal | Chi tiết riêng trên bề mặt lặp: vết bẩn, biển, nứt | Godot Mobile: tối đa 8 decal mỗi mesh resource; Compatibility không có decal (dùng Sprite3D cho mặt gần phẳng) |
| Triplanar | Địa hình, đá, khối không có UV tốt | World space để liền giữa các mesh; mờ ở góc giao; tốn shader hơn |

## Làm tileable

1. Thiết kế mảng lớn/trung/nhỏ theo style; tránh một dấu nổi bật dễ nhận ra khi lặp.
2. Tạo nguồn (gen theo gen craft, hoặc vẽ), rồi làm liền mép (offset nửa ô, sửa vết nối).
3. Kiểm `preview.py tile --repeat 3` và trên model ở khoảng nhìn game; tìm dấu lặp và vết nối.
4. Biến thể giảm lặp: 2–3 tile cùng palette, hoặc decal/vertex color phủ lên.

## Làm trim sheet

1. Liệt kê chi tiết cần dùng chung (ván, gờ, viền kim loại…) và chiều rộng thực.
2. Xếp dải ngang theo thứ tự, chiều cao dải tỷ lệ với kích thước thực theo texel density chung.
3. Mỗi dải lặp được theo chiều ngang; giao bảng dải (tên, vị trí v, chiều rộng thực).
4. Kiểm trên vài mesh mẫu do 3D Artist map: mép dải không lem, chi tiết không méo.

## Tự kiểm

- Texel density đồng nhất giữa asset cùng cảnh (`inspect_model.py` texel_density cho từng mesh).
- Lặp không lộ ở góc game; decal hợp ánh sáng và palette.
- Mip thấp: không lem dải bên (trim) hay vết nối (tile).

## Gotchas

- Ảnh gen thường có ánh sáng một phía: tileable phải khử sáng/phẳng sáng, nếu không lặp sẽ thành sọc sáng tối.
- Trim sheet chỉ hiệu quả khi 3D Artist map theo quy ước: thống nhất bảng dải trước khi vẽ.
