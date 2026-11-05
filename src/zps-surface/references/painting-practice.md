# Thực hành nét vẽ và chất liệu stylized

Đây là bài hướng dẫn có điều kiện, không preset cho mọi style. Dùng công cụ paint/edit có thực và quyền của phiên; source có layer chỉ được khai khi thực sự tạo được. Nếu dùng công cụ sinh ảnh, mô tả quan hệ thị giác này bằng reference/edit rồi kiểm kết quả, không giả đã thao tác brush thủ công.

## Đặt nét có mục đích

Làm từ khối/mảng lớn bằng nét đủ rộng; nét nhỏ quá sớm dễ biến thành noise. Hard/soft edge do cấu trúc, ánh sáng và ngôn ngữ hình quyết định. Nét sắc cho chỗ cần đọc, chuyển mềm cho mặt cong khi hợp style; không airbrush toàn ảnh làm mất plane. Giảm opacity nhiều lớp có thể làm màu đục nếu chỉ trộn tối/sáng; kiểm vai trò hue/value/saturation thay vì thêm lớp vô hạn.

Nhóm stroke theo bề mặt: vân gỗ theo thớ/cách cắt; đá theo plane và nứt; vải theo lực và cách dệt. Nét đi qua UV seam phải tiếp tục trên model, không nối chỉ vì hai mép gần nhau trên atlas. Mỗi nhóm có khoảng nghỉ, độ dài/dày biến thiên theo ý đồ. Brush texture là phương tiện tạo dấu, không thay phân bố có lý do.

Với unlit có ánh sáng vẽ sẵn, xác định hướng sáng và nhóm mặt nhận sáng trước. Mặt lồi, khe tiếp xúc và ranh giới vật liệu tạo các loại chuyển khác nhau; không viền sáng mọi cạnh hoặc tô đen mọi khe. Với dynamic-lit, tách các dấu vật liệu khỏi highlight/cast shadow phụ thuộc đèn. Không dùng màu bóng trong concept như màu vật liệu đo được.

## Recipe A — gỗ đẽo cho prop nhỏ

Mục tiêu giả định: rõ khối, có lịch sử sử dụng, không realistic noise. Dựng mảng mỗi tấm theo silhouette/plane, đặt hướng thớ và mối nối. Chọn vài cụm thớ góp nhận diện, thay mật độ và để vùng yên. Mép mẻ phải liên quan cấu tạo/va chạm; vết gần tay cầm có lý do dùng. Kiểm từ góc game: nếu thớ thành sọc đều cạnh tranh khối, gom hoặc giảm nhịp. PBR/lit: thử roughness của vùng mòn riêng, không bake vệt specular vào màu.

## Recipe B — đá có mặt phẳng

Mục tiêu giả định: đọc plane lớn và độ nặng. Trước hết cần geometry/silhouette phù hợp. Màu biến thiên theo nhóm mặt/vật liệu, không chỉ random từng polygon. Chọn nứt theo lực/khối và phân nhóm, tránh mạng nứt đều. Painted edge cần bề rộng có nhịp và nguyên nhân; đừng thêm highlight để giả một mặt vát không có khi camera quay. Kiểm clay và surface riêng để phát hiện texture đang che form yếu.

## Recipe C — vải, da và kim loại cùng prop

Giữ cùng mức stylization nhưng khác cảm giác: vải có nếp theo lực và cạnh mềm thích hợp; da có seam, vùng uốn/mòn; kim loại có phản ứng phản xạ theo roughness/ánh sáng hoặc ngôn ngữ minh họa đã chốt. Không phân biệt chỉ bằng ba màu. Thử vùng giao vật liệu để xem scale nét và độ sắc có hòa hợp, tránh mỗi phần trông thuộc game khác.

## Bài thử nhỏ trước khi mở rộng

So cùng model/camera ba trạng thái: mảng nền, thêm cấu trúc, thêm điểm nhấn. Mỗi lần thêm phải giải thích được lợi ích ở target size. Giữ bản trước để thấy khi polish làm xấu hierarchy. Với mẫu mới, thử góc không dùng author và điều kiện nền/đèn quan trọng; không coi swatch đẹp trên sphere là đủ cho mọi asset.
