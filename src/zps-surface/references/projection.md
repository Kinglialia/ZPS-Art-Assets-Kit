# Projection paint — tách stage paint và integration

## Hợp đồng tối thiểu

Nếu được giao **tô view**: nhận render guide mỗi góc, thiết kế/reference có vai trò, phần giữ/đổi, output size/framing và lighting model. Source model/version và camera được nhận bằng ID/thông tin từ caller; không bắt artist mở mesh/UV nếu caller sở hữu projection/bake. Clay + mask/landmark có thể đủ cho paint đơn giản; depth/normal/position/UV/material-ID chỉ bắt buộc khi phương pháp/check cụ thể cần. Pass thiếu encoding/hệ tọa độ không được dùng như số đo chính xác.

Nếu được giao **bake và xác minh trên model**: cần mesh/camera/mapping và công cụ phù hợp. Stage này có owner rõ, không mặc định artist phải làm thêm sau khi đã giao view.

## Tô view

Tool phải nhận source và chỉnh bố cục; thiếu thì báo blocked phần paint. Chọn anchor, giữ màu/vật liệu/landmark giữa các góc. Không tô specular/rim phụ thuộc camera vào màu chiếu trừ thiết kế/đích cho phép; phân biệt nét cạnh thực với viền silhouette. Đọc hand-painted/PBR chỉ khi cần giải vấn đề nét hoặc shading, không bắt toàn bộ surface pipeline.

Mở output, kiểm framing, kích thước, landmark và phần giữ. Resize sửa canvas, không chứng minh alignment. Alpha vừa áp bằng mask chỉ xác minh masking, không chứng minh nội dung bám geometry. Xử lý ảnh theo tool/quyền của phiên. Vùng khuất không có nguồn phải ghi suy luận; không tự mở lại thiết kế.

## Khi có integration evidence

Owner chiếu/bake rồi render view nguồn và góc chưa dùng author khi cần xác nhận coverage/seam. Artist dùng kết quả đó để sửa vùng được giao; không bake trùng. View nghiêng/occluded cần weighting/visibility hợp lý; blend đều có thể làm nhòe chi tiết. Cạnh họa tiết phẳng không cần trùng depth edge. So màu tại vùng bề mặt tương ứng, cùng không gian/điều kiện; không áp ngưỡng ΔE/px chung chưa định nghĩa.

## Bàn giao đúng phạm vi

Giao paint_<view>, source guide/version, checks và suy luận; palette/schema chỉ khi caller cần. Paint đạt contract thì có thể ghi hoàn tất stage paint, integration chưa kiểm/thuộc caller. Nếu task yêu cầu cả integration mà thiếu thì ghi phần đó partial/blocked. Không nhận seamless hay game-ready từ chỉ paint views. Ánh sáng bake đi theo object khi quay: ghi phạm vi pose/ánh sáng đã kiểm.
