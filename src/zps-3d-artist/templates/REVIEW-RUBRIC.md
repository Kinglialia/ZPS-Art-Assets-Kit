# Rubric review hình ảnh — 3d-artist v0.3 (từ art-3d-artist v0.1)

Dùng cho mọi lượt review sản phẩm có concept. Người duyệt hình ảnh là người dùng hoặc subagent `3d-critic` với context mới mỗi lượt, chỉ nhận bộ review của đúng bước đang review. Orchestrator dùng rubric này để tự kiểm trước khi gửi; tự kiểm không thay lượt duyệt độc lập.

Concept orthographic (front/left/back/right) không có ConceptCam nên không có `concept_compare.png`: thay bằng `overlay_*.png` của `tools/self_build/render_views.py --input <final.glb> --mode critic` (concept đỏ, model xanh). `concept_compare.png` chỉ bắt buộc khi spec có ConceptCam.

Trong vòng lặp self-build, critic nhận thêm bộ ảnh của `tools/self_build/render_views.py --mode critic` (`clay_*`, `normal_*`, `overlay_*`, `parts_*`, `prev_34`). Mục 1 (Khối) chỉ chấm trên `clay_*` và `normal_*`, vì texture che lỗi khối (research_notes §2).

## Bộ review theo bước (người gửi review chuẩn bị; tên file theo script `render_rig`/`asset_checks`, không có script thì dùng ảnh tương đương chụp đúng camera game và ghi nguồn)
| Thành phần | File | Khối | Texture | Engine |
|---|---|:-:|:-:|:-:|
| Concept đã duyệt + brief (ưu tiên đọc, camera game, góc xoay được phép, shading) | brief | ✓ | ✓ | ✓ |
| **Clay ở camera game** — xem trước | `game_clay_crop.png`, `view*_clay.png` | ✓ | ✓ | ✓ |
| JSON đo: budget_use, coverage, IoU, kích thước | `mesh_check`, `concept_coverage`, `iou_check` | ✓ | ✓ | ✓ |
| Sản phẩm ở camera game, kích thước thật và phóng 2× | `game_albedo_crop.png`, `game_albedo_crop_2x.png` | | ✓ | ✓ |
| Concept \| sản phẩm ở góc concept | `concept_compare.png` | | ✓ | ✓ |
| Các góc xoay trong phạm vi brief | `view*_albedo.png` | | ✓ | ✓ |
| JSON uv / export | `uv_check`, `export_check` | | uv | ✓ |
| Ảnh engine ở camera game | ảnh chụp engine | | | ✓ |

Camera game trùng camera concept (concept vẽ đè grey-box ở camera game): bỏ `game_albedo_crop.png`, dùng `concept_compare.png` và `game_albedo_crop_2x.png`.

Không gửi: bản trước, lịch sử làm việc, lời giải thích của artist. Thiếu thành phần đánh ✓ của bước đang review → người duyệt trả bộ review về người gửi, không kết luận.

## Thứ tự xem — mục 1 đến 5 đều chặn
| Mục | Khối | Texture | Engine |
|---|:-:|:-:|:-:|
| 1 Khối | ✓ | ✓ | ✓ |
| 2 Silhouette, bố cục | ✓ | ✓ | ✓ |
| 3 Ưu tiên đọc | phần khối | ✓ | ✓ |
| 4 Look | | ✓ (trừ chiếu sáng) | ✓ |
| 5 Góc xoay | phần khối | ✓ | ✓ |

Mục không thuộc bước đang review ghi vào "Chưa kiểm được", không tính là lỗi.

1. **Khối (chỉ nhìn clay ở camera game).** Clay có đọc ra ngôn ngữ khối của concept không: các mặt vát lớn, khối con, độ nghiêng mặt đỉnh. Khối tròn trịa, quá ít mặt hoặc "như ổ bánh mì" là `chưa đạt` dù texture đẹp. Xem clay trước để texture chiếu không che khối thô.
2. **Silhouette và bố cục** ở góc concept và camera game: đường viền lớn, tỷ lệ, vị trí trước/sau, che khuất. IoU dưới `iou.min_iou` trong spec là `chưa đạt`; IoU cao không chứng minh khối đúng (với M1 IoU gần như luôn cao).
3. **Ưu tiên đọc** ở camera game, kích thước thật: từng dòng trong brief đọc ra hay không. Bước khối chỉ xét các dòng thuộc về hình khối.
4. **Look** so với concept: màu, nét, vật liệu, mức chi tiết; ảnh engine: kiểm chiếu sáng hai lần theo shading trong brief.
5. **Các góc xoay trong phạm vi brief:** không kéo sọc, không mảng lặp lộ rõ, không mặt trống, không vật thể lòi qua nhau. Bước khối chỉ xét lòi qua nhau và mặt thiếu. Ngoài phạm vi brief chỉ ghi nhận xét.

## Ghi kết quả
```
BƯỚC: khối | texture | engine
KẾT LUẬN: đạt | chưa đạt
Lỗi (lớn trước):
- [mục 1–5] [vị trí] → [khác concept thế nào] → [sửa gì] → [dấu hiệu đạt]
Sửa nhỏ kèm "đạt" (chỉ lỗi kỹ thuật có script đo: pivot, tên object, padding UV, kích thước trong dung sai; ghi script + ngưỡng):
Giữ: [những gì đã khớp concept]
Chưa kiểm được: [...]
```
Có một lỗi ở mục 1–5 → `chưa đạt`. Lỗi nhìn bằng mắt không được xếp vào sửa nhỏ. Người giao việc (hoặc artist, khi người giao việc cho phép) kiểm sửa nhỏ bằng cách chạy lại script đã ghi; pass thì giữ `đạt`, không review lại. Một bước chỉ được một lần `đạt` kèm sửa nhỏ.

## Ví dụ (từ test 1 và bài thử M1)
- Sai: "Đạt kèm điều kiện: thân L như xô; sửa ở bước mesh." → lỗi khối (mục 1), phải `chưa đạt`.
- Sai: "Ảnh ở góc concept giống hệt concept, IoU 0.98 → đạt." → với M1 hai điều này đúng sẵn; phải xem clay ở camera game.
- Đúng: "chưa đạt. [1] RockL ở camera game → clay là khối tròn, concept có ~8 mặt vát lớn và 3 khối chân → cắt thêm mặt vát theo concept → clay ở camera game thấy rõ các mặt vát lớn."
