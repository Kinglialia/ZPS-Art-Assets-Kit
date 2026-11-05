---
name: zps-surface-codex
description: "Creates, edits or diagnoses textures and materials on existing 3D models once the texturing method is chosen (hand-painted, flat color or vertex color, PBR, tileable or trim, pixel, photo-based, projection paint), or paints rendered views for a 3D Artist to project; follows the project's engine map conventions (Godot profile included). Use for producing or fixing texture (\"vẽ texture\", \"sửa texture\", \"làm material\", \"trim sheet\", \"paint view\", \"sửa seam\"). If the method is not chosen, use zps-texture-planning-codex first; standalone review uses zps-texture-review-codex."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Surface - Codex

Theo [quy tắc chung](../.art-production-support/rules/art-operation.md) và [chuẩn chất lượng](../.art-production-support/rules/art-quality.md).

## Intake

Phương pháp: người gọi nêu cụ thể (hoặc yêu cầu theo tài liệu Art Style) thì làm theo; không ai nêu → dùng zps-texture-planning-codex để tự chọn. Khi 3D Artist gọi, nhận theo phần A của [bàn giao 3D ↔ Texture](../.art-production-support/templates/3d-texture-handoff.md); tự đo phần đo được bằng `inspect_model.py`, chỉ hỏi phần không đo được và gom thành một lần hỏi. Cần: model/UV/shader version, vùng được giao, style sheet, hợp đồng map (kênh, color space, kích thước, normal convention từ thông số project; Godot: [tech profile](../.art-production-support/templates/tech-profile-godot.md)), người nhận. Thiết kế mới (motif, biểu tượng): chuyển phần thiết kế sang Concept/AD nếu thuộc task; không tự đổi identity đã khóa. Không có Bible/style sheet đủ, chỉ có ảnh reference: đọc style theo [style read](../.art-production-support/shared/style-read.md) và trình một bản thử trên model trước khi làm loạt. Reference mâu thuẫn hoặc cần style cho cả project → đề xuất AD.

## Workflow

1. Đọc **chỉ** file của phương pháp đã chốt (cộng file chung khi cần):

| Phương pháp | Đọc |
|---|---|
| Hand-painted | [Hand-painted](references/hand-painted.md); recipe: [painting practice](references/painting-practice.md) |
| Flat color, gradient atlas, vertex color | [Flat color](references/flat-color.md) |
| PBR, bake, data maps | [PBR](references/pbr.md) |
| Tileable, trim sheet, decal, triplanar | [Tileable/trim](references/tileable-trim.md) |
| Pixel texture | [Pixel texture](references/pixel-texture.md) |
| Photo/scan | [Photo/scan](references/photo-scan.md) |
| Paint view để chiếu | [Projection](references/projection.md) |
| Chung: phân mảng vật liệu mới | [Surface craft](references/surface-craft.md) |
| Chung: UV, seam, bake, import | [Mapping](references/mapping-validation.md) |

2. Cần render **checker + clay** (`render_model.py`) khi chưa có render còn hiệu lực cho đúng mesh/UV version, khi mesh/UV đổi, hoặc khi lỗi có thể do UV/scale. Sửa màu nhỏ trên mesh/UV không đổi thì dùng lại bằng chứng cũ. Không có Blender: xin 3D Artist ảnh render.
3. Material intent và ngân sách chi tiết theo style sheet.
4. Tạo theo phương pháp; phần gen/edit theo [gen craft](../.art-production-support/shared/gen-craft.md).
5. Gắn lên model, render nhiều góc, ánh sáng game nếu biết.
6. Kiểm thêm thắt theo chuẩn chất lượng, bảng lỗi ảnh gen, self-check; sửa nguyên nhân (UV, scale, shading) trước khi làm lại. Ảnh chưa đạt: chọn cách sửa theo [fix playbook](../.art-production-support/shared/fix-playbook.md). Task nhiều lượt hoặc cần bàn giao: ghi [task record](../.art-production-support/templates/task-record.md).

## Self-check (trên render model)

- Đúng phương pháp, style sheet; so render asset đã duyệt cùng loại.
- Seam không lộ ở góc game; chi tiết theo khối, không theo cạnh UV.
- Lit/PBR: không bake highlight/bóng cố định vào albedo; kênh, color space đúng.
- Không chi tiết ngoài kiểm kê.

## Handoff

Giao theo phần B của [bàn giao 3D ↔ Texture](../.art-production-support/templates/3d-texture-handoff.md): cách làm đã dùng và lý do (khi tự chọn), maps/atlas/paint views, render đã mở (renderer: Blender không phải engine đích), hợp đồng map, bảng ô atlas hoặc dải trim nếu có, **ghi chú thiết lập material** cho người đưa vào engine (lit/unlit, nén, mipmap, ảnh nào là normal map), phần chưa kiểm. Texture không tự tạo material trong project engine trừ khi task giao rõ. Khi 3D Artist gọi, trả kết quả cho 3D để gắn vào model và xuất file cuối.

## Gotchas

- Gen lên UV layout thường vẽ sáng/bóng theo atlas: luôn render kiểm.
- Vùng vật liệu lấy từ bảng "phần → vật liệu" và ảnh parts trong phần A của mẫu bàn giao; model mặc định chỉ có một material. Cần 3D sửa UV hoặc tách slot: gom mọi yêu cầu vào một lần gửi.
- Normal map engine khác có thể DirectX-style; Godot cần OpenGL Y+.
