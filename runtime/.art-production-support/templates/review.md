# Review — quick hoặc tracked (cùng trường issue với AD)

Trường issue, mức ưu tiên và verdict lấy từ [issue-fields.json](issue-fields.json); AD `artistic-critique` dùng cùng bộ, nên issue artist ghi có thể chuyển thẳng cho AD và ngược lại.

**Quick:** artifact/version + điều kiện đã xem → điểm mạnh cần giữ → 1–3 vấn đề có tác động + hướng sửa → phần chưa đủ bằng chứng.

**Self-check 6 chiều** (cùng trục `visual-intelligence` của AD): composition · shape_silhouette · color_value · lighting · material_texture · visual_appeal. Mỗi chiều: đạt / lệch (vì sao) / không áp dụng / chưa kiểm.

**Tracked** khi nhiều lỗi, nhiều vòng sửa hoặc AD yêu cầu:

| id | priority | region | viewing_condition | evidence | consequence | confidence | repair | preserve | acceptance | status |
|---|---|---|---|---|---|---|---|---|---|---|
| I-01 | blocker | chuôi kiếm | 64px, nền panel tối | ngọc đỏ không có trong brief | lệch cấp độ vật phẩm | cao | xóa ngọc, giữ khối chuôi | silhouette lưỡi | 64px không còn điểm đỏ ở chuôi | open |

`priority`: blocker (yêu cầu bắt buộc hoặc phân biệt gameplay thiết yếu thất bại) / major (chất lượng, nhất quán đáng kể) / minor (polish cục bộ) / preference (sở thích, ghi riêng).

`status`: open / resolved / superseded (AD đổi yêu cầu) / regression. Giữ `id` qua các version. Chỉ `resolved` khi artifact mới chứng minh `acceptance`.

Verdict: meets_checked_criteria / needs_revision / insufficient_evidence — giới hạn theo phần đã kiểm. Ghi rõ self-review hay reviewer khác; verdict không phải AD approval hay quyền ship.
