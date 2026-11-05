> Vai trò trong skill này: "người giao việc", "người giữ chuẩn hình ảnh", "người duyệt" = người dùng. "Review độc lập" chỉ khi có reviewer tách biệt thực sự; không mặc định gọi subagent. Ngưỡng nằm trong `task/spec.json`; số đo lấy từ script trong `tools/`. Nguồn: skill art-3d-artist v0.1.0.

# Chọn và kiểm chứng giải pháp dựng

## 1. Phân tích trước khi chọn

Đọc concept, chuẩn hình ảnh, asset mẫu và tiêu chí task. Xác định camera, kích thước hiển thị, yêu cầu chuyển động/tương tác, engine/shader và budget đã biết. Thiếu dữ kiện ảnh hưởng lựa chọn thì nêu giả định cùng tác động.

Dùng ưu tiên đọc trong brief: chức năng/thông tin do người giao việc xác định, đặc trưng hình ảnh do người duyệt hình ảnh xác định. Xem tại các góc, khoảng nhìn và kích thước hiển thị được phép; không suy độ quan trọng chỉ từ diện tích trong concept hoặc ảnh render phóng lớn. Thiếu dữ kiện thì ghi đề xuất/giả định, chỉ hỏi phần làm thay đổi quyết định.

Phân loại chi tiết theo vai trò: hình khối/đường viền; cấu tạo và mối nối; chuyển động/tương tác; phản ứng ánh sáng; màu và hoa văn. Một chi tiết có thể giữ nhiều vai trò.

## 2. Chọn kỹ thuật theo tác dụng

| Kỹ thuật | Khi cân nhắc | Cần kiểm |
|---|---|---|
| **Geometry** | Chi tiết ảnh hưởng silhouette, độ dày, khoảng hở, chuyển động, bóng đổ hoặc tương tác | Hình ở các góc cần dùng; chất lượng có xứng chi phí geometry |
| **Bevel + custom/weighted normals** | Cạnh cần bắt sáng, mặt lớn cần shading ổn định | Bevel đủ thấy ở camera đích; không méo khối hoặc tạo shading lỗi |
| **Normal map** | Chi tiết cần thay đổi phản ứng ánh sáng nhưng không cần khối hoặc khoảng hở thật | Có đọc được ở kích thước đích; tangent, UV, compression và shader đúng |
| **Texture màu/hand-painted** | Phân vùng màu, hoa văn hoặc sáng tối theo style | Khớp ngôn ngữ hình ảnh; painted lighting phù hợp cách chiếu sáng đích |
| **Trim sheet/tiling** | Chi tiết hoặc vật liệu lặp trên nhiều bề mặt/asset | Scale, hướng pattern, seam, repetition và khả năng dùng chung material |
| **Decal** | Ký hiệu hoặc chi tiết cục bộ cần đặt độc lập trên bề mặt | Hỗ trợ của renderer, layering, chi phí và khả năng nhìn ở góc xiên |
| **Cards + alpha** | Hình mỏng như lá, tóc hoặc cụm chi tiết phù hợp mặt phẳng | Góc nhìn, silhouette, bóng, mip/alpha và overdraw; không mặc định rẻ hơn geometry |
| **Parallax/POM** | Bề mặt cần cảm giác sâu hơn normal map, shader đích hỗ trợ | Góc xiên, artifact, chi phí GPU và giới hạn tại mép vật thể |
| **LOD** | Asset xuất hiện ở nhiều kích thước hiển thị và giảm chi tiết có lợi | Mất silhouette, shading, chi tiết nhận diện và chuyển cấp; không ép tỷ lệ giảm cố định |

Phối hợp kỹ thuật theo từng phần của asset. Không chọn chỉ từ tên loại asset hoặc nền tảng; không áp ngưỡng độ sâu theo cm cho mọi trường hợp.

