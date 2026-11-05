# Bảo trì library.json schema 2

Nguồn chuẩn: library.json; card, INDEX, KNOWLEDGE và gallery (nếu phát hành) là bản dựng từ đó. maintain.py dựng TXT; gallery có công cụ dựng riêng, không mặc định được cập nhật cùng lệnh. File maintain.py trong gói thư viện kiểm tra và tạo lại TXT bằng Python 3.11+, không gọi mạng. Có thể thực hiện schema tương đương bằng công cụ môi trường khác nếu không có Python.

Entry: id, name, category, example, source_url, checked_at (YYYY-MM-DD), version (số nguyên dương), status (INDEX_ONLY/DRAFT/READY), card, source_summary, observed, ad_inference, validation_suggestion, limitations, rights, visual_review, games, media. Các trường image/image_sha256/image_source_url trỏ ảnh đầu tiên của media. card_drive_url giữ link hồ sơ cloud.

Media: file (đường dẫn tương đối trong gói), source_url, game, credit, official_url (null nếu nguồn không cung cấp), sha256, width, height, visual_review; drive_url và drive_id sau khi đồng bộ. Chỉ ghi reviewed khi đã thực sự mở ảnh; ảnh kiểm tra decode/hash nhưng chưa xem phải ghi riêng. Trong ghi nhận review, chỉ rõ file/hash hoặc phiên bản ảnh, ngày và phạm vi đã xem khi biết. Có thể ghi trong trường mô tả hiện có; không tự đổi schema. Khi thay ảnh hoặc đổi ảnh đại diện, rà lại observed, ad_inference và các kết luận phụ thuộc ảnh; giữ lịch sử và đánh dấu phần cần xem lại. Không kế thừa review từ ảnh trước hoặc coi ghi nhận của người/phiên trước là quan sát mới.

## Chuẩn bị chung

Xác định đích ghi và phạm vi được duyệt theo quy định project. Phân biệt bản làm việc cục bộ với kho chuẩn; yêu cầu chỉnh bản cục bộ không tự cho phép publish lên Drive. Kiểm tra công cụ bảo trì thực sự có trong gói: repo skill không kèm maintain.py, build_gallery.py hoặc ảnh. Nếu thiếu, chỉ thực hiện kiểm tra tương đương có thể làm được và báo phần chưa thực hiện.

Giữ ID cũ và nguồn, tăng version khi nội dung đổi. Chuẩn hóa URL để tìm ứng viên trùng, giữ query có ý nghĩa; kiểm tra identity trước khi hợp nhất, không tự coi URL đổi là reference mới. Tạo bản DRAFT khi thiếu dữ liệu. Bảo toàn bytes ảnh, credit và lịch sử; không thay ảnh bằng game khác để lấp chỗ trống.

## Cập nhật bản cục bộ

1. Ghi nhận version/hash ban đầu của dữ liệu liên quan, giữ bản trước chỉnh sửa ở vị trí history/backup đã xác định trong phạm vi task. Không dựa vào chat làm lịch sử.
2. Sửa bản làm việc; QA ID/URL, trường bắt buộc, path, ảnh decode/kích thước/hash, image khớp media[0], credit và link. Kiểm tra snapshot coverage chỉ khi thuộc phạm vi; trạng thái review ảnh phải phản ánh bằng chứng thực có.
3. Kiểm tra lại mốc cục bộ trước khi thay thế file; nếu có thay đổi khác thì hòa giải. Dựng lại các bản đọc chịu tác động: card, INDEX, KNOWLEDGE, gallery nếu có; đối chiếu cùng release/phiên bản. Cập nhật manifest nếu gói có manifest và file được khai báo đã đổi; giữ mốc cũ trong lịch sử.
4. Đọc lại file đầu ra và báo “đã cập nhật cục bộ”, vị trí, QA và phần còn thiếu. Nếu chỉ lưu trong workspace tạm thì ghi rõ chưa lưu bền vững; không coi Drive đã đồng bộ. Đưa kết quả về nơi lưu được user chỉ định trong phạm vi được phép.

