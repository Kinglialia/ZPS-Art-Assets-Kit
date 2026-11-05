---
name: zps-texture-artist
description: "Router for textures on 3D models: picks Texture Planning, Surface or Texture Review when the texture task is unclear. Use for a general texture request (\"texture cho model\", \"việc texture\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Texture Artist
Router: chọn skill thực thi rồi đọc skill đó. Router không có quy trình sản xuất riêng; intake, style, công cụ, tự kiểm và bàn giao nằm trong skill được chọn. Task đã rõ thì vào thẳng skill đó.

| Việc | Skill |
|---|---|
| Chọn cách texture cho model, chưa chốt phương pháp | [Texture planning](../zps-texture-planning/SKILL.md) |
| Texture/material, atlas, trim, paint view; phương pháp đã chốt | [Surface](../zps-surface/SKILL.md) |
| Góp ý, chẩn đoán, xác nhận bản sửa | [Texture Review](../zps-texture-review/SKILL.md) |
| Thiết kế mới: motif, biểu tượng, vật liệu chưa có | Ngoài phạm vi → Concept Artist / AD |
| Icon, sprite, background, UI art | Ngoài phạm vi → [2D Artist](../zps-2d-artist/SKILL.md) |
| Mesh, UV, bake high-poly, gán vertex color | Ngoài phạm vi → [3D Artist](../zps-3d-artist/SKILL.md) |

Không chọn được vì chưa rõ đã chốt phương pháp hay chưa: coi là chưa chốt và dùng Texture planning. User mô tả trực tiếp, không có brief: skill thực thi lập brief tối thiểu theo [Artist Brief](../.art-production-support/templates/artist-brief.md) và ghi giả định. Mặt khuất không có trong concept luôn ghi là suy luận. Phần ngoài chuyên môn: chuyển theo [workflow chung](../.art-director-support/workflows/art-direction.md); không tự mở rộng đầu ra.
