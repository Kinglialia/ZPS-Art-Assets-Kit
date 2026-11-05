---
name: zps-2d-review
description: "Reviews in-game 2D assets and UI art at their real display size and background: readability, set consistency, alpha edges, canvas/pivot/frame stability, tile seams, 9-slice, states and long/Vietnamese text, plus style fit, and verifies revisions with the shared AD issue fields. Use for standalone 2D/UI review, and when zps-asset-2d or zps-ui deliver a full set, a final or a UI screen (\"review icon\", \"kiểm sprite\", \"soát bộ icon\", \"review UI\", \"màn hình này ổn chưa\", \"tile bị lộ nối\"). Not for textures on 3D models (zps-texture-review), concept art or cross-domain style decisions (zps-artistic-critique), or open-ended image appreciation (zps-visual-intelligence); routine self-checks on single assets and small edits stay inside those skills."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - 2D Review
Theo [quy tắc chung](../.art-production-support/rules/art-operation.md). Review không cần tool tạo ảnh, nhưng phải mở được ảnh thật. Asset 2D được đánh giá **ở kích thước hiển thị và trên nền thật** của game, không chỉ ở bản phóng to.

## Intake

Artifact/version, loại asset (icon, item set, sprite/frame sequence, tile, decal, background, UI component/màn hình), brief, Bible/style sheet version, asset mẫu của bộ (tìm và dùng theo [asset mẫu](../.art-production-support/shared/set-anchor.md)), stage (thumbnail / bản thử / final), kích thước hiển thị và nền đích; với UI thêm wireframe đã duyệt, state yêu cầu, chuỗi dài nhất và ngôn ngữ. Không có Bible: nhận xét theo brief, ghi mức phù hợp project là tạm thời.

## Workflow

1. Mở ảnh: nhìn tổng thể → soi vùng giải thích nhận định → nhìn lại tổng thể. Xem ở kích thước đích trên nền sáng/tối/nền game bằng `preview.py sheet`; so với asset mẫu bằng `preview.py compare`.
2. Kiểm mỹ thuật và độ phù hợp style (những chiều liên quan trong 6 chiều: composition, shape/silhouette, color/value, lighting, material/texture, visual appeal) — tách riêng với kiểm kỹ thuật ở bước 3.
3. Chạy các kiểm chuyên môn 2D bên dưới theo loại asset; chi tiết trong [2D checks](references/2d-checks.md). UI dùng thêm tiêu chí trong [UI QA](../zps-ui/references/ui-qa.md).
4. Kiểm **ghi chú import** đi kèm (filter, mipmap, nén, alpha, padding atlas): đủ và đúng với loại asset theo bảng import trong [Sản xuất asset 2D](../zps-asset-2d/references/production.md); UI theo [Godot handoff](../zps-ui/references/ui-godot-handoff.md) khi project dùng Godot. Không mở engine. Ghi mức đã đạt: export đã kiểm; import và thiết bị để cho người đưa vào game.
5. Soi bảng lỗi ảnh gen trong [gen craft](../.art-production-support/shared/gen-craft.md); chi tiết không truy được về brief là issue. Review giao cho người/agent khác: gửi theo [review request](../.art-production-support/templates/review-request.md).
6. Review nhanh: nêu vài vấn đề có bằng chứng, không bắt buộc score/ID. Khi theo dõi revision hoặc nghiệm thu, ghi issue theo [mẫu review](../.art-production-support/templates/review.md) — cùng trường với AD: id, priority, region, viewing_condition, evidence, consequence, confidence, repair, preserve, acceptance, status.
7. Ưu tiên 1–3 việc tác động lớn nhất; giữ danh sách đầy đủ khi tracked.
8. Bản sửa: giữ id, chỉ `resolved` khi ảnh mới chứng minh acceptance; tìm regression và điểm mạnh bị mất.

Đọc [phương pháp sâu](../.art-production-support/shared/visual-review.md) khi nhiều tiêu chí, nhiều vòng hoặc nguyên nhân chưa rõ.

## Kiểm chuyên môn 2D (chọn theo loại asset)

