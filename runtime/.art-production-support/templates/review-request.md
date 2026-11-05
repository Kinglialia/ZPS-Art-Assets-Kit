# Review request — giao review cho người/agent/session khác

Gửi đủ các ô; người review chấm theo **tiêu chí gửi kèm**, không theo trí nhớ hay bản cũ.

```markdown
# Review <asset> <version> — chỉ đọc, không gen, không sửa file

- Ảnh: <đường dẫn trên máy người review> (+ ảnh gốc nếu là bản edit)
- Style sheet/Bible: <version> — dán các dòng áp dụng, kể cả số đo chuẩn (màu 5% tối nhất, cast, value, palette)
- Reference cùng loại deliverable: <đường dẫn>
- Tiêu chí chấm (pass/partial/fail + 1 câu bằng chứng): <id: tiêu chí đo được>
- Đo: score_variants / palette / value / structure_diff (nếu là edit) — ghi lệnh
- Kiểm kê phần tử: danh sách được phép = <…>
- Trả về: bảng số đo, bảng chấm, kiểm kê, lỗi ảnh gen. Không gửi ảnh qua base64.
```

Người review phải tự mở ảnh. Tiêu chí nào thiếu số đo chuẩn thì chấm `insufficient_evidence`, không đoán.
