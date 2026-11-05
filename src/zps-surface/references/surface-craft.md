# Thiết kế texture đẹp và có cá tính

Phần chung cho mọi phương pháp. Cách author (vẽ tay, flat color, procedural, ảnh…) và shader (unlit, lit/toon, PBR) là hai lựa chọn độc lập, do style sheet/Bible của project quyết định.

## Material intent trước map

Mỗi vùng ghi vật liệu/cách chế tác, scale, hướng cấu trúc, cách sử dụng, mức stylization và vai trò trong hierarchy. “Gỗ” chưa đủ: gỗ mềm sơn, gỗ thô đẽo hay gỗ đánh bóng tạo hình và phản ứng khác nhau. Đặc trưng phải đọc trong diện tích/pixel thực, không chỉ crop phóng to.

Tạo nét riêng từ quan hệ vật liệu và thế giới: cách chạm khắc, nối, vá, dệt; motif có logic và vài đặc điểm nổi bật được chọn. Dùng reference để hiểu nguyên lý, tránh lấy nguyên biểu tượng/chi tiết nhận diện. “Độc đáo” là đánh giá tương đối với nguồn đã xem, không chứng nhận chưa từng có.

## Bố cục bề mặt

Thiết kế mảng lớn/trung/nhỏ có chủ đích: vùng nghỉ, vùng cấu trúc, điểm nhấn. Không áp tỷ lệ phần trăm cố định. Theo mặt khối và camera game; seam UV không phải đường bố cục tự nhiên. Hướng nét/vân theo cấu trúc vật liệu, không theo cạnh atlas.

Màu, độ sáng, độ bóng và scale vân cùng tạo cảm giác chất liệu. Tách vật liệu bằng quan hệ đủ dùng; không bắt mỗi vùng phải tương phản cực mạnh. Chú ý màu lân cận và ánh sáng làm sai cảm nhận màu map.

Mỗi dấu mòn cần nguyên nhân: cầm nắm, ma sát, va chạm, nước đọng, nắng, bụi. Dấu có phân bố và hướng hợp lý; không phủ cạnh sáng/noise đồng đều. Stylized có thể cường điệu nguyên nhân nhưng giữ ngôn ngữ của game. Vùng chưa cần hao mòn có thể sạch.

## Cách thử tiết kiệm

Chọn vùng chứa tương tác quan trọng: gỗ–kim loại, mép vải–da, mặt đổi hướng và seam. Làm mảng nền/nhịp chính rồi gắn lên model ngay. Nếu nét không đọc do UV nhỏ, xác định nguyên nhân trước tăng resolution. Dùng mẫu còn hiệu lực thay vì thử lại từ đầu.

So bản cũ/mới trong cùng camera/đèn/exposure; xem model quay và kích thước đích. Nét “đẹp” trên atlas có thể sai hướng, thành noise hoặc mất hình trên model. Tách mục đạt mỹ thuật khỏi map hợp lệ kỹ thuật. Chỉ thêm polish giải quyết vấn đề thực, không mặc định thêm chi tiết làm tăng giá trị.
