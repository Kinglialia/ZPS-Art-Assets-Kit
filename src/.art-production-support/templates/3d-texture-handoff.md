# Bàn giao 3D ↔ Texture

Mẫu chung cho 3D Artist và Texture Artist. 3D điền phần A khi gọi Texture; Texture điền phần B khi trả kết quả. Task nhỏ chỉ ghi các dòng liên quan, trong record hiện có.

## A. 3D → Texture (yêu cầu)

```markdown
# Texture cho <asset> — model v<số>, UV v<số>
- File model: <đường dẫn GLB/FBX>
- Lý do gọi: model mới | sau retopo, texture cũ không đạt (nêu lý do) | khác: …
- Cách làm texture: <theo yêu cầu của …> | chưa ai yêu cầu (Texture tự chọn)
- UV: UV0 có/không; chồng/mirror/stack có chủ đích ở: <vùng> | không có; trong 0–1 | tile
- Cách làm texture đã biết lúc unwrap: <cách, nguồn> | chưa biết (UV riêng, không chồng)
- Vùng vật liệu: <phần → vật liệu, ví dụ thân → gỗ, đai → kim loại> (từ trường `material` trong part_graph.json khi self-build); ảnh `parts_<view>.png`: <đường dẫn>
- Material: một material (mặc định) | đã tách slot theo yêu cầu của Texture Planning: <slot → vùng>
- Kiểm UV: kết quả uv_check <đường dẫn JSON>; ảnh checker <đường dẫn>
- Camera và kích thước trên màn hình: <từ spec>
- Map đã bake (normal/AO…) và quy ước: <có/không, đường dẫn>
- Texture tạm từ pipeline 3D (chiếu concept/bake): <có/không, đường dẫn> — bản tạm, Texture quyết định giữ/sửa/làm lại
- Concept/view dùng; mặt khuất là suy luận: <vùng>
- Engine: <Godot/…>
```

## B. Texture → 3D (kết quả)

```markdown
# Texture <asset> — cho model v<số>, UV v<số>
- Cách làm đã dùng: <author × shader> — <theo yêu cầu của … | tự chọn vì …>
- Map/atlas giao: <file, kích thước, kênh, color space>
- Gắn vào material slot: <slot → map>
- Ghi chú thiết lập material cho người đưa vào engine: lit | unlit; nén; mipmap bật/tắt; ảnh nào là normal map (quy ước OpenGL/DirectX)
- Render on-model đã mở: <đường dẫn, renderer>
- Yêu cầu 3D sửa UV hoặc tách material slot (nếu có, gom một lần): <…>
- Phần chưa kiểm / còn lỗi:
```

## Quy tắc dùng

- Mặc định một material và UV riêng, không chồng. Thông tin vùng vật liệu đi theo bảng "phần → vật liệu" và ảnh parts, không cần material slot riêng. Chỉ tách slot khi Texture Planning yêu cầu shader khác nhau theo vùng.
- Texture cần UV khác hoặc slot riêng: gom mọi yêu cầu vào một lần gửi cho 3D.

- Texture tự đo những gì đo được bằng `inspect_model.py` (UV, material, vertex color, texel density); không hỏi lại các mục đó.
- Chỉ hỏi những gì không đo được: ý đồ UV chồng, vùng nào là vật liệu gì, camera. Thiếu nhiều mục thì gom thành **một lần hỏi**.
- Model hoặc UV đổi version sau khi gửi: phần A phải gửi lại; texture làm cho version cũ phải kiểm lại.
