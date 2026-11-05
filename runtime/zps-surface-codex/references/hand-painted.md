# Stylized hand-painted

## Khóa mục tiêu ánh sáng

Chọn theo brief: unlit có ánh sáng vẽ sẵn, stylized lit với một phần shading chủ ý, hay base color painted dưới PBR. Không suy từ chữ hand-painted. Ánh sáng bake vào màu đi theo object khi object quay; phải kiểm phạm vi xoay/ánh sáng của game.

## Tiến trình author có thể điều chỉnh

1. **Mảng nền và hierarchy:** xác định vùng vật liệu và độ sáng tương đối trên model. Chưa cần noise; khối lớn và dấu nhận diện phải đọc ở kích thước game.
2. **Cấu trúc bề mặt:** chia tấm gỗ, thớ, đường may, nếp lớn, mặt đá theo nguyên nhân tạo thành. Hướng nét mô tả khối, có nhóm và khoảng nghỉ.
3. **Màu có quan hệ:** thay đổi hue/value/saturation có chọn lọc theo vật liệu, môi trường và ý đồ. Bóng lạnh/highlight ấm là một lựa chọn, không quy tắc. Không dùng saturation hoặc gradient để che phân mảng sai.
4. **Ánh sáng được phép:** với unlit, mô tả mặt, tiếp xúc và chiều sâu theo rig giả định; với lit, tránh highlight/specular và bóng đổ cố định trừ hiệu ứng đã chốt. AO/art shading phải kiểm không làm bẩn/đen kép dưới shader.
5. **Cạnh và điểm nhấn:** độ dày, độ sắc và cường độ nét thay đổi theo khối/scale/style; không tô mọi mép bằng một đường sáng. Highlight phải có lý do ánh sáng hoặc ngôn ngữ minh họa đã duyệt.
6. **Dấu sử dụng và polish:** thêm đúng nơi góp câu chuyện/nhận diện; giữ vùng nghỉ. Thu nhỏ thường xuyên, bỏ hoặc tổ chức lại chi tiết chỉ tạo nhiễu trong điều kiện đích.

Không bắt mọi asset đủ sáu lớp/source layer này; đây là thứ tự quyết định, không tiêu chí chấm hình. Layer chỉ được khai là có khi thực sự tồn tại trong source.

## Kiểm và tra cứu thêm

Xem base-color/unlit view khi cần tách nét khỏi shading, rồi shader thực. Giữ biểu đạt tổng thể; không tối đa contrast, sắc nét hoặc độ bẩn. Recipe gỗ/đá/vải và kỹ thuật stroke chỉ có tại [painting practice](painting-practice.md), đọc khi cần ví dụ để giải quyết vùng khó; không là bước bắt buộc.
