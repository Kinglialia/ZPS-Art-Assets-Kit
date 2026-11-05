# Stylized lit và PBR

## Tách nghệ thuật khỏi hợp đồng dữ liệu

Stylized có thể dùng PBR. Chọn tỷ lệ, palette, roughness distribution và chi tiết có chủ đích; không cần thêm micro-noise để “đúng PBR”. Độ đẹp và độ hợp lý vật liệu cần xem trên shader, không đọc từ histogram.

Với metallic-roughness, base color phi kim mô tả màu diffuse; kim loại mô tả phản xạ có màu. Kim loại có màu không đòi mọi kênh RGB cao như nhau. Metallic thường chọn vật liệu thuần 0/1; giá trị trung gian có thể do pha trộn/coverage, phải có ý nghĩa. Roughness điều khiển độ rộng/đặc tính phản xạ theo shader, không đồng nghĩa độ tối. Không suy cả roughness/height/normal đúng từ một ảnh RGB.

Texture màu thường được encode sRGB; map dữ liệu không áp chuyển sRGB. glTF dùng roughness G, metallic B và base-color RGB sRGB với alpha linear, straight alpha. Đó là hợp đồng glTF, không mặc định mọi engine cùng packing. Filament shader input dùng linear và quy ước alpha riêng; không lẫn shader value với bytes của texture. Normal theo tangent basis/convention thực, kiểm DirectX/OpenGL và mirrored UV, không chỉ đổi tên file.

## Author và chẩn đoán

Với look mới hoặc rủi ro chưa giải, làm material swatch trên bề mặt có nhiều hướng; dùng lại mẫu đã đạt nếu điều kiện còn đúng. Kiểm base color riêng, roughness/metallic và normal, rồi tổng hợp khi cần tìm nguyên nhân. Dùng neutral light để chẩn đoán và lighting của game để duyệt look; giữ exposure, tone mapping, camera, environment giữa bản so. Không dùng emissive để che màu tối trừ khi brief yêu cầu phát sáng.

Với dynamic lighting, tránh bake highlight hoặc cast shadow cố định vào base color. Một chút art shading có thể hợp stylized-lit nhưng cần kiểm trong vùng sáng/tối và góc xoay thực; không gọi đây là albedo vật lý sạch.

Normal không thay silhouette. Height cần scale/range và shader hỗ trợ. Roughness có thể thiết kế theo vùng lớn–vừa, tránh hạt li ti không ổn định ở mip thấp. Chi tiết biến mất khi thu nhỏ cần đánh giá trong mục tiêu, không tự tăng resolution.

## Bake và smart material

Bake chuyển chi tiết từ high-poly sang low-poly (normal, AO, curvature, thickness) để làm nền cho vật liệu. Cần: high-poly và low-poly khớp, UV low-poly không chồng ở vùng có chi tiết riêng, cage/khoảng ray phù hợp, cùng quy ước tangent với engine. Một owner bake (thường 3D Artist); artist dùng map bake làm mask cho mòn cạnh, bụi khe, không vẽ tay lại AO. Smart material (Substance…) là DCC ngoài khả năng tự chạy của role: đề xuất thông số, kiểm kết quả trên model. Godot có `ORMMaterial3D` dùng một texture gộp occlusion/roughness/metallic.

## Xác minh

Chọn kiểm theo thay đổi: repaint look cần xem phản ứng ánh sáng; đổi normal cần kiểm convention/tangent; chỉ repack cần đối chiếu giá trị từng kênh và import đích, không author lại swatch. Quay model hoặc đèn độc lập khi cần lộ phản xạ bị vẽ sai, inversion và seam. Kiểm compression/mip và runtime material thật khi thuộc đầu ra; Workbench/clay không xác nhận PBR. Chưa có engine thì giao mức đã kiểm trong DCC, ghi rõ runtime chưa kiểm. Nguồn chuẩn kỹ thuật: glTF 2.0, Filament và tài liệu engine phiên bản được chọn.
