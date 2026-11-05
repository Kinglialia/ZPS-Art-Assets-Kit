# Tech profile — Godot mobile (Web: mục mở rộng sau)

Một file cho mỗi project, do lead kỹ thuật/AD xác nhận. Artist đọc file này thay vì đoán thông số. Ô trống là chưa biết: ghi giả định trong task, không tự điền vào profile.

```markdown
# Tech profile <project> — Godot <phiên bản> — status: draft | confirmed_by:<người>

## Màn hình đích
- Viewport thiết kế (px) và stretch mode/aspect:
- Thiết bị tham chiếu thấp nhất:
- Safe area / notch:

## Asset 2D
- Kích thước hiển thị icon/sprite chuẩn (px tại viewport thiết kế):
- Hệ số vẽ so với hiển thị (ví dụ vẽ 2x rồi để Godot scale):
- Filter mặc định (project setting/CanvasItem: Linear/Nearest), mipmap cho 2D:
- Atlas/AtlasTexture hay file rời; padding giữa ô:
- Alpha: straight; Fix Alpha Border (mặc định bật):
- Nén: Lossless / Lossy / VRAM Compressed theo loại asset:

## Texture 3D
- Shader: unlit / StandardMaterial3D / shader riêng:
- Texel density hoặc kích thước map theo loại asset:
- Color space: albedo sRGB, data maps linear; normal map convention (Godot dùng OpenGL Y+):
- VRAM Compressed mobile: ETC2 (mặc định) hay ASTC (high quality); mipmap (mặc định bật khi Detect 3D):
- Định dạng giao (PNG/glTF), quy ước tên map:

## Đặt tên & thư mục
- Quy ước tên file/state/frame:
- Thư mục giao trong project / Drive:

## Web (để sau)
- Giới hạn kích thước tải, định dạng ảnh, nén:
```

Ghi chú cố định cho Godot 4: import 2D và 3D cấu hình riêng trên từng texture (`.import`); đổi preset import là việc của người giữ project, artist chỉ đề xuất. Kiểm ảnh trong editor/thiết bị khi có quyền, không suy từ file PNG.
