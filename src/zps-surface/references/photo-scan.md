# Photo / scan-based texture

Dùng ảnh chụp hoặc scan làm nguồn vật liệu, cho realistic hoặc stylized dựa trên ảnh.

## Quyền và nguồn

- Chỉ dùng ảnh có quyền sử dụng trong sản phẩm (ảnh tự chụp, thư viện có license, nguồn project cung cấp). Ảnh xem được trên web không tự có quyền. Ghi nguồn và license vào task record.
- Ảnh screenshot game khác chỉ để học nguyên tắc, không làm nguồn texture.

## Quy trình

1. **Chọn ảnh** chụp thẳng góc, ánh sáng đều/u ám, độ phân giải đủ theo texel density đích.
2. **Khử ánh sáng (delight)**: bỏ bóng đổ, highlight, AO nướng sẵn khỏi albedo để engine tự chiếu sáng; giữ lại khi style là unlit có ánh sáng vẽ sẵn.
3. **Cân màu** về palette/value của style sheet; `tone_match.py` có thể kéo cast màu về reference, `structure_diff.py` xác nhận không đổi hình.
4. **Làm liền/tile** nếu là vật liệu lặp (xem tileable-trim).
5. **Map dữ liệu** (normal, roughness) nếu PBR: suy từ ảnh chỉ là xấp xỉ; kiểm dưới đèn xoay, đọc pbr.
6. **Stylize** nếu style yêu cầu: giảm chi tiết tần số cao, gom mảng, giữ đặc trưng vật liệu; so với reference cùng loại.

## Tự kiểm

- Albedo không còn bóng/highlight cố định (trừ style unlit).
- Màu và value khớp style sheet; không lệch giữa các asset chung cảnh.
- Lặp không lộ; độ sắc nét đồng nhất với asset khác ở khoảng nhìn game.

## Gotchas

- Ảnh chụp mang ánh sáng và góc nhìn của lúc chụp: khi xoay model hoặc đổi đèn sẽ lộ.
- Chi tiết ảnh thật dễ "lạc style" cạnh asset stylized: kiểm cạnh asset đã duyệt.
