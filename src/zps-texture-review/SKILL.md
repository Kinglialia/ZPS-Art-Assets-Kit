---
name: zps-texture-review
description: "Reviews textures and materials as they appear on a 3D model: seams, texel density, map channels/color space/normal convention, baked lighting in albedo, mip/compression and style fit, diagnosing whether a problem comes from the map, UV or lighting, and verifies revisions with the shared AD issue fields. Use for standalone texture/material review (\"review texture\", \"kiểm texture\", \"texture bị seam\", \"material nhìn sai\", \"soát map\"). Not for 2D sprites/UI (zps-2d-review), mesh/topology checks (zps-3d-artist), cross-domain or concept critique (zps-artistic-critique); routine self-checks stay inside zps-surface."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Texture Review
Theo [quy tắc chung](../.art-production-support/rules/art-operation.md). Review không cần tool tạo ảnh, nhưng phải mở được ảnh/render thật. Texture được đánh giá **trên model**: một atlas phẳng đẹp chưa chứng minh texture đạt.

## Intake

Artifact/version của **texture và model/UV/material** đang xem; brief, Bible/style sheet version; phương pháp texture (hand-painted, flat/vertex color, PBR, tileable/trim, pixel, projection…) lấy theo thứ tự: yêu cầu cụ thể của người gọi (AD, user, tài liệu Art Style) → cách Texture Artist đã ghi khi tự chọn (phần B của [bàn giao 3D ↔ Texture](../.art-production-support/templates/3d-texture-handoff.md)). Không tìm thấy: suy ra từ texture, ghi là giả định, và ghi issue "chưa ghi phương pháp". Khi Texture tự chọn, kiểm thêm lựa chọn đó có hợp brief và model không; hợp đồng map (kênh, color space, kích thước, normal convention) nếu có; stage (bản thử / final); camera, khoảng cách và lighting đích; renderer của ảnh được gửi (Workbench, Eevee, Cycles hay engine thật). Không có Bible: nhận xét theo brief, ghi mức phù hợp project là tạm thời. Thiếu render on-model và không tự render được: chỉ nhận xét được atlas, ghi phần on-model là `not_checked`, và verdict không thể là `meets_checked_criteria` cho tiêu chí on-model.

## Workflow

1. Mở render: nhìn tổng thể → soi vùng giải thích nhận định → nhìn lại tổng thể. Ưu tiên góc và khoảng cách camera game. Reviewer được tự chạy `render_model.py` (checker/clay/textured), `inspect_model.py` và `preview.py` khi có Blender/Pillow, để tự lấy bằng chứng thay vì hỏi lại; không sửa model hay texture.
2. Kiểm mỹ thuật và độ phù hợp style (những chiều liên quan trong 6 chiều: composition, shape/silhouette, color/value, lighting, material/texture, visual appeal) — tách riêng với kiểm kỹ thuật ở bước 3.
3. Chạy các kiểm chuyên môn texture bên dưới theo phương pháp và rủi ro; chi tiết trong [texture checks](references/texture-checks.md).
4. Chẩn đoán trước khi đề xuất sửa: cùng một biểu hiện có thể do map, UV, normal/tangent, shader hoặc lighting. Ghi nguyên nhân là giả thuyết khi chưa có bằng chứng phân biệt, và đề xuất một kiểm phân biệt rẻ.
5. Soi bảng lỗi ảnh gen trong [gen craft](../.art-production-support/shared/gen-craft.md) khi texture có phần do AI tạo; chi tiết không truy được về brief là issue. Review giao cho người/agent khác: gửi theo [review request](../.art-production-support/templates/review-request.md).
6. Review nhanh: nêu vài vấn đề có bằng chứng, không bắt buộc score/ID. Khi theo dõi revision hoặc nghiệm thu, ghi issue theo [mẫu review](../.art-production-support/templates/review.md) — cùng trường với AD: id, priority, region, viewing_condition, evidence, consequence, confidence, repair, preserve, acceptance, status. `region` ghi vùng trên model và, khi biết, vùng/ô trên atlas.
7. Ưu tiên 1–3 việc tác động lớn nhất; giữ danh sách đầy đủ khi tracked.
8. Bản sửa: giữ id, chỉ `resolved` khi render mới cùng điều kiện chứng minh acceptance; tìm regression và điểm mạnh bị mất. Nếu mesh/UV đã đổi giữa hai bản, ghi bằng chứng cũ không còn hiệu lực cho vùng bị ảnh hưởng.

