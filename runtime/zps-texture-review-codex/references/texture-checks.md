# Texture checks — cách kiểm và chẩn đoán

Đọc khi cần kiểm sâu một nhóm trong bảng ở SKILL.md hoặc khi nguyên nhân chưa rõ. Chi tiết kỹ thuật về UV, bake, padding và import nằm ở [Mapping, bake và kiểm tại đích](../../zps-surface-codex/references/mapping-validation.md); file này chỉ nói reviewer kiểm gì, bằng gì và kết luận được tới đâu.

## Bằng chứng tối thiểu theo câu hỏi

| Câu hỏi review | Bằng chứng cần | Không đủ để kết luận |
|---|---|---|
| Texture có đúng style không | Render on-model ở camera game, so với asset đã duyệt cùng loại dưới cùng lighting | Atlas phẳng, paint view, ảnh gen |
| Seam có lộ không | Render nhiều góc ở khoảng cách game, có góc nhìn thẳng vào đường cắt UV chính | Một góc đẹp; ảnh UV layout |
| Texel density có đều không | Render checker, hoặc số đo texel density từ `inspect_model.py` | Kích thước file texture |
| Map đúng hợp đồng không | Danh sách kênh, color space, normal convention từ file/import thật | Tên file, mô tả trong prompt |
| Đọc được ở xa không | Render ở khoảng cách xa nhất, mip/compression thật nếu thuộc scope | Thu nhỏ ảnh render bằng tay |
| Đạt trong engine không | Ảnh hoặc capture từ engine đích | Render Blender (ghi rõ là Blender) |

Thiếu bằng chứng ở hàng nào thì kết luận hàng đó là `not_checked`, không phải pass hay fail.

## Kiểm thêm theo phương pháp texture

Hỏi hoặc đọc từ brief phương pháp đã chốt trước khi kiểm. Cùng một biểu hiện có thể đúng với phương pháp này và sai với phương pháp khác (ví dụ ánh sáng vẽ sẵn).

| Phương pháp | Điểm riêng cần kiểm | Không coi là lỗi |
|---|---|---|
| Hand-painted unlit | Ánh sáng vẽ sẵn cùng một hướng giả định trên mọi mảnh; ánh sáng không "đi theo" object sai khi object xoay trong phạm vi game; nét theo khối | Có shading vẽ trong albedo |
| Hand-painted / stylized lit | Không bake highlight, specular hay bóng đổ cố định; shading chủ ý vẫn đúng ở vùng sáng và tối khi xoay đèn | Một chút art shading đã chốt trong brief |
| Flat color / gradient atlas / vertex color | Vùng vật liệu đọc rõ ở kích thước màn hình; ô atlas không lem ở mip thấp; không có nét, vân, noise mà style không có | UV chồng giữa các mặt cùng màu |
| PBR | Base color không chứa lighting; roughness/metallic hợp lý dưới đèn xoay; normal đúng convention; packing kênh đúng hợp đồng | Base color tối hoặc sáng hơn ảnh concept khi lighting engine bù |
| Tileable / trim / decal | Lặp không lộ ở khoảng nhìn game; mép dải trim không lem; decal đúng scale, mép và blending | Lặp khi nhìn soi gần ngoài camera game |
| Pixel texture | Texel density đồng nhất giữa các asset; filter Nearest; không màu ngoài palette; pixel không nhòe ở khoảng xa | Cạnh răng cưa có chủ ý |
| Photo / scan | Ánh sáng và bóng của ảnh gốc đã được loại; chi tiết ảnh thật không "lạc style" cạnh asset đã duyệt | — |
| Projection (paint view) | Paint bám geometry ở góc chiếu; vùng không thấy được fill hợp lý và ghi là suy luận; mặt sau hoặc dưới có được xem | Vùng suy luận đơn giản hơn vùng chiếu |

Chi tiết từng phương pháp: các file trong [Surface references](../../zps-surface-codex/references/).

## Cây chẩn đoán nhanh

- **Mờ:** ảnh gốc đủ nét? → UV island có đủ diện tích/không bị kéo giãn (checker)? → mip/filter/compression? → shader/lighting làm mất chi tiết?
- **Đen, sai màu, quá sáng:** color space của từng map → alpha mode → normal bị lật kênh Y → material link/shader. Chỉ đề nghị vẽ lại khi các bước này đã loại trừ.
- **Seam:** UV split đặt ở đâu → padding/dilation → tangent/bake cage → khác biệt nét vẽ hai bên đường cắt. Blur seam chỉ là chữa triệu chứng.
- **Chi tiết đi theo UV, không theo khối:** thường do vẽ/gen trực tiếp trên atlas. Đề nghị vẽ trên model hoặc paint view theo hướng khối.
- **Ánh sáng sai hướng hoặc nhân đôi:** lighting đã bake vào albedo cộng với lighting của engine (PBR/lit), hoặc ánh sáng vẽ sẵn không cùng quy ước giữa các mảnh (unlit).
- **Lặp lộ:** dấu nổi bật trong tile, scale tile quá nhỏ so với khoảng nhìn, thiếu biến thể/decal phá lặp.

## Phân mức

- **blocker:** sai hợp đồng map khiến asset hiển thị sai trong engine (color space, normal convention, thiếu kênh bắt buộc); seam hoặc lỗi làm hỏng khả năng đọc vật liệu/gameplay ở camera game.
- **major:** lệch style rõ so với asset đã duyệt; texel density lệch thấy được giữa các mảnh cạnh nhau; ánh sáng bake sai pipeline.
- **minor:** seam chỉ lộ khi soi gần ngoài camera game; nhịp chi tiết chưa đẹp ở vùng phụ.
- Ghi riêng **preference** cho lựa chọn thẩm mỹ không vi phạm brief.

## Ranh giới role

Reviewer kết luận vấn đề và nguyên nhân có bằng chứng. Sửa map thuộc Surface; sửa UV layout, mesh, bake high→low thuộc 3D Artist; đổi style thuộc AD. Khi nguyên nhân chưa phân biệt được giữa map và UV, ghi cả hai giả thuyết và kiểm phân biệt (ví dụ render checker cùng góc).
