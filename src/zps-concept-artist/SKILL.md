---
name: zps-concept-artist
description: "Draw or revise concept art for 3D game assets: grey-box paint-over from the game camera, clear forms, hidden parts and extra views for the modeler. Use for concept images (\"vẽ concept\", \"paint over grey-box\", \"vẽ thêm view\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Concept Artist

**Not for:** brainstorming ideas (zps-creative-brainstorming); writing a brief (zps-art-bible-artist-direction); 2D images placed in the game (zps-asset-2d).

Chuyển direction thành concept nhìn thấy được và đủ rõ cho người dựng. AD có thể vừa định hướng vừa vẽ concept trong cùng task.

## Chốt phạm vi từ thông tin đã có

Dùng brief, quyết định style và phạm vi duyệt hiện tại; không bắt user nhập lại biểu mẫu. [Concept brief](templates/CONCEPT-BRIEF.md) là mẫu tùy chọn để ghi thông tin còn thiếu và bàn giao.

Xác định chức năng asset, thông tin gameplay cần đọc, silhouette/đặc trưng cần giữ, camera và kích thước hiển thị, shading, nguồn ảnh/grey-box và đầu ra cần giao. Chỉ hỏi khi điều thiếu có thể làm sai thiết kế hoặc khiến bước tiếp theo không thực hiện được. Có thể làm bản thăm dò với giả định được ghi rõ; không tự đặt thông số engine hay coi style tạm là đã chốt.

Nếu chưa có direction và user muốn khám phá, Creative Brainstorming giúp chọn ý tưởng; Concept Artist có thể tạo các ảnh thử có nhãn provisional. Quy tắc áp dụng chung cho nhiều asset thuộc Art Style Development. Không buộc chạy hai skill đó trước mọi bản vẽ.

## Vẽ hoặc sửa concept

- Mở ảnh nguồn trước khi sửa. Với paint-over grey-box, giữ camera, khung hình, tỷ lệ và các khối bị khóa. Nếu yêu cầu đòi đổi khối, phân biệt rõ phần được phép đổi. Không có grey-box thì dùng camera đã cung cấp; khi camera chưa xác định, ghi góc minh họa và không tuyên bố khớp camera game.
- Khối trước chi tiết: silhouette, mặt phẳng lớn và khối phụ phải đọc được ở kích thước game khi đã biết. Không để chi tiết bề mặt che cấu trúc.
- Tách hình thức trình bày và đầu ra dùng để dựng. Với ảnh dùng projection/texture, tránh bóng nền sát chân bị lấy nhầm thành màu đáy; dùng nền trơn hoặc alpha theo đầu ra. Ảnh trình bày có thể có bóng tiếp xúc, nhưng không dùng nguyên bản đó làm texture projection. Các vật trong cụm cần viền đủ tách biệt.
- Shading theo pipeline: với unshaded, chỉ bake ánh sáng theo quy ước đã chốt; với lit, tách lighting của ảnh trình bày khỏi base color/albedo dùng sản xuất, không mặc định đưa highlight và bóng chiếu vào albedo. Concept shaded để diễn tả form vẫn hợp lệ. Nếu chưa rõ pipeline, giữ đây là giả định thay vì ép một công thức chung.
- Với phạm vi xoay hoặc yêu cầu dựng cần phần khuất, bổ sung view/chi tiết khi có ích. Giữ nhất quán giữa các view; ghi phần suy đoán và phần chưa giải quyết. Không bịa kích thước: số đo phải có đơn vị, mốc và nguồn hoặc nhãn ước lượng.
- Với revision, ghi **Gốc / Giữ / Đổi** và tạo phiên bản mới; giữ bản đã duyệt. Yêu cầu mới của user có thể thay đổi phạm vi cũ, nhưng bản sửa không tự trở thành chuẩn chung.

Dùng công cụ tạo/chỉnh ảnh có sẵn và hướng dẫn của công cụ đó. Nếu không thể tạo ảnh, giao brief/prompt và báo phần hình ảnh chưa thực hiện; không gọi prompt là concept hoàn thành. Không tự mở rộng sang dựng model hoặc texture production.

## Kiểm và bàn giao

Mở kết quả thực tế; kiểm silhouette, hình khối, chi tiết khóa, framing và khả năng đọc ở kích thước được cung cấp. Không khẳng định khớp camera số học chỉ từ ảnh sinh; ghi sai lệch và cần kiểm chứng khi chưa đối chiếu được. Với sheet nhiều view, kiểm nhận diện và kết cấu có nhất quán không.

Giao ảnh concept/PNG dùng để dựng, phiên bản, camera/grey-box nguồn, phần khuất/giả định và câu hỏi ảnh hưởng tới dựng. Chỉ giao file có layer hoặc nền alpha khi thực sự tạo và kiểm được; nếu công cụ chỉ xuất ảnh phẳng, nói rõ và xác định phần còn thiếu nếu layered source là yêu cầu bắt buộc.

Tách ba trạng thái: tự kiểm đã làm (không phải review độc lập), phê duyệt mỹ thuật của người được chỉ định, và xác nhận đủ thông tin dựng của người dựng. Không tự điền tên/ngày duyệt hoặc xác nhận thay người khác. Một bản concept tốt không chứng minh topology, budget hoặc khả năng import engine. Không áp số vòng sửa hay chi phí mặc định; dùng giới hạn đã được giao.

Artistic Critique hỗ trợ review hoặc theo dõi revision khi cần; Art Bible & Artist Direction chỉ cập nhật các quyết định đã chốt thành hướng dẫn. Xem [workflow AD](../.art-director-support/workflows/art-direction.md) cho tác vụ kết hợp.
