---
name: zps-texture-planning-codex
description: "Recommends how to texture a given 3D model for a project's style: reads the model (UVs, materials, polygon count, vertex colors, screen size) and the concept or style sheet, then proposes one or two texturing methods with trade-offs and a small test. Use before texturing when the method is not chosen (\"nên texture kiểu gì\", \"chọn cách texture\", \"hand-painted hay PBR\", \"lên phương án texture\"); once the method is chosen, use zps-surface-codex."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Texture Planning - Codex

Theo [quy tắc chung](../.art-production-support/rules/art-operation.md). Đầu ra là đề xuất phương pháp, không phải texture đã vẽ.

**Ai quyết cách làm:** người gọi (AD, user) nêu cách làm cụ thể, hoặc yêu cầu theo tài liệu Art Style → làm theo. Không ai nêu → skill tự chọn. Giới hạn kỹ thuật của model (ví dụ không có UV) vẫn phải theo. Hai yêu cầu cụ thể mâu thuẫn nhau → hỏi người gọi, không tự chọn bên nào. Khi tự chọn: ghi cách đã chọn và lý do một dòng trong bàn giao; ưu tiên cách skill tự làm được tới chất lượng giao (mục "Năng lực thực của role" trong [texture methods](references/texture-methods.md)); cách cần người hoặc DCC thì báo trước, không chọn ngầm.

## Intake

Người giao (3D Artist, AD, user); khi 3D Artist gọi, nhận theo phần A của [bàn giao 3D ↔ Texture](../.art-production-support/templates/3d-texture-handoff.md); model và version; concept hoặc style sheet/Bible; camera, kích thước trên màn hình; số asset cùng loại, biến thể; thông số engine của project (Godot: [tech profile](../.art-production-support/templates/tech-profile-godot.md)). Thiếu thì ghi giả định. Concept thiếu vùng vật liệu/mặt khuất: ghi suy luận hoặc hỏi user callout.

## Workflow

1. **Đo model**: `inspect_model.py` (UV, material, vertex color, texel density) và `render_model.py --mode clay` + `--mode checker` vài góc; mở ảnh. Xem [scripts](../.art-production-support/shared/scripts/README.md#model). Không có Blender: xin 3D Artist ảnh UV, thông số; ghi phần chưa đo. Chỉ hỏi những gì không đo được, gom thành một lần hỏi.
2. **Đọc concept/style**: nét vẽ tay, ánh sáng vẽ sẵn hay engine, vân bề mặt, mức realistic. Chưa có style sheet → [style read](../.art-production-support/shared/style-read.md).
3. **Chọn 1–2 phương pháp** (author × shader) theo [texture methods](references/texture-methods.md), kèm lý do, đánh đổi (chất lượng, bộ nhớ, draw call, công sức, biến thể) và phần cần DCC/người.
4. **Bản thử nhỏ**: vùng đại diện, góc camera, tiêu chí đạt.
5. Giao theo [mẫu đề xuất](references/proposal-template.md); khi phương pháp đã được chốt hoặc nằm trong quyền lựa chọn hiện có, chuyển [Surface](../zps-surface-codex/SKILL.md).

## Gotchas

- UV chồng giữa các object dùng chung một texture là lỗi khi các vùng đó cần chi tiết, bake hoặc dấu riêng. Palette/gradient atlas, stack và mirror có chủ đích là hợp lệ khi không cần thông tin riêng (xem spec của 3D Artist); xác nhận ý đồ trước khi gọi là lỗi. Ánh sáng bake vào albedo thì mirror/stack dễ lộ.
- UV ngoài 0–1 có thể là tileable/trim có chủ đích: hỏi trước khi gọi là lỗi.
- Không có UV: chỉ vertex color, triplanar, procedural cho tới khi có UV.
- Phương pháp role không tự làm được: ghi rõ phần cần người/DCC.
- 3D Artist gọi **trước khi unwrap**: đề xuất phải kèm yêu cầu UV cho 3D (được chồng không, texel density, hướng trim) và có cần tách material slot theo vùng không. Chỉ yêu cầu tách slot khi các vùng cần shader khác nhau; mặc định giữ một material.
