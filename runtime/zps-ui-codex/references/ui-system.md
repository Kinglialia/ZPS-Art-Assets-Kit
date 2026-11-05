# UI system, hướng visual và nguồn/asset

## Contents
- Hai hướng visual
- Hệ thống vừa đủ
- Nguồn chỉnh sửa và xuất
- Quyền sử dụng

## Hai hướng visual

Chỉ khi project chưa có UI style. Dựng trên cùng wireframe và nội dung đã duyệt. Mỗi hướng nêu: cảm giác chủ đạo và liên hệ thế giới game; ngôn ngữ hình khối (silhouette, góc, độ dày, nhịp lặp); typography, vật liệu, mức trang trí; thứ tự chú ý; đánh đổi về khả năng đọc và công sản xuất; một khuyến nghị. Glow, gradient, đối xứng không phải lỗi mặc định: đánh giá theo style, trọng tâm và khả năng đọc.

## Hệ thống vừa đủ

| Nhóm | Đặc tả theo phạm vi |
|---|---|
| Màu | Vai trò nền, chữ, hành động, trạng thái/rarity; không dùng cùng tín hiệu cho ý nghĩa xung đột |
| Chữ | Font, cấp chữ, line height, outline/shadow, fallback, quy tắc chữ dài |
| Layout | Spacing, padding, alignment, minimum size, co giãn, overflow |
| Component | ID ổn định, cấu trúc, biến thể, state cần thiết, vùng chạm |
| Icon trạng thái | Hình khối, độ dày, chi tiết theo kích thước dùng thật |
| Trang trí | Frame, viền, vật liệu và giới hạn dùng |
| Motion | Mục đích, trigger, thời lượng đề xuất, phương án giảm motion nếu áp dụng |

Không tạo token, biến thể hay state chưa có nhu cầu. Hover không cần cho UI chỉ dùng touch.

## Nguồn chỉnh sửa và xuất

Có yêu cầu cụ thể về định dạng nguồn (AD, tài liệu Art Style, project) thì làm theo. Không ai nêu thì chọn theo loại UI và ghi lý do một dòng:

| Loại UI | Nguồn mặc định |
|---|---|
| Nút, panel, thanh, khung 9-slice phẳng hoặc gradient đơn giản; icon trạng thái dạng khối/nét; UI phẳng, sci-fi, tối giản | **SVG** (LLM viết được, sửa được trong Figma, sắc nét mọi kích thước) |
| Khung trang trí vẽ tay (gỗ, kim loại chạm, đá, fantasy nhiều họa tiết), illustration, nền | **Ảnh gen** theo [gen craft](../../.art-production-support/shared/gen-craft.md); raster riêng là nguồn illustration |
| Kết hợp | Khung SVG + một lớp texture raster; ghi rõ lớp nào là nguồn nào |

Luật cho SVG nguồn:
- **Chữ không nằm trong SVG.** Chữ là chữ sống trong engine. Chỉ logo hoặc tiêu đề trang trí mới chuyển thành path.
- **Mở được trong Figma:** chỉ dùng path, shape, gradient và group. Group đặt tên theo component/state (ví dụ `btn_play_pressed`), hoặc mỗi state một file. Không dùng filter, mask, script, foreignObject.
- Kích thước 1x của SVG (width/height theo px) bằng kích thước hiển thị ở base size của project.
- Xuất PNG bằng `svg_render.py` (xem [scripts](../../.art-production-support/shared/scripts/README.md#svg)); script báo khi SVG có chữ hoặc tính năng rủi ro.

`.tscn`, `.tres` không là nguồn mặc định. Không tạo được định dạng bắt buộc → báo trước khi sản xuất, đề xuất thay thế.

| Thành phần | Yêu cầu |
|---|---|
| Layout, chữ, nút | Sửa độc lập; chữ động tách khỏi trang trí, không nướng vào ảnh |
| Frame | Vùng cố định, vùng stretch/tile, content padding, size tối thiểu |
| Icon/illustration | Nguồn + bản xuất; raster riêng có thể là nguồn illustration |
| Background | Crop, tile, scale và vùng cần giữ |

Ghi chuỗi nguồn → công cụ/phiên bản và thao tác xuất → file runtime; liệt kê font và dependency, không đường dẫn riêng của máy. Kích thước xuất theo diện tích hiển thị và ngân sách; phân biệt kích thước ảnh, kích thước hiển thị và vùng chạm. Thử đổi chữ dài, thay icon hoặc resize một component rồi xuất lại; ghi kết quả.

## Quyền sử dụng

Tài nguyên đưa vào sản phẩm: ghi nguồn, tác giả, license, attribution; chưa xác minh → pending. Reference phân tích không tự được phép phát hành. Ảnh gen: ghi công cụ và vai trò.
