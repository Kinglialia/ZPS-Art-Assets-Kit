# Review có bằng chứng

## Ba trục độc lập

1. Mỹ thuật: tổng thể, nhịp, cá tính, biểu đạt và quan hệ hình/màu/cạnh/vật liệu.
2. Đúng brief: phần khóa, style và câu hỏi đã được giải tại stage này.
3. Khả năng sử dụng: file/mapping/import và nhìn trong điều kiện đích.

Đọc whole → inspect → whole. Chỉ soi vùng có thể giải thích/bác bỏ nhận định. Tách quan sát (mắt thấy), diễn giải (nguyên nhân có thể) và phán đoán theo mục tiêu. Không suy topology, resolution hay performance từ ảnh. Grayscale không thay kiểm thị giác màu; ảnh tĩnh không chứng minh chuyển động hoặc phản ứng người chơi.

## Check theo nhánh

Concept: ý tưởng phân biệt được, silhouette/negative space, tỷ lệ/cấu tạo, phối cảnh/foreshortening, hierarchy và câu hỏi dựng. Environment thêm đường đi/scale; character thêm gesture/identity giữa view; prop thêm công năng/mối nối.

Surface: mảng vật liệu, hướng/scale nét, nhịp chi tiết, art intent; geometry/UV/normal/shader có thể gây cùng biểu hiện, cần phân biệt. Kiểm neutral và target lighting, góc khác, mip/compression nếu thuộc scope. Một texture phẳng đẹp chưa đạt on-model.

Asset 2D: alpha/pivot/canvas/frame, sự đồng bộ trong bộ, kích thước hiển thị và nền thực. Phần thiếu evidence đánh not_checked, không phán lỗi hoặc đạt.

UI: đúng wireframe đã duyệt, thứ tự chú ý, đủ state, chữ dài và tiếng Việt có dấu, 9-slice ở min/max size, vùng chạm sau scale. Preview safe area không thay thử thiết bị. Vấn đề flow/UX ghi cho UX/game design, không chấm là lỗi art.

## Vòng sửa

Khi theo dõi nhiều vòng hoặc caller yêu cầu, mỗi issue quan trọng có ID, vị trí/state, điều kiện, evidence, impact, causal hypothesis, repair direction, strengths-to-preserve và observable acceptance. Blocker là yêu cầu bắt buộc thất bại ở checkpoint này; major ảnh hưởng chất lượng đáng kể; minor là polish; preference ghi riêng. Không chặn concept rough chỉ vì thiếu chi tiết final.

Khóa artifact, brief và điều kiện so. Khi AD đổi yêu cầu, đánh superseded với lý do; không tính như một lỗi được sửa. Kiểm regression và ý tưởng tổng thể sau sửa. Reviewer đề xuất phương pháp, không ép artist dùng đúng kỹ thuật nếu kết quả đạt.

## Verdict trung thực

Self-review không là approval của AD. Review độc lập cần context/reviewer thực riêng; không tự gọi độc lập bằng đổi persona. Kết luận: meets_checked_criteria, needs_revision hoặc insufficient_evidence, giới hạn theo stage. Chỉ dùng [gate kỹ thuật](scripts/README.md#evidence-gate) khi caller yêu cầu nghiệm thu máy đọc được; required IDs là cấu hình đã chốt, không tự bỏ để pass. Missing/stale evidence không được trộn với not_applicable. Số điểm nếu có phải có rubric và không che blocker. Không cần tìm lỗi cho đủ quota.