| Loại | Kiểm gì | Công cụ |
|---|---|---|
| Mọi asset | Đọc được ở kích thước hiển thị trên nền game; phân biệt được với asset cùng bộ; không có phần tử ngoài brief | `preview.py sheet` |
| Bộ asset | Cùng góc nhìn, độ dày nét, mức chi tiết, hướng sáng, scale vật và khoảng đệm với asset mẫu | `preview.py compare` |
| Alpha | Không halo/fringe trên nền sáng và tối; không nền giả trong suốt; không crop mất phần | `inspect_image.py`, `sheet` nền tối |
| Canvas/pivot | Đúng kích thước file, pivot/baseline theo hợp đồng | `inspect_image.py` |
| Frame sequence | Pivot không rung giữa frame; volume, phụ kiện, màu nhất quán; không auto-crop từng frame; quỹ đạo và khoảng cách pose hợp lý, không giật | `sprite_check.py`; `anim_preview.py` (filmstrip + onion skin để xem; GIF cho người duyệt) |
| Tile | Nối liền bốn cạnh; không có dấu nổi bật lộ nhịp lặp khi trải nhiều ô | `preview.py tile` |
| Pixel art | Grid, cluster sạch, đúng palette; không bị resample bilinear | `palette_report.py` khi có palette |
| Decal | Alpha và blend đúng trên vật liệu đích; mép không lộ viền; scale khớp vật xung quanh | Xem trên ảnh nền/vật liệu thật |
| Background | Đủ vùng cho parallax/occlusion theo scope; camera và scale khớp gameplay; không tranh chú ý với nhân vật và UI | `preview.py compare` với ảnh gameplay |
| UI | Đúng wireframe; đủ state; 9-slice đúng ở min/max; chữ dài và tiếng Việt có dấu không tràn/cắt; vùng chạm sau scale | [UI QA](../zps-ui/references/ui-qa.md) |

## Khi Asset 2D hoặc UI gọi

Asset 2D và UI tự gọi skill này khi giao cả bộ, giao bản final, hoặc làm màn hình UI. Asset lẻ và sửa nhỏ chỉ cần self-check của skill sản xuất.

- Khi môi trường cho phép, chạy review trong một subagent mới. Subagent chỉ nhận asset, brief, style sheet, asset mẫu và ghi chú import; không nhận quá trình làm. Ghi là review độc lập.
- Không chạy được subagent: ghi rõ là tự review.
- Có issue: skill sản xuất sửa, rồi vòng sau chỉ kiểm lại các issue đã mở và regression, không review lại toàn bộ. Số vòng theo budget của task.

## Output

Điểm mạnh cần giữ → issue ưu tiên → việc tiếp theo → phần chưa đủ bằng chứng (ví dụ chưa xem trong engine/thiết bị; nhịp animation chưa có người xem) → mức đã đạt (export đã kiểm / import / thiết bị) → verdict: meets_checked_criteria / needs_revision / insufficient_evidence. Ghi self-review hay reviewer độc lập thật. Verdict không phải AD approval.

## Gotchas

- Không bịa lỗi để có đủ danh sách; "không cần sửa" là kết luận hợp lệ.
- Phóng to để soi chi tiết, nhưng kết luận về khả năng đọc phải dựa trên kích thước đích.
- So lệch bộ phải so với asset mẫu của bộ, không so với reference cảnh hay concept.
- Stylization có chủ ý không phải lỗi anatomy/phối cảnh.
- Agent không xem được GIF chuyển động. Quỹ đạo, khoảng cách pose và chỗ giật kết luận từ onion skin; nhịp và cảm giác chuyển động ghi `not_checked` trừ khi người đã xem GIF hoặc chạy trong game.
- Ảnh tĩnh không chứng minh cảm giác chạm, flow hay safe area trên thiết bị.
- Vấn đề flow/UX: ghi cho UX/game design, không chấm là lỗi art.
- Khi được giao cả sửa: chuyển issue cho skill sản xuất, không review lại toàn bộ.
- Issue ngoài phạm vi role: ghi issue, đánh dấu ngoài phạm vi; không tự sửa.

[Gate kỹ thuật](../.art-production-support/shared/scripts/README.md#evidence-gate) chỉ khi caller cần nghiệm thu máy đọc được.
