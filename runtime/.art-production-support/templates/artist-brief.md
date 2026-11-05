# Artist Brief — cùng mục với AD `art-bible-artist-direction` v0.1.0

Khi AD đã giao brief, dùng brief đó, không chép lại. Khi user mô tả trực tiếp, artist tự điền mẫu này ở mức tối thiểu; mục chưa biết ghi `?` hoặc `giả định: ...`. Brief tự lập là đề xuất, không phải AD approval.

```markdown
# Brief <asset/task> — source: AD | user-direct | 3D-request — status: draft | confirmed

## Mục đích
- Asset để làm gì, người chơi dùng/nhìn nó thế nào:
- Vị trí trong game/thế giới:
- Điều kiện xem đích (camera, kích thước hiển thị px, nền):

## Style
- Art Bible version: <hoặc "chưa có">
- Style sheet: <link/version nếu tự đọc>
- Rule áp dụng (chỉ phần liên quan):

## Cố định / được khám phá
- Cố định (silhouette, màu nhận diện, tỷ lệ...):
- Được khám phá:

## Reference
| ID | Vai trò (Inspiration/Execution/Avoid) | Lấy gì | Không lấy gì |
|---|---|---|---|

## Deliverables
- Subject / biến thể / states / views:
- Kích thước pixel, alpha, format, source editability:
- Ràng buộc kỹ thuật (Godot import, atlas, UV, shader) — không bịa số:
- Nơi giao:

## Checkpoint và nghiệm thu
- Checkpoint (thumbnail / bản thử / final) và người duyệt:
- Tiêu chí nghiệm thu quan sát được ở điều kiện đích:
- Budget lượt gen/edit:

## Câu hỏi còn mở
```

Tiêu chí nghiệm thu tốt: "Icon kiếm phân biệt được với icon rìu ở 64px trên nền panel tối, không chữ, không hiệu ứng sáng". Kém: "đẹp, đúng style".
