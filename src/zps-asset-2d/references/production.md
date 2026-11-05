# Sản xuất asset 2D cho game

Nhận loại output: icon, sprite, tile, decal, portrait, background hay frame sequence. Canvas, pivot, safe area, target size, states và source editability là các yêu cầu độc lập; DPI không thay pixel dimensions. Kiểm prototype trong layout/game khi có.

Icon: silhouette và điểm nhận diện ở kích thước nhỏ, nhịp/scale đồng bộ trong bộ; không cố nhét mọi chi tiết concept. Sprite: giữ pivot, baseline và khoảng crop; không auto-crop từng frame làm nhân vật rung. Frame sequence: kiểm pose, volume, phụ kiện, màu và nhịp khi chạy thật; tĩnh không chứng minh animation. Background: các lớp đủ vùng parallax/occlusion theo scope, giữ camera và scale.

Tile: kiểm biên nối, lặp nhiều ô và dấu nổi bật bị lặp. Atlas cần extrusion/padding đúng importer; transparent pixels cũng có thể làm viền sai khi lọc. Decal kiểm alpha/blend trên vật liệu đích. Với pixel art: grid, cluster, palette và filtering theo project; không tự resample bằng bilinear.

Giữ source có lớp khi công cụ thực tạo được; file phẳng chỉ là file phẳng. Export rõ resolution, alpha mode, frame order/duration, pivot và tài nguyên phụ thuộc. Kiểm nền sáng/tối/nền game; metadata không chứng minh edge sạch.

## Godot 4 — đề xuất import cho asset 2D

Thông số project lấy từ tech profile; dưới đây là điểm phải đề xuất rõ khi giao, không tự sửa `.import` hay project settings ngoài quyền. Theo [tài liệu import của Godot](https://github.com/godotengine/godot-docs/blob/master/tutorials/assets_pipeline/importing_images.rst): mặc định 2D là Lossless, không mipmap; filter/repeat từ Godot 4 đặt ở CanvasItem (project setting làm mặc định), không nằm trong import.

| Loại | Đề xuất cần ghi | Lý do kiểm |
|---|---|---|
| UI icon/sprite hiển thị gần 1:1 | Lossless, mipmap tắt; filter Linear ở CanvasItem | Giữ nét icon nhỏ; mipmap tăng ~33% bộ nhớ mà không lợi khi không thu nhỏ |
| Sprite thu nhỏ mạnh theo camera | Bật mipmap; xem ở mức zoom xa nhất | Tránh lấm tấm khi thu nhỏ |
| Pixel art | Lossless, không mipmap; filter Nearest; scale nguyên lần | Giữ cạnh pixel |
| Background lớn | Cân nhắc VRAM Compressed (mặc định ETC2 trên mobile, ASTC khi bật high quality); kiểm banding | Bộ nhớ mobile |
| Có alpha | Straight alpha; giữ Fix Alpha Border (mặc định bật) | Giảm viền tối khi lọc bilinear |
| Atlas | Padding/extrude giữa ô theo tech profile | Tránh lem màu ô bên |

Giao ảnh đã kiểm và ghi mức: export đã kiểm / đã import Godot / đã xem trên thiết bị. Web export để mục riêng sau. Thu nhỏ là diagnostic, không chứng nhận gameplay readability hay accessibility.
