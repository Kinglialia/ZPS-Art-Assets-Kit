# Bảo trì library.json schema 2

Nguồn chuẩn: library.json; card, INDEX và KNOWLEDGE là bản dựng từ đó. File maintain.py trong gói thư viện kiểm tra và tạo lại TXT bằng Python 3.11+, không gọi mạng. Có thể thực hiện schema tương đương bằng công cụ môi trường khác nếu không có Python.

Entry: id, name, category, example, source_url, checked_at (YYYY-MM-DD), version (số nguyên dương), status (INDEX_ONLY/DRAFT/READY), card, source_summary, observed, ad_inference, validation_suggestion, limitations, rights, visual_review, games, media. Các trường image/image_sha256/image_source_url trỏ ảnh đầu tiên của media. card_drive_url giữ link hồ sơ cloud.

Media: file (đường dẫn tương đối trong gói), source_url, game, credit, official_url (null nếu nguồn không cung cấp), sha256, width, height, visual_review; drive_url và drive_id sau khi đồng bộ. Chỉ ghi reviewed khi đã thực sự mở ảnh; ảnh kiểm tra decode/hash nhưng chưa xem phải ghi riêng.

## Quy trình ghi

1. Đọc version và metadata cloud hiện tại, giữ chúng làm mốc. Chuẩn hóa URL bỏ fragment/slash cuối và hạ chữ hostname; không bỏ query có ý nghĩa. Cùng URL thì cập nhật entry cũ; ID mới phải duy nhất.
2. Lưu entry/card/ảnh phiên bản cũ vào history. Với bản phát hành lớn giữ ZIP cũ trên Drive. Không dựa duy nhất vào lịch sử trong máy cá nhân.
3. Tạo bản DRAFT, đọc nguồn, bổ sung ảnh và metadata. Không thay nguồn bằng một game khác chỉ để lấp ảnh thiếu. Giữ nguyên bytes ảnh tải về.
4. QA: ID/URL duy nhất, trường bắt buộc, path không thoát thư mục, decode ảnh, kích thước và hash, khớp image với media[0], credit và link. Khi đồng bộ website, kiểm tra tập style và tập ảnh riêng. Chỉ READY nếu đáp ứng yêu cầu; ghi ngoại lệ nguồn thiếu tác giả hoặc ảnh phụ chưa visual review.
5. Kiểm tra lại mốc cloud trước khi ghi. Nếu người khác đã sửa, đọc và hòa giải thay vì ghi đè. Upload file mới; update file cũ theo ID để giữ link. Không thay sharing.
6. Ghi URL/ID trả về vào media và receipt; dựng lại card/index. Upload ảnh trước, card sau, rồi library/index/knowledge/QA/receipt. Nếu gián đoạn, receipt/checkpoint phải cho biết file nào đã hoàn thành. Thử lại chỉ sau khi list/metadata kiểm tra kết quả lần trước.
7. Readback xác minh số lượng, file ID, bytes; dùng checksum nếu API có. Chỉ báo hoàn tất khi dữ liệu chuẩn và các bản đọc đồng nhất.

Lệnh: python3 maintain.py --coverage kiểm tra snapshot; thêm --cloud để yêu cầu link cloud. Snapshot phải được cập nhật từ nguồn quan sát thật khi website thay đổi, không sửa snapshot chỉ để test pass.

Thêm reference từ nguồn khác: namespace mới + slug ổn định, source URL thật và cùng schema; không cần sửa skill. Cập nhật version là trách nhiệm của bước maintenance; validator không tự chứng minh nội dung đáng được tăng version. Không chạy tự động vì file xuất hiện trong Inbox.

Kiểm tra ảnh bằng script cần Pillow (requirements.txt trong ZIP). Validator decode ảnh và đối chiếu kích thước/hash; việc decode không thay visual review. Nếu không có Python/Pillow, dùng công cụ có khả năng kiểm tra tương đương và ghi đúng kiểm tra nào đã chạy.

Drive connector hiện tại không cung cấp điều kiện ghi ETag trong update_file. Việc readback version trước ghi chỉ giảm, không loại bỏ hoàn toàn race condition. Khi không có conditional-write, chỉ một người/agent bảo trì kho tại một thời điểm; nếu phát hiện chỉnh sửa đồng thời thì dừng ghi bản cũ và hòa giải. Không tuyên bố transaction hoặc chống race tuyệt đối.
