# Sửa ảnh không làm trôi thiết kế

Ghi Gốc/Giữ/Đổi bằng thuộc tính và vùng cụ thể. Reference phải đánh số/vai trò trong yêu cầu công cụ. Chọn sửa cục bộ khi có source phù hợp; không âm thầm sinh ảnh mới từ chữ để thay bản edit.

Giữ source và phiên bản được duyệt. Công cụ có thể đổi framing, tỷ lệ, chi tiết phụ hoặc số bộ phận dù prompt yêu cầu giữ. Mở và so cả vùng sửa lẫn vùng giữ. Khi yêu cầu giữ pixel tuyệt đối, dùng công cụ hỗ trợ mask/composite theo chính sách môi trường và so pixel vùng khóa; prompt không bảo đảm bất biến. Không gọi phần ghép từ ảnh phẳng là source có layer vẽ gốc.

Nếu ảnh đầu ra khác kích thước, kiểm crop/landmark trước. Resize có thể sửa kích thước file nhưng không tự sửa cấu trúc hay phối cảnh; không kéo méo để vừa guide. Phần chỉnh sửa ảnh phải dùng công cụ được phép của phiên, không đi vòng qua hạn chế tool.

So toàn hình, vùng quan trọng và kích thước đích. Đóng issue khi artifact mới chứng minh đã sửa; không lấy lời giải thích làm bằng chứng. Yêu cầu AD mới là thay brief, không phải lỗi hồi tố. Hết budget hoặc lỗi lặp thì chẩn đoán nguyên nhân và hướng khác, không retry prompt vô hạn.
