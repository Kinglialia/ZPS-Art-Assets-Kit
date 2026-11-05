# UI handoff — chỉ giữ phần thuộc phạm vi

Dùng kèm [task record](../../.art-production-support/templates/task-record.md). Đường dẫn tương đối; không secrets hay đường dẫn riêng của máy.

```markdown
# UI handoff <màn hình/component> <bản> — mức xác nhận: thiết kế | Godot | thiết bị

## Ngữ cảnh
- Godot version, base size, stretch/aspect/scale, tỷ lệ hỗ trợ, orientation, safe area:
- Wireframe/đặc tả tương tác đã duyệt (nguồn):

## Đầu ra
| ID | File (PNG 1x/@2x) | Mục đích | Nguồn chỉnh sửa (SVG / raster gen / kết hợp) | Công cụ và cách xuất (ví dụ `svg_render.py --scales 1 2`) |
|---|---|---|---|---|

## Component
| ID/bản | Layout, sizing, Container/anchors | Chữ: font, fallback, overflow | State | Theme/StyleBox/asset |
|---|---|---|---|---|

## 9-slice
| Asset | Texture margin (L/T/R/B) | Content margin (L/T/R/B) | Stretch/tile | Min/max đã thử |
|---|---|---|---|---|

## QA
| Kiểm | Bản/môi trường/kích thước | Tiêu chí | Bằng chứng | Kết quả | Hiệu lực |
|---|---|---|---|---|---|

## Còn lại và tài nguyên ngoài
- Vấn đề, ai xử lý, có chặn bàn giao không:
- Font/tài nguyên: nguồn, license, attribution:
```