Chi tiết chỉ đổi màu/hoa văn ưu tiên texture màu hoặc material; chi tiết cần phản ứng ánh sáng nhưng không cần khối thật cân nhắc normal. Geometry giữ silhouette, độ dày, khoảng hở, bóng, chuyển động hoặc tương tác có ý nghĩa theo brief. Normal không thay đường viền hoặc cấu tạo đã bỏ.

Chưa chắc thì dùng phép thử nhỏ trong bước proof hiện có: bỏ geometry của vùng đại diện, thay bằng texture/normal phù hợp và so cùng camera/light/kích thước ở các góc sử dụng. Chấp nhận khi vẫn giữ ưu tiên đọc và chức năng; không kết luận phương pháp thất bại chỉ vì map thử chưa đúng. Có chuẩn/mẫu phù hợp thì dùng lại, không thử từng vết xước hoặc mở thêm gate. Phối hợp bên texture/material khi có; thay cách thể hiện đã duyệt vẫn phải trình người duyệt hình ảnh.

## 3. Chọn cách dựng hình

- **Mesh trực tiếp:** khối cần kiểm soát đỉnh, cạnh và topology cụ thể.
- **Curve/sweep:** hình chạy theo đường dẫn như dây, ống, viền và các cấu kiện cong.
- **Sculpt:** hình hữu cơ hoặc biến dạng cần xử lý trực tiếp trên bề mặt; retopo khi yêu cầu đích cần.
- **Boolean:** tạo giao/cắt phù hợp cấu tạo; kiểm kết quả shading và topology sau thao tác.
- **Procedural/modular:** cấu trúc lặp, có quy luật hoặc cần chỉnh nhiều biến thể; kiểm cả mối nối và sự lặp dễ nhận thấy.
- **Mesh từ generator:** dùng khi phù hợp quyền và công cụ; kiểm thiết kế, mesh, UV và export như mọi nguồn khác.

Có thể phối hợp nhiều cách. Chọn phương pháp giúp giữ thiết kế, sửa thuận lợi và đáp ứng đích sử dụng.

Dựng một bản runtime chính trong budget trước. Chỉ thêm LOD khi camera/kích thước hiển thị và yêu cầu đích có lợi; tạo từ source chung khi phù hợp, dùng chung texture/material nếu giữ được look. Không mặc định dựng ba bản Low/Medium/High độc lập hoặc giảm mặt theo phần trăm cố định. Bản sculpt high-poly để bake là nguồn riêng khi cần chi tiết bề mặt; không đồng nhất với mức chi tiết cao nhất của bộ LOD.

## 4. Dùng chuẩn hoặc thử nhỏ

Có chuẩn/asset mẫu còn phù hợp thì dùng lại, ghi phiên bản và điều kiện áp dụng. Khi xuất hiện rủi ro mới, chọn vùng nhỏ nhất đủ bộc lộ vấn đề và thử trước khi mở rộng.

Nếu cần so hai giải pháp, giữ cùng camera, kích thước hiển thị, ánh sáng và material tương đương. So chất lượng nhìn thấy, khả năng sửa và dữ liệu chi phí liên quan. Chưa đo runtime thì chỉ ghi chi phí dự kiến.

Ví dụ: so vết khắc bằng geometry và normal trên cùng một vùng; không dựng hai asset hoàn chỉnh chỉ để trả lời câu hỏi này.

## 5. Quyết định và chuyển duyệt

Ghi ngắn trong hồ sơ task: `phần cần thể hiện | kỹ thuật chọn | lý do | chuẩn/mẫu dùng lại hoặc kết quả thử | phần chưa kiểm`.

3D Artist tự quyết giải pháp trong chuẩn và budget. Phối hợp bên texture/material khi liên quan map/material/bake (tự làm thì ghi rõ là tự làm). Thay cách thể hiện đã duyệt thì trình người duyệt hình ảnh; vượt budget hoặc quyền task thì đưa đề nghị cùng đánh đổi.
