---
name: zps-asset-2d
description: "Creates or revises in-game 2D images: icons, item sets, sprites, frame sequences, tiles, decals and backgrounds, including small design choices within the brief, for the project's engine and display sizes (Godot mobile profile available). Use when the deliverable is placed directly in the game (\"vẽ icon\", \"làm bộ item\", \"làm sprite\", \"tile\", \"background\", \"sửa icon\"). UI elements use zps-ui; 3D asset concepts use zps-concept-artist; textures on models use zps-surface."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Asset 2D
Theo [quy tắc chung](../.art-production-support/rules/art-operation.md) và [chuẩn chất lượng](../.art-production-support/rules/art-quality.md).

## Intake

Cần: brief, Bible/style sheet, asset mẫu của bộ (theo [asset mẫu](../.art-production-support/shared/set-anchor.md)), kích thước hiển thị và file, alpha, pivot/baseline, states/frames, nền hiển thị. Thông số engine: Godot theo [tech profile](../.art-production-support/templates/tech-profile-godot.md); engine khác theo thông số project. Concept đã chốt (nếu có) làm Execution reference. Icon mới tự thiết kế trong phạm vi brief; câu hỏi thiết kế lớn (nhân vật/prop chưa chốt): báo user cần concept đã chốt. Không có Bible/style sheet đủ, chỉ có ảnh reference: đọc style theo [style read](../.art-production-support/shared/style-read.md) rồi làm cả bộ và trình duyệt một lần; chỉ làm mẫu trước khi user yêu cầu. Reference mâu thuẫn hoặc cần style cho cả project → đề xuất AD.

## Workflow

1. Đọc [production](references/production.md) khi tạo mới hoặc đổi canvas/alpha/pivot/frame/import; sửa giữ thiết kế: [revision](../.art-production-support/shared/revision.md).
2. Ngân sách chi tiết theo **kích thước hiển thị**: ở kích thước nhỏ (ví dụ icon 64px), ưu tiên silhouette và vài điểm nhận diện chính; kiểm bằng `preview.py sheet` ở kích thước đích thay vì đếm chi tiết.
3. Tạo theo [gen craft](../.art-production-support/shared/gen-craft.md), asset mẫu của bộ làm reference đầu vào.
4. Hậu kỳ: tách nền, crop theo canvas cố định, đặt pivot/baseline, scale về kích thước file; không auto-crop từng frame.
5. `preview.py sheet` (kích thước đích, nền sáng/tối/game); `tile` cho tile; `sprite_check.py` và `anim_preview.py` (filmstrip, onion skin, GIF) cho frame; `palette_report.py` khi có palette; `inspect_image.py` cho hợp đồng file.
6. Mở preview; kiểm thêm thắt theo [chuẩn chất lượng](../.art-production-support/rules/art-quality.md), bảng lỗi ảnh gen, self-check; sửa tới khi đạt hoặc hết budget. Ảnh chưa đạt: chọn cách sửa theo [fix playbook](../.art-production-support/shared/fix-playbook.md). Task nhiều lượt hoặc cần bàn giao: ghi [task record](../.art-production-support/templates/task-record.md).

## Self-check

- Đọc được ở kích thước hiển thị trên nền game; phân biệt với asset cùng bộ.
- Đồng bộ bộ: cùng góc nhìn, độ dày nét, mức chi tiết, hướng sáng, scale vật.
- Alpha sạch (không halo trên nền tối/sáng), canvas/pivot đúng hợp đồng.
- Tile nối liền, không lộ dấu lặp; frame không rung pivot.

## Handoff

Giao cả bộ hoặc bản final: gọi [2D Review](../zps-2d-review/SKILL.md) trước khi giao (mục "Khi Asset 2D hoặc UI gọi"); sửa issue rồi chỉ kiểm lại các issue đó. Sau khi AD/user duyệt: ghi asset mẫu theo [asset mẫu](../.art-production-support/shared/set-anchor.md).

PNG đúng kích thước/alpha, source thực có, contact sheet đã mở, GIF animation nếu có (cho người duyệt xem), đề xuất import (filter, mipmap, nén, atlas), trạng thái: export đã kiểm / đã import vào engine / đã xem trên thiết bị.

## Gotchas

- Gen icon hay thêm khung, nền tròn, bóng đổ, glow ngoài bộ: so với icon mẫu.
- Thu nhỏ ảnh gen làm mất nét mảnh: tăng độ dày nét/khối trước, không chỉ sharpen.
- Ảnh gen hay có nền giả trong suốt hoặc nền trắng: kiểm `alpha_extrema`.
- Pixel art: không resample bilinear; filter Nearest.