Đọc [phương pháp sâu](../.art-production-support/shared/visual-review.md) khi nhiều tiêu chí, nhiều vòng hoặc nguyên nhân chưa rõ.

## Kiểm chuyên môn texture (chọn theo phương pháp và rủi ro)

| Nhóm | Kiểm gì |
|---|---|
| Seam | Seam lộ ở góc/khoảng cách game; lệch màu, value hoặc hướng nét qua đường cắt UV; seam chỉ lộ ở mip thấp |
| Texel và scale | Mật độ texel giữa các mảnh nhìn cạnh nhau; vùng ưu tiên đủ độ phân giải; scale vân/nét đồng nhất giữa vùng cùng vật liệu |
| Theo khối | Chi tiết, nét và chuyển sắc đi theo khối của model, không theo cạnh/island UV; không có vết vẽ cắt ngang khối |
| Ánh sáng trong map | Lit/PBR: không bake highlight, bóng đổ cố định hoặc AO quá nặng vào albedo. Unlit/hand-painted: ánh sáng vẽ sẵn cùng hướng với quy ước và nhất quán giữa các mảnh |
| Map contract | Đủ kênh theo hợp đồng; color space đúng (albedo sRGB; roughness/metal/AO/normal linear); normal đúng convention của engine đích (Godot: OpenGL Y+); packing kênh đúng thứ tự |
| Lặp và tiling | Dấu nổi bật lặp lộ ở nhiều ô; trim/decal đúng hướng, scale, mép và blending |
| Xa và nén | Ở khoảng cách xa nhất: lấm tấm, mờ hoặc banding do mip/compression; alpha/cutout giữ được hình |
| Mirror/stack | Chi tiết riêng (chữ, vết, logo) bị lật hoặc lặp vì UV mirror/stack; chỉ là lỗi khi vùng đó cần thông tin riêng |
| Vật liệu đọc được | Các vùng vật liệu phân biệt được ở kích thước game; độ chi tiết theo phân cấp thị giác, không phủ đều mọi bề mặt |

## Output

Phương pháp đã dùng làm chuẩn kiểm và nguồn của nó → điểm mạnh cần giữ → issue ưu tiên (ghi rõ nghi do map / UV / lighting / shader) → việc tiếp theo và ai làm (Surface sửa map; 3D Artist sửa UV/mesh/bake) → phần chưa đủ bằng chứng → verdict: meets_checked_criteria / needs_revision / insufficient_evidence. Ghi self-review hay reviewer độc lập thật, renderer đã dùng, và ảnh Blender không chứng minh kết quả trong engine. Verdict không phải AD approval.

## Gotchas

- Không bịa lỗi để có đủ danh sách; "không cần sửa" là kết luận hợp lệ.
- Atlas phẳng hay paint view đẹp không chứng minh texture on-model đạt; luôn xin hoặc tự render trên model.
- Lỗi đen/sai màu: kiểm color space, alpha, normal và material link trước khi đề nghị vẽ lại. Lỗi seam: kiểm UV/tangent/bake/padding trước khi blur.
- So bản trước/sau chỉ hợp lệ khi cùng camera, lighting, exposure, tone mapping và import.
- Ảnh tĩnh không chứng minh animation, topology hay hiệu năng; không suy texture resolution từ ảnh render.
- Khi được giao cả sửa: chuyển issue cho skill sản xuất, không review lại toàn bộ.
- Issue ngoài phạm vi role (mesh, UV layout, bake high→low): ghi issue, đánh dấu cho 3D Artist; không tự sửa.

[Gate kỹ thuật](../.art-production-support/shared/scripts/README.md#evidence-gate) chỉ khi caller cần nghiệm thu máy đọc được.
