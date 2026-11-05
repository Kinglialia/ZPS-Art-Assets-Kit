---
name: zps-2d-artist
description: "Router for 2D game art: picks Asset 2D, UI or 2D Review when the type of 2D work is unclear. Use for a general 2D or UI request (\"làm asset 2D\", \"việc 2D\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - 2D Artist
Router: chọn skill thực thi rồi đọc skill đó. Router không có quy trình sản xuất riêng; intake, style, công cụ, tự kiểm và bàn giao nằm trong skill được chọn. Task đã rõ thì vào thẳng skill đó.

| Việc | Skill |
|---|---|
| Icon, item, sprite, frame, tile, decal, background | [Asset 2D](../zps-asset-2d/SKILL.md) |
| Nút, panel, frame, HUD, thanh, 9-slice, đặc tả bàn giao UI | [UI](../zps-ui/SKILL.md) |
| Góp ý, chẩn đoán, xác nhận bản sửa | [2D Review](../zps-2d-review/SKILL.md) |
| Khám phá thiết kế mới, nhân vật/prop chưa chốt | Ngoài phạm vi → Creative Brainstorming / Concept Artist |
| Texture/material trên model | Ngoài phạm vi → [Texture Artist](../zps-texture-artist/SKILL.md) |
| Luồng màn hình, wireframe, luật chơi | Ngoài phạm vi → UX/game design |

Không chọn được vì thiếu loại đầu ra: hỏi đúng một câu về loại đầu ra. User mô tả trực tiếp, không có brief: skill thực thi lập brief tối thiểu theo [Artist Brief](../.art-production-support/templates/artist-brief.md) và ghi giả định. Phần ngoài chuyên môn: chuyển theo [workflow chung](../.art-director-support/workflows/art-direction.md); không tự mở rộng đầu ra.
