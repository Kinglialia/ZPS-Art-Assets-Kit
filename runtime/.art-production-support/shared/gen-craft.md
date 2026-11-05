# Gen craft — viết yêu cầu cho tool gen/edit và soi lỗi ảnh gen

Đọc trước khi gọi tool tạo/sửa ảnh và khi tự kiểm output. Áp dụng cho mọi tool (Codex `image_gen`, API ảnh, edit có mask).

## Contents
- Viết yêu cầu
- Lỗi đặc trưng của ảnh gen

## Viết yêu cầu

1. **Đưa ảnh Execution reference vào tool** khi tool nhận ảnh; ghi vai trò từng ảnh (Image 1: style/màu chuẩn; Image 2: structure only…). Chữ mô tả style không thay ảnh: prompt chỉ có chữ dễ trôi sang kiểu render khác.
2. **Chọn reference theo màu**: model bám màu ảnh hơn mã hex. Reference lệch tông so với style sheet → bỏ, hoặc ghi "structure only, ignore its colors".
3. **Gọi đúng tên loại ảnh đích** theo deliverable: "in-game screenshot of a real-time 3D game", "game UI icon on transparent background", "tileable texture, flat lighting"… Từ "concept art", "illustration", "keyframe" kéo về tranh vẽ.
4. **Mô tả bằng danh từ cụ thể**: vật, vật liệu, góc nhìn, bố cục. Không chồng tính từ ("epic, highly detailed, intricate" là lệnh thêm chi tiết). Kinh nghiệm với các tool đã thử (chưa kiểm rộng): tính từ màu mạnh ("vivid", "saturated", tên màu viết hoa) hay làm màu vượt đích; khi có ảnh chuẩn màu, ưu tiên "match the colors of Image N".
5. **Luôn ghi ràng buộc loại trừ**: không chữ, không logo, không phụ kiện/hiệu ứng ngoài danh sách, nền theo hợp đồng.
6. **Edit**: ghi "change only X; keep everything else unchanged" và nhắc lại mỗi lượt; dùng mask khi tool có. Khi yêu cầu giữ hình/bố cục, chạy `structure_diff.py` so với ảnh gốc; task chủ đích đổi cấu trúc thì so bằng mắt các vùng phải giữ.
7. **Ghi lại** prompt, ảnh đầu vào và vai trò, tool/model, tham số vào task record.

## Lỗi đặc trưng của ảnh gen

Mở ảnh ở kích thước đích **và** phóng to vùng chi tiết. Phân mức theo mẫu review: **blocker** khi lỗi làm hỏng yêu cầu bắt buộc hoặc khả năng đọc/phân biệt gameplay ở điều kiện xem đích; **major** khi ảnh hưởng chất lượng/nhất quán đáng kể; **minor** khi chỉ là polish. Lỗi nhìn thấy được chưa tự động là blocker; lỗi thêm thắt ngoài brief vẫn phải ghi và xử lý.

| Nhóm | Dấu hiệu cần bắt |
|---|---|
| Thêm thắt | Hoa văn phủ mọi bề mặt; ngọc, dây, đai, quai không công năng; motif nhân bản; hạt sáng, bokeh, sparkle, glow, khói, lá bay không được yêu cầu; đồ vật lạ ở nền |
| Cấu tạo | Ngón tay thừa/dính, chi không nối thân, khớp cơ khí không chịu lực, dây xuyên vật, đối xứng sai một bên |
| Chữ & ký hiệu | Chữ giả, glyph vô nghĩa, logo/watermark mờ, rune trang trí ngoài brief |
| Ánh sáng | Nhiều hướng sáng mâu thuẫn, rim light quanh mọi cạnh, bóng đổ không khớp nguồn, highlight bóng loáng trong style matte/flat, toàn ảnh ám tông khác reference |
| Bề mặt | Noise/vân giả làm "chi tiết", gradient airbrush trong style cel/flat, cạnh nhòe, texture đổi scale giữa hai vùng cùng vật liệu |
| Style trôi | Kiểu render khác reference (minh họa thay vì game render…), nét/độ bão hòa khác, bán-realistic chen vào stylized |
| Phối cảnh | Hai điểm tụ cho cùng họ cạnh, ellipse sai mặt phẳng, vật trôi không chạm sàn |
| Kỹ thuật | Halo/fringe trên alpha, nền giả trong suốt, crop mất phần, kích thước khác hợp đồng |