## Đồng bộ Drive khi được giao

1. Đọc version/metadata cloud hiện tại trước khi chuẩn bị ghi, giữ làm mốc; receipt cũ không thay bước này. Lưu phiên bản cũ ở history đã xác định; giữ ZIP cũ với bản phát hành lớn.
2. Chuẩn bị và QA bản làm việc theo các bước cục bộ. Trước upload, kiểm tra lại mốc cloud; hòa giải khi có chỉnh sửa khác. Update file cũ theo ID để giữ link, upload file mới khi cần; không thay sharing.
3. Upload ảnh trước, ghi ID/URL trả về vào dữ liệu và receipt. Dựng lại card và các bản đọc phụ thuộc link mới rồi upload card, library, INDEX, KNOWLEDGE, gallery nếu phát hành, QA và receipt. Checkpoint phải ghi rõ phần đã lưu và phần đang chờ; kiểm tra đích trước khi retry timeout.
4. Readback số lượng, ID, bytes và checksum nếu công cụ có. Đối chiếu dữ liệu chuẩn với các bản đọc theo cùng phiên bản; chỉ báo phần đã xác minh. Nếu gián đoạn, chỉ rõ bản nào mới/bản nào còn cũ và bước phục hồi, không tuyên bố giao dịch nguyên tử.

Lệnh: python3 maintain.py --coverage kiểm tra snapshot đã lưu và dựng lại TXT; đây không phải lệnh chỉ đọc. Thêm --cloud chỉ yêu cầu URL cloud hợp lệ trong dữ liệu cục bộ, không gọi Drive hay xác minh file tồn tại, quyền truy cập hoặc nội dung từ xa. Báo riêng kiểm tra cục bộ, đối chiếu snapshot và readback Drive trực tiếp với thời điểm thực hiện. Snapshot phải được cập nhật từ nguồn quan sát thật khi website thay đổi, không sửa snapshot chỉ để test pass.

Thêm reference từ nguồn khác: namespace mới + slug ổn định, source URL thật và cùng schema; không cần sửa skill. Cập nhật version là trách nhiệm của bước maintenance; validator không tự chứng minh nội dung đáng được tăng version. Không chạy tự động vì file xuất hiện trong Inbox.

Kiểm tra ảnh bằng script cần Pillow (requirements.txt trong ZIP). Validator decode ảnh và đối chiếu kích thước/hash; việc decode không thay visual review. Nếu không có Python/Pillow, dùng công cụ có khả năng kiểm tra tương đương và ghi đúng kiểm tra nào đã chạy.

Kiểm tra khả năng connector/API thực sự có trong phiên: đọc metadata, checksum và điều kiện ghi nếu được hỗ trợ. Không suy ra connector có toàn bộ khả năng của Drive API. Version phía Drive và version entry/release thư viện có ý nghĩa khác nhau; dùng metadata cloud làm mốc thay đổi từ xa, không thay cho version nội dung. Nếu công cụ hỗ trợ conditional-write, dùng điều kiện đã đọc để phát hiện xung đột và hòa giải khi điều kiện thất bại. Việc readback version trước ghi chỉ giảm, không loại bỏ hoàn toàn race condition. Khi không có conditional-write, chỉ một người/agent bảo trì kho tại một thời điểm; nếu phát hiện chỉnh sửa đồng thời thì dừng ghi bản cũ và hòa giải. Không tuyên bố transaction hoặc chống race tuyệt đối.

## Refresh website khi được giao

Đối chiếu mục mới/thay đổi/mất khỏi nguồn với snapshot. Kiểm tra style và ảnh riêng, kể cả gallery/lazy loading; loại bản trùng theo nội dung/identity, không loại ảnh khác chỉ vì cùng game. Ghi nguồn lỗi và độ phân giải. Giữ lịch sử mục mất khỏi website; không tự xóa dữ liệu đã lưu. Báo riêng kết quả cục bộ, đối chiếu snapshot và xác minh Drive trực tiếp.
