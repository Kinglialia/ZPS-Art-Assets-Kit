# Texture methods — chọn cách author × shader

Một kiểu bề mặt = **cách tạo màu (author)** × **cách engine chiếu sáng (shader)**. Hai lựa chọn độc lập: vẽ tay có thể chạy unlit hoặc PBR; màu phẳng có thể lit hoặc toon.

## Contents
- Cách author
- Shader
- Đọc input → gợi ý
- Ràng buộc Godot mobile
- Năng lực thực của role

## Cách author

| Cách | Bản chất | Hợp khi | Đánh đổi | Đọc khi làm |
|---|---|---|---|---|
| Hand-painted | Vẽ màu, sáng tối, vân vào albedo | Concept có nét vẽ tay, ánh sáng vẽ sẵn, camera ổn định | Công vẽ cao; ánh sáng vẽ sẵn sai khi xoay đèn | hand-painted, painting-practice |
| Flat color / palette atlas | Mỗi vùng vật liệu là ô màu phẳng; khối do engine | Low-poly, mặt phẳng rõ, màu theo khối, nhiều asset chung palette | Ít chi tiết bề mặt; phụ thuộc hình khối và ánh sáng | flat-color |
| Gradient atlas | Ô màu chuyển trong ô | Như trên nhưng cần chiều sâu (gốc tối, ngọn sáng) | Hướng gradient gắn với UV | flat-color |
| Vertex color | Màu gán vào đỉnh, không texture | Mobile rất nhẹ, mesh đủ đỉnh để giữ ranh giới màu | Ranh giới màu theo cạnh mesh; khó chi tiết | flat-color |
| Bake + material | Bake normal/AO/curvature từ high-poly rồi phủ vật liệu | Hero asset, PBR, cận cảnh | Cần high-poly và DCC (Substance…); nặng hơn | pbr |
| Tileable / trim sheet / decal | Texture lặp hoặc dải dùng chung, decal thêm chi tiết | Môi trường lớn, kiến trúc, nhiều mesh cùng vật liệu | UV phải theo quy ước trim; lặp dễ lộ | tileable-trim |
| Triplanar | Chiếu texture theo 3 trục, không cần UV | Đá, đất, khối địa hình; mesh chưa có UV | Mờ ở vùng giao; tốn shader hơn | tileable-trim |
| Pixel texture | Texel to, palette giới hạn, filter Nearest | Game pixel/retro 3D | Texel density phải đồng nhất toàn game | pixel-texture |
| Photo / scan | Từ ảnh chụp, đã khử sáng và cân màu | Realistic hoặc stylized dựa trên ảnh | Quyền ảnh; ánh sáng nướng sẵn; dễ lệch style | photo-scan |
| Projection paint | Vẽ trên ảnh render rồi chiếu vào model | Hero asset góc nhìn cố định, paintover concept | Mặt khuất cần xử lý; cần owner bake | projection |

## Shader

| Shader | Khi nào | Lưu ý |
|---|---|---|
| Unlit | Ánh sáng vẽ sẵn, mobile rất nhẹ | Không phản ứng đèn/ngày đêm |
| Lit / toon | Màu phẳng hoặc vẽ tay nhẹ, cần đèn động | Albedo không vẽ bóng cố định; toon dùng ramp |
| PBR (metallic-roughness) | Vật liệu cần phản xạ thật | Albedo sạch ánh sáng; cần roughness/metallic/normal đúng convention |

## Đọc input → gợi ý

| Quan sát | Nghiêng về |
|---|---|
| Concept có nét/vân vẽ tay, bóng vẽ sẵn | Hand-painted (unlit hoặc lit nhẹ) |
| Màu theo khối, mặt phẳng rõ, gần như không vân | Flat/gradient atlas hoặc vertex color + lit/toon |
| Nhiều mesh cùng vật liệu, cảnh lớn | Tileable/trim/decal, triplanar cho địa hình |
| Cận cảnh, vật liệu phản xạ (kim loại, da bóng) | Bake + PBR |
| Model không có UV | Vertex color, triplanar; hoặc xin UV |
| UV chồng nhiều, mirror | Tránh chi tiết bất đối xứng; flat/tileable |
| Pixel lớn, cạnh pixel rõ | Pixel texture, Nearest |
| Nhiều skin/mùa | Palette atlas swap, hoặc material instance đổi màu |

Gợi ý là giả thuyết: kiểm bằng bản thử trên vùng đại diện của model trước khi làm toàn bộ. Khi có yêu cầu cụ thể từ người gọi hoặc tài liệu Art Style, bảng này không thay yêu cầu đó.

## Ràng buộc Godot mobile

- Godot sắp xếp vật theo material/shader: ít material, chung atlas thì nhẹ hơn.
- Instancing tự động chỉ có ở Forward+, **không có ở Mobile/Compatibility**: nhiều vật giống nhau trên mobile dùng MultiMesh (3D Artist/Developer quyết).
- Vật alpha blend không sắp được, vẽ từ xa tới gần và không được instancing tự động: ưu tiên alpha scissor/hash; tách phần trong suốt thành surface riêng.
- Vertex color: `StandardMaterial3D` mặc định bỏ qua; bật **Vertex Color → Use as Albedo** (thường kèm **Is sRGB**).
- Decal: Mobile áp tối đa 8 decal mỗi mesh resource; Compatibility không hỗ trợ decal.
- `ORMMaterial3D` dùng một texture ORM (occlusion, roughness, metallic).
- Normal map Godot dùng quy ước OpenGL (Y+).

Nguồn: tài liệu Godot (Standard Material 3D, Using decals, Optimizing 3D performance), repo `godotengine/godot-docs`. Kích thước texture, nén, mipmap: tech profile của project.

## Năng lực thực của role

Khi tự chọn, ưu tiên cách role tự làm tới chất lượng giao. LLM làm tốt: palette/gradient atlas, projection từ ảnh vẽ, texture lặp, chỉnh màu bằng script. LLM làm kém: vẽ tay texture riêng trực tiếp trên UV layout (ảnh gen hay vẽ sáng tối theo atlas thay vì theo khối), bake high-poly chất lượng cao, Substance.

Tự làm: gen/edit ảnh theo [gen craft](../../.art-production-support/shared/gen-craft.md), palette/gradient atlas, chỉnh màu bằng script, render kiểm trên model (Blender headless), paint view. Cần người/DCC: sculpt high-poly, bake chất lượng cao, Substance, chỉnh UV, gán vertex color trên mesh (đề xuất cho 3D Artist). Ghi rõ trong đề xuất.
