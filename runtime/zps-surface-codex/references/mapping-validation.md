# Mapping, bake và kiểm tại đích

## Preflight theo phương pháp

Tái dùng mesh/UV version, UV set, materials, units/scale, shader, texture resolution và view đã có; chỉ bổ sung dữ liệu cần cho thao tác. Repack maps theo hợp đồng có sẵn không bắt mở mesh nếu chỉ được giao đổi kênh. UV không bắt buộc cho mọi procedural/vertex-color; đầu ra texture UV thì cần mapping tương ứng. Gửi lỗi mesh/UV đúng owner với vùng bị chặn. High→low bake chỉ một owner; giữ cage, triangulation và tangent conventions.

Kiểm distortion bằng checker trên model; density theo vùng ưu tiên, không bắt mọi pixel/mọi asset bằng nhau. Shared atlas cần xét overlap giữa **mọi object dùng cùng ảnh**, không chỉ từng object. Mirror/stack/UDIM/tiling có thể hợp lệ nhưng ảnh hưởng bake và unique marks. Script đơn giản 0–1 không chứng minh UDIM hợp lệ.

Tiling: offset giúp tìm seam nhưng vẫn cần nhìn lặp nhiều ô và trên bề mặt. Trim theo chiều/hướng vật liệu; decal kiểm mép, scale và blending. Không dùng perspective warp một concept để mặc định thành texture sạch ánh sáng.

## Padding và filtering

Khoảng cách giữa islands khác phần dilation màu ra ngoài island. Chọn theo resolution, mip lớn nhất sử dụng, filtering, compression và export. Không có bảng px nào bảo đảm mọi trường hợp. Test seam ở khoảng nhìn đích và mip thấp; không mặc định tắt mip để chữa. Map có alpha kiểm nền sáng/tối, straight/premultiplied theo renderer; RGBA PNG tự nó không xác nhận convention.

## Điều kiện xem và nguyên nhân

Khóa camera, lighting, exposure, tone mapping và import giữa bản đối chiếu. Lỗi mờ: ảnh gốc → diện tích/distortion UV → sampler/mip/compression → shader/lighting. Lỗi đen: color space/alpha/normals/material links trước repaint. Lỗi seam: UV/tangent/bake/packing trước blur. Tách perceived material và implementation; một ảnh đẹp không chứng minh map đúng.

Bằng chứng cần khớp artifact/version. Script chỉ ghi pass cho check đã chạy; mandatory not_checked thì chưa đủ điều kiện. Import lại GLB kiểm cấu trúc hữu ích nhưng chưa thay kiểm engine. Nêu rõ ảnh được render bằng Workbench, Eevee, Cycles hay engine thật. Giao map/channel/color-space/normal/UV/resolution/source và file ngoại liên quan; đo kích thước thực, không lấy số trong prompt.
