# 2D checks — cách kiểm và chẩn đoán

Đọc khi cần kiểm sâu một nhóm trong bảng ở SKILL.md hoặc khi nguyên nhân chưa rõ. Quy cách sản xuất và đề xuất import nằm ở [Sản xuất asset 2D](../../zps-asset-2d-codex/references/production.md); UI ở [UI QA](../../zps-ui-codex/references/ui-qa.md). File này nói reviewer kiểm gì, bằng gì và kết luận được tới đâu.

## Bằng chứng tối thiểu theo câu hỏi

| Câu hỏi review | Bằng chứng cần | Không đủ để kết luận |
|---|---|---|
| Đọc được trong game không | Preview ở kích thước hiển thị trên nền game thật hoặc ảnh chụp màn hình game | Ảnh phóng to; nền trắng trơn |
| Alpha sạch không | `inspect_image.py` (alpha_extrema) và xem trên nền tối + sáng | File là RGBA |
| Pivot/frame ổn không | `sprite_check.py` trên cả sequence | Xem từng frame riêng |
| Chuyển động đúng quỹ đạo, không giật | Onion skin + filmstrip từ `anim_preview.py` | Từng frame riêng; agent tự xem GIF |
| Nhịp, cảm giác chuyển động | Người xem GIF ở fps đích, hoặc chạy trong game | Onion skin (chỉ thấy quỹ đạo) |
| Đồng bộ với bộ không | So với asset mẫu theo [asset mẫu](../../.art-production-support/shared/set-anchor.md); chưa có mẫu thì so cả bộ cạnh nhau | So với concept hay reference cảnh |
| Ghi chú import đúng | Đối chiếu bảng import trong [Sản xuất asset 2D](../../zps-asset-2d-codex/references/production.md) | Tên file, "đã xuất PNG" |
| Tile liền không | `preview.py tile` nhiều ô | Xem một ô |
| UI chịu được chữ dài không | Render với chuỗi dài nhất thật, có dấu tiếng Việt | Chữ mẫu ngắn tiếng Anh |
| Chạy đúng trong engine/thiết bị | Import thật / thử trên thiết bị | Preview từ script |

Thiếu bằng chứng ở hàng nào thì kết luận hàng đó là `not_checked`, không phải pass hay fail.

## Cây chẩn đoán nhanh

- **Khó đọc ở kích thước nhỏ:** silhouette không rõ → quá nhiều điểm nhận diện → value giữa vật và nền quá gần → nét mảnh mất khi thu nhỏ. Sửa bằng đơn giản hóa khối hoặc tăng độ dày nét trước khi sharpen.
- **Lệch bộ:** góc nhìn, độ dày nét, mức chi tiết, hướng sáng hay scale vật khác asset mẫu. Ghi rõ trục nào lệch.
- **Viền sáng/tối quanh asset:** halo do tách nền, premultiplied/straight alpha sai, hoặc thiếu alpha border khi lọc.
- **Nhân vật rung khi chạy animation:** canvas/pivot không cố định giữa frame, thường do auto-crop từng frame.
- **Tile lộ nối:** cạnh không khớp, hoặc dấu nổi bật lặp đều. Tách hai trường hợp vì cách sửa khác nhau.
- **Pixel art nhòe:** resample bilinear hoặc scale không nguyên lần; hoặc ghi chú import đề xuất filter Linear.
- **Animation giật:** khoảng cách giữa các pose trên onion skin không đều ở đoạn cần đều; một frame lệch quỹ đạo; volume nhân vật co giãn giữa frame.

## Phân mức

- **blocker:** không đọc/phân biệt được ở kích thước game khi đó là chức năng chính (ví dụ icon vật phẩm, trạng thái UI); alpha/canvas/pivot sai hợp đồng làm asset hiển thị sai; ghi chú import sai làm asset hiển thị sai (pixel art không Nearest, thiếu padding atlas gây lem); chữ UI tràn/cắt ở chuỗi bắt buộc.
- **major:** lệch bộ rõ; halo thấy được trên nền game; tile lộ nhịp lặp ở khoảng nhìn thường.
- **minor:** chi tiết phụ chưa gọn; lỗi chỉ thấy khi phóng to.
- Ghi riêng **preference** cho lựa chọn thẩm mỹ không vi phạm brief.

## Review UI

Tiêu chí kiểm lấy từ [UI QA](../../zps-ui-codex/references/ui-qa.md). Phần dưới bổ sung bằng chứng và phân mức từ góc nhìn reviewer.

| Câu hỏi | Bằng chứng cần | Không đủ để kết luận |
|---|---|---|
| Chữ có tràn/cắt không | Render với chuỗi dài nhất thật, có tiếng Việt có dấu | Chữ mẫu ngắn |
| Đủ state không | Ảnh từng state đã yêu cầu (bình thường, nhấn, khóa, chọn…) | Một state đại diện |
| 9-slice đúng không | Render ở kích thước nhỏ nhất và lớn nhất sẽ dùng | Ảnh frame gốc |
| Đọc được trên game không | Màn hình ở độ phân giải đích, trên nền game bận nhất | Nền trơn |
| Vùng chạm đủ không | Số đo sau scale ở độ phân giải đích | Kích thước ảnh |
| Đúng wireframe không | Đặt cạnh wireframe đã duyệt | Mô tả bằng lời |
| Nguồn SVG đúng luật không | Cảnh báo của `svg_render.py` (chữ trong SVG, filter, mask…); tên group theo component/state | Chỉ xem PNG |

- **blocker:** chữ bắt buộc tràn/cắt; thiếu state bắt buộc; 9-slice vỡ ở kích thước dùng thật; vùng chạm dưới mục tiêu của project; sai wireframe đã duyệt.
- **major:** thứ tự chú ý sai; HUD khó đọc trên nền bận; lệch UI kit hoặc hướng đã chọn.
- **minor:** lệch căn lề nhỏ; trang trí thừa không ảnh hưởng đọc.
- Vấn đề flow/UX: ghi cho UX/game design, không chấm là lỗi art.

## Ranh giới role

Reviewer kết luận vấn đề có bằng chứng. Sửa asset thuộc Asset 2D hoặc UI; vấn đề flow/wireframe thuộc UX/game design; đổi style thuộc AD.
