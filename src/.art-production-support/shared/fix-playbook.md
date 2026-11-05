# Fix playbook — chọn cách sửa theo triệu chứng

Đọc khi ảnh chưa đạt và phải chọn bước tiếp. Thứ tự cách sửa dựa trên thử nghiệm thật; độ tin ghi theo lượng bằng chứng (thấp = một subject/style/tool). Bằng chứng chi tiết nằm ở repo nguồn (`research/trials/`), không nằm trong package.

## Contents
- Quy trình chọn
- Đo bằng gì theo deliverable
- Bảng triệu chứng → cách sửa
- Chọn phương án
- Ghi bài học và khi nào dừng

## Quy trình chọn

1. **Chẩn đoán bằng số + mắt.** Số cho biết lệch ở đâu; mắt thấy cái số không thấy (kiểu render, chi tiết lạ, cấu tạo).
2. **Phân loại lỗi**: *cấu trúc* (render, hình, bố cục, phần tử) · *màu/tông* (cast, palette, value) · *cục bộ* (một vùng) · *kỹ thuật* (alpha, canvas, pivot, seam).
3. **Chọn cách rẻ nhất có bằng chứng** theo bảng. Cấu trúc đã đạt → ưu tiên cách xác định (script, edit cục bộ) trước gen lại.
4. **≥2 giả thuyết**: chọn thử tuần tự (giả thuyết khả năng cao/rẻ nhất trước) hoặc song song khi budget cho phép và song song rẻ hơn tổng số lượt; mỗi nhánh đổi đúng một yếu tố. Không tự tăng budget hay số agent để thử song song.
5. Khi có nhiều phương án, **chấm lại cùng lúc** trong cùng điều kiện, review mắt top 2–3, chọn và ghi lý do.

## Đo bằng gì theo deliverable

Reference để chấm phải **cùng loại** với đầu ra.

| Deliverable | Reference để so | Công cụ |
|---|---|---|
| Concept/cảnh | Execution reference cùng loại cảnh | `preview.py compare`, `value`; `score_variants.py` |
| Icon/sprite/asset bộ | Asset mẫu đã duyệt trong cùng bộ | `preview.py sheet` (kích thước đích, nền game), `compare`; `score_variants.py`; `inspect_image.py`; `sprite_check.py` cho frame |
| Tile/background | Tile/background đã duyệt | `preview.py tile`, `compare` |
| Texture trên model | Render on-model của asset đã duyệt cùng ánh sáng | `render_model.py` nhiều góc + `compare` |
| Bản edit của ảnh có sẵn | Ảnh gốc | `structure_diff.py` (giữ hình), `inspect_image.py --lock-mask` (giữ pixel) |

## Bảng triệu chứng → cách sửa

| Triệu chứng | Đo | Thử trước | Thử sau | Không nên | Tin |
|---|---|---|---|---|---|
| Sai kiểu render (ra minh họa 2D, painterly, bán-realistic…) | Mắt, `compare` | Gen lại **có ảnh Execution reference**, gọi đúng tên loại ảnh đích | Đổi/thêm reference đúng kiểu render | Thêm tính từ style vào prompt chữ | trung bình |
| Palette lệch toàn ảnh, cấu trúc đạt | `score_variants` cast_*, off_palette | `tone_match.py --bands shadows midtones`, rồi `structure_diff` xác nhận giữ hình | Edit "change only colors" kèm ảnh chuẩn màu, rồi `tone_match` kéo về | Gen lại toàn ảnh chỉ vì màu; hex trong prompt; tính từ màu mạnh | trung bình |
| Màu bị kéo theo một reference lệch tông | Palette/`--profile` từng reference | Bỏ reference lệch tông hoặc đánh dấu "structure only" | Giảm số reference | Thêm reference "cho đủ" | thấp |
| Vùng tối/ánh sáng sai tông (nâu thay vì xám lạnh, cam thay vì trung tính) | `score_variants` dark_hue_gap, cast_shadows/highlights | `tone_match` đúng dải; không chỉnh dải sáng khi trời/highlight đã đúng | Gen lại với reference đúng ánh sáng làm chuẩn màu; kiểm lại kiểu render | Mô tả màu tối bằng lời trong prompt | thấp |
| Chi tiết lạ, phần tử ngoài brief | Kiểm kê phần tử | Edit cục bộ xóa (mask nếu tool có); `structure_diff` kiểm phần còn lại | Gen lại với danh sách loại trừ rõ hơn | Giữ vì "trông đẹp" | chưa thử |
| Lệch bộ: nét, góc nhìn, mức chi tiết, hướng sáng khác asset mẫu | `sheet` + `compare` cạnh asset mẫu, cùng kích thước | Gen lại với asset mẫu của bộ làm reference chính | Edit cục bộ vùng lệch | So với reference cảnh thay vì asset mẫu | chưa thử |
| Cấu tạo/phối cảnh sai một vùng | Mắt, phóng to | Edit cục bộ + nhắc invariant; `structure_diff` vùng ngoài | Gen lại với reference cấu tạo | Sửa màu để che | chưa thử |
| Texture không theo khối, seam lộ, sáng/bóng vẽ theo atlas | `render_model` checker + textured nhiều góc | Sửa trên UV/paint view theo hướng khối, render lại | Báo UV cho 3D Artist | Đánh giá trên atlas phẳng | chưa thử |
| Sprite trôi pivot/baseline, canvas lệch | `sprite_check.py` | Đặt lại canvas/pivot bằng script | Gen lại frame lệch với frame chuẩn làm reference | Auto-crop từng frame | chưa thử |
| Mất alpha, halo, nền giả trong suốt | `inspect_image --require-alpha`, `sheet` nền tối | Yêu cầu nền trong suốt thật; tách nền lại | — | Tin alpha có là sạch | chưa thử |

Script màu (`tone_match`, `score_variants`) bỏ qua pixel trong suốt và giữ alpha.

## Chọn phương án

- **Mắt trước** (bắt buộc): đúng kiểu render, kiểm kê phần tử, bảng lỗi ảnh gen, 6 chiều tự kiểm.
- **Số sau, chỉ để phân xử**: số đo giúp loại phương án lệch rõ và phân xử khi các phương án đạt mắt gần ngang nhau. Total `score_variants` thấp hơn không tự chứng minh phương án tốt hơn về art; trọng số là ước lượng chưa calibrate, chỉ so total trong cùng lần chấm, cùng reference. Số đo màu không thấy kiểu render, cá tính hay biểu đạt.
- Bản edit phải qua `structure_diff` nếu yêu cầu giữ hình.

## Ghi bài học và khi nào dừng

- Ghi cách đã thử, số trước/sau, lựa chọn vào **task record**; điều riêng của style/project (reference nào chỉ dùng cấu tạo, cách sửa đã hiệu quả) vào **mục Ghi chú sản xuất của style sheet**. Không sửa file skill đã cài.
- Phát hiện có vẻ đúng chung cho tool/loại lỗi: đề xuất owner kèm bằng chứng để cập nhật playbook ở repo nguồn.
- Dừng theo budget trong [chuẩn chất lượng](../rules/art-quality.md). Một loại lỗi đã thử ≥2 cách không tiến bộ: dừng, chẩn đoán lại và báo cách khác kèm bằng chứng (sửa tay trong DCC, đổi tool/model, đổi reference). Đổi tiêu chí là quyết định riêng của AD/owner, không phải cách để đạt pass.
