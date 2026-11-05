# Đọc style từ reference thành style sheet

Dùng khi nhận concept/reference style mà chưa có Art Bible hoặc Artist Brief của AD đủ để vẽ. Mục tiêu: một style sheet ngắn mà người khác đọc xong vẽ ra cùng một ngôn ngữ, mỗi rule có bằng chứng nhìn thấy trên ảnh.

## Contents
- Khi nào tự đọc, khi nào chuyển AD
- Quy trình 5 bước
- Mẫu style sheet và ví dụ

## Khi nào tự đọc, khi nào chuyển AD

| Tình huống | Làm gì |
|---|---|
| Có Bible/Brief của AD, reference minh họa đúng Bible | Dùng Bible; style sheet chỉ ghi phần Bible chưa nói (ví dụ nét ở icon 64px) |
| Có reference thống nhất, chưa có Bible | **Tự đọc style**, trình style sheet + 1 bản thử để user/AD xác nhận trước khi làm loạt. Asset 2D và UI: làm cả bộ rồi trình duyệt một lần (xem [asset mẫu](set-anchor.md)) |
| Reference mâu thuẫn (khác render, khác ánh sáng, khác tỷ lệ) mà brief không nói ưu tiên | Nêu mâu thuẫn cụ thể; đề xuất chuyển AD (`art-style-development`) hoặc hỏi user chọn reference chủ đạo |
| Cần đặt style cho cả project/IP mới | Việc của AD; artist chỉ hỗ trợ bản thử khi được giao |

Không tự trộn hai style mâu thuẫn thành "trung bình".

## Quy trình

1. **Mở mọi reference thật**, gán ID (R1, R2…) và vai trò: Inspiration / Execution reference / Avoid. Chỉ Execution reference là chuẩn để so pixel/nét; Inspiration chỉ cho mood/nguyên tắc.
2. **Đo, không đoán**: `preview.py compare` cho bộ reference cùng chiều cao; `preview.py value`; `palette_report.py` lấy palette thật; `score_variants.py --profile` lấy màu trung bình 5% pixel tối nhất, cast màu từng dải sáng và value p2/p50/p98. Với tiêu chí màu dễ bị mô tả sai bằng lời (màu vùng tối, cast ánh sáng), ghi kèm số đo này làm mốc kiểm; số đo hỗ trợ câu hỏi cụ thể, không thay phán đoán về quan hệ màu, ánh sáng và mục tiêu biểu đạt.
   Ghi palette riêng cho từng reference: reference lệch tông so với số đông thì đánh dấu "structure only" khi đưa vào tool gen.
3. **Điền các trục ảnh hưởng task** trong 12 trục của mẫu dưới (icon đơn lẻ có thể chỉ cần vài trục; style sheet cho cả loạt asset cần nhiều hơn). Trục không xét ghi "chưa xét", không bịa. Mỗi trục đã điền: quan sát cụ thể kèm ID ảnh → rule có thể làm theo → biên độ cho phép → độ tin (cao khi ≥2 Execution reference đồng ý).
4. **Ghi điều cần tránh, có nguồn**: chỉ ghi là *cấm* khi brief/AD nói rõ, hoặc mọi Execution reference nhất quán tránh và có lý do nhìn thấy được (ví dụ viền đen sẽ phá ngôn ngữ viền màu). Thứ chỉ "chưa thấy" trong vài reference ghi là *chưa thấy trong reference*, dùng để soi chi tiết lạ, không phải luật cấm.
5. **Làm 1 bản thử** trên subject mới không có trong reference, chạy `preview.py compare` với Execution reference ở cùng kích thước, chấm từng trục: khớp / lệch / chưa kiểm. Sửa style sheet hoặc ảnh, tối đa theo [chuẩn chất lượng](../rules/art-quality.md).

## Mẫu style sheet

```markdown
# Style sheet <tên> v<số> — status: proposed | confirmed_by:<người>
Nguồn: R1 (Execution), R2 (Execution), R3 (Inspiration), R4 (Avoid)

| Trục | Quan sát (ảnh) | Rule | Biên độ | Tin |
|---|---|---|---|---|
| Render | | | | |
| Nét (có/không, độ dày theo kích thước, màu) | | | | |
| Shape language | | | | |
| Tỷ lệ (đầu–thân, độ phóng đại) | | | | |
| Value (dải, key, vùng tối nhất) | | | | |
| Palette (họ màu, bão hòa, màu bóng) | | | | |
| Ánh sáng (hướng, vẽ sẵn hay dynamic) | | | | |
| Vật liệu (mức đơn giản hóa) | | | | |
| Cạnh (sắc/mềm ở đâu) | | | | |
| Mật độ chi tiết & vùng nghỉ | | | | |
| Dấu brush/texture | | | | |
| Camera/góc nhìn | | | | |

Tránh (nguồn: brief/AD/reference): ...
Chưa thấy trong reference (để soi, không phải luật): ...
Bản thử: <file> — kết quả so: ...
Câu hỏi còn mở: ...

## Ghi chú sản xuất (cập nhật sau mỗi task)
- Bộ reference đưa vào tool gen và vai trò (style/màu chuẩn · structure only):
- Số đo chuẩn (`--profile`): màu 5% tối nhất, cast từng dải, value p2/p50/p98:
- Cách sửa đã hiệu quả / không hiệu quả với style này (kèm task record):
```

Ghi chú sản xuất là nơi lưu bài học riêng của style/project; không ghi vào file skill.

## Ví dụ một dòng tốt và một dòng kém

- Tốt: `Nét | R1, R2: viền màu nâu đậm (không đen), dày ~3px ở icon 128px, mảnh dần ở đầu nhọn | Viền màu tối của vật liệu, 2–3% cạnh dài vật | ±1px | cao`
- Kém: `Nét | đẹp, mềm mại | dùng nét đẹp` — không quan sát, không làm theo được.
