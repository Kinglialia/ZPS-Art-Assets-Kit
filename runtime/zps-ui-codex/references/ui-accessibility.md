# UI accessibility theo task

Chốt mục tiêu và cách kiểm cho task; không tuyên bố đạt chuẩn chung từ checklist.

- Vùng chạm sau scale, khoảng cách giữa hành động dễ nhầm, thao tác lặp, che khuất bởi tay.
- Phóng to chữ/UI trong phạm vi hỗ trợ mà nội dung và hành động vẫn dùng được.
- Tương phản trên nền thực tế (nền gameplay, ảnh, chuyển động), không chỉ nền phẳng.
- Trạng thái quan trọng có tín hiệu ngoài màu: nhãn, hình, pattern.
- Kết quả quan trọng không chỉ báo bằng âm thanh.
- Motion không thiết yếu có phương án giảm/tắt khi thuộc yêu cầu; tránh nhấp nháy gây khó chịu.
- Nút chỉ có icon cần nghĩa rõ; ghi nhãn, thứ tự focus và semantic khi có yêu cầu công nghệ hỗ trợ.

Tham khảo W3C để hiểu vấn đề ([màu](https://github.com/w3c/wcag/blob/main/understanding/20/use-of-color.html), [contrast](https://github.com/w3c/wcag/blob/main/understanding/20/contrast-minimum.html), [vùng chạm](https://github.com/w3c/wcag/blob/main/understanding/22/target-size-minimum.html), [motion](https://github.com/w3c/wcag/blob/main/understanding/21/animation-from-interactions.html)). Đây là tiêu chí web: CSS pixel không gán thẳng cho đơn vị Godot và không chứng nhận game native. Ghi đơn vị và nguồn mục tiêu của project; screen reader/focus phải đối chiếu đúng Godot, hệ điều hành và thiết bị.
