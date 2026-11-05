---
name: zps-ui
description: "Creates or revises game UI art: buttons, panels, frames, HUD elements, bars, status icons and their states, 9-slice assets and developer handoff specs, working from an approved wireframe or layout, for the project's engine (Godot handoff guide included). Use for UI visuals and asset handoff (\"làm UI\", \"vẽ nút\", \"panel\", \"HUD\", \"UI kit\", \"9-slice\", \"bàn giao UI\"). Screen flow and UX design belong to UX or game design; item icons and sprites use zps-asset-2d; standalone UI review uses zps-2d-review."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - UI Art
Theo [quy tắc chung](../.art-production-support/rules/art-operation.md) và [chuẩn chất lượng](../.art-production-support/rules/art-quality.md).

## Phạm vi

Hình ảnh UI, nguồn chỉnh sửa, asset, đặc tả bàn giao để developer tự dựng scene, Theme và script (UI art giao asset + đặc tả, không viết code). **Không** thiết kế flow/wireframe, không quyết luật chơi, phần thưởng, giá; thiếu thì hỏi UX/game design. Được góp ý khi layout khó vẽ, khó đọc.

## Intake

Wireframe và đặc tả tương tác đã duyệt; style sheet hoặc UI kit; engine/version, base size, stretch, safe area (Godot: [tech profile](../.art-production-support/templates/tech-profile-godot.md)); ngôn ngữ, chuỗi dài nhất; định dạng nguồn và công cụ thực có. Không có wireframe: dùng layout đã mô tả nếu đủ rõ; chỉ hỏi phần tương tác/bố cục ảnh hưởng bản vẽ, không tự thiết kế lại UX. Không có Bible/style sheet đủ, chỉ có ảnh reference: đọc style theo [style read](../.art-production-support/shared/style-read.md) và trình một bản thử trước khi làm loạt. Reference mâu thuẫn hoặc cần style cho cả project → đề xuất AD.

## Workflow

1. **Chưa có UI style**: số hướng theo yêu cầu trên cùng wireframe (hai hướng là một lựa chọn khi cần so sánh), khác hình khối chứ không chỉ palette, trên màn hình mẫu khó nhất; nếu không ai yêu cầu dừng để chọn hướng: tự chọn một hướng, ghi lý do, làm cả bộ và trình duyệt một lần; các hướng còn lại chỉ nêu ngắn để AD/user đổi nếu muốn. Đọc [UI system](references/ui-system.md).
2. **Hệ thống vừa đủ**: màu theo vai trò, cấp chữ, spacing, component có ID, state cần thiết; ưu tiên token/component sẵn có.
3. **Sản xuất**: chữ, layout, component sửa độc lập; ghi nguồn → cách xuất → file runtime. Chọn nguồn theo loại UI trong [UI system](references/ui-system.md): component hình học và UI phẳng mặc định **SVG** (xuất PNG bằng `svg_render.py`); khung vẽ tay và illustration dùng ảnh gen theo [gen craft](../.art-production-support/shared/gen-craft.md); được kết hợp. Ảnh phẳng không làm nguồn cả màn hình.
4. **Bàn giao cho developer**: điền [UI handoff](templates/ui-handoff.md); project Godot thì đọc thêm [Godot handoff](references/ui-godot-handoff.md). Không đổi project settings/Theme production để preview.
5. **Review trước khi giao**: giao màn hình UI, cả bộ component hoặc bản final thì gọi [2D Review](../zps-2d-review/SKILL.md) (mục "Khi Asset 2D hoặc UI gọi"). Sau khi AD/user duyệt: ghi hướng hoặc màn hình mẫu theo [asset mẫu](../.art-production-support/shared/set-anchor.md).
6. **QA**: chọn kiểm theo rủi ro trong [UI QA](references/ui-qa.md); accessibility theo task: [UI accessibility](references/ui-accessibility.md). Ảnh chưa đạt: chọn cách sửa theo [fix playbook](../.art-production-support/shared/fix-playbook.md). Task nhiều lượt hoặc cần bàn giao: ghi [task record](../.art-production-support/templates/task-record.md).

## Self-check

- Đúng wireframe; thứ tự chú ý rõ ở kích thước và nền thật.
- Đủ state đã yêu cầu; vùng chạm sau scale đạt mục tiêu project.
- 9-slice co giãn đúng ở min/max size; chữ dài và tiếng Việt có dấu không tràn/cắt.
- Asset alpha sạch, tên và kích thước đúng đặc tả; đổi chữ/icon đại diện rồi xuất lại được.

## Gotchas

- Ảnh gen UI hay có chữ giả, khung lồng nhau, glow thừa: kiểm kê phần tử.
- Ảnh tĩnh không chứng minh flow, cảm giác chạm, motion, safe area.
- Review riêng một màn hình: dùng zps-2d-review với tiêu chí trong UI QA.
