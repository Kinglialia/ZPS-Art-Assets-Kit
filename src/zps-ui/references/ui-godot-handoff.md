# Bàn giao UI cho Godot

Mốc đối chiếu: tài liệu Godot 4.5 / 4.5-stable; **không phải yêu cầu phiên bản**. Tra đúng phiên bản project trước khi chỉ định thiết lập.

## Contents
- Ngữ cảnh hiển thị
- Layout và safe area
- Component, Theme, 9-slice
- Chữ và localization
- Asset và import
- Đối chiếu bản dựng

## Ngữ cảnh hiển thị

Ghi Godot version, orientation, base size, stretch mode/aspect/scale, khoảng tỷ lệ hỗ trợ ([Multiple resolutions](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/rendering/multiple_resolutions.rst)). Tách đơn vị thiết kế, đơn vị layout Godot và kích thước trên thiết bị: nút đủ lớn trong ảnh chưa chứng minh vùng chạm sau scale. Không đổi project settings để khớp screenshot.

## Layout và safe area

| Hạng mục | Đặc tả |
|---|---|
| Màn hình | ID, kích thước tham chiếu, khoảng tỷ lệ, nội dung mẫu |
| Bố cục | Phần cố định/co giãn, anchors hoặc Container gợi ý, minimum size, padding, alignment |
| Responsive | Khi nào wrap, cuộn, đổi số cột, crop; thứ tự ưu tiên giữ nội dung |
| Safe area | Phần nằm trong vùng an toàn, phần được phủ ra ngoài |
| Lớp UI | Lớp nhận thao tác, Back/close, modal — theo đặc tả UX đã duyệt |

Container sắp xếp Control con ([Containers](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/ui/gui_containers.rst)); phần không thuộc Container dùng [anchors](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/ui/size_and_anchors.rst). Không ghi đồng thời tọa độ tay mâu thuẫn. [`DisplayServer.get_display_safe_area()`](https://github.com/godotengine/godot/blob/4.5-stable/doc/classes/DisplayServer.xml) khác theo nền tảng: preview desktop chỉ chứng minh mô phỏng; Developer xác nhận trên thiết bị.

## Component, Theme, 9-slice

Ghi ID, biến thể/state, Control gợi ý, mapping tới màu, font, constant, StyleBox của project; không ép chọn node khi có cách tương đương.

9-slice: ghi **bốn texture margin** (phần giữ hình) và **bốn content margin** (khoảng cho nội dung) riêng, cách stretch/tile mỗi trục, min/max size đã thử. Content margin có thể lấy fallback từ texture margin ([StyleBoxTexture](https://github.com/godotengine/godot/blob/4.5-stable/doc/classes/StyleBoxTexture.xml)); khác nhau thì ghi rõ.

## Chữ và localization

Font/fallback, cỡ, line height, màu, outline/shadow, wrap/truncate, số dòng, overflow. Kiểm theo ngôn ngữ thật: chuỗi dài, tiếng Việt có dấu (clipping dấu, fallback), số lớn, placeholder đổi vị trí; RTL chỉ khi có ngôn ngữ liên quan. Pseudolocalization tìm lỗi độ dài nhưng không thay kiểm glyph thật ([Internationalizing games](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/i18n/internationalizing_games.rst)).

## Asset và import

Mặc định giao **PNG** ở kích thước base của project (thêm `@2x` nếu project cần), xuất từ SVG bằng `svg_render.py`, kèm **SVG nguồn** để sửa trong Figma hoặc xuất lại. Reviewer kiểm đúng các PNG này. Chỉ giao SVG để import thẳng khi developer hoặc project yêu cầu (ví dụ icon cần nhiều mức scale); khi đó ghi scale import đề xuất, và ghi rủi ro: Godot vẽ SVG bằng ThorVG, có thể lệch nhẹ gradient và độ dày nét so với PNG đã review; lề 9-slice tính theo kích thước sau scale.

Ghi file, ID, nguồn, kích thước xuất/dùng, alpha, mục đích, filter/scale đề xuất. SVG được rasterize khi import, chữ trong SVG phải thành path ([Importing images](https://github.com/godotengine/godot-docs/blob/4.5/tutorials/assets_pipeline/importing_images.rst)); giữ nguồn chữ chỉnh sửa được. Filter/repeat ở Godot 4 đặt ở CanvasItem, không trong import. Mipmap, nén, atlas: đề xuất, Developer chốt theo ngân sách.

## Đối chiếu bản dựng

Ghi bản thiết kế và build, viewport, state, nội dung. Mỗi sai lệch: vị trí, kỳ vọng, thực tế, ảnh hưởng, hướng sửa. Phân biệt thiếu thông số thiết kế với lỗi dựng; không khẳng định input, safe area, hiệu năng khi chưa thử trên môi trường tương ứng.
