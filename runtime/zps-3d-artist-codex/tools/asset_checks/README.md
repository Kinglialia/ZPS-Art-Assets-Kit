# asset_checks v0.3.0

Script đo chạy bằng Blender (đã thử với Blender 5.2.3 LTS). Script chỉ đo và so với ngưỡng trong spec của task, không chấm art. Kết quả JSON để trong thư mục bằng chứng của việc (ví dụ `evidence/<bước>/`). Spec (`task/spec.json`) viết từ brief đã duyệt; người giao việc chốt ngưỡng, sau khi chốt artist không tự sửa — cần đổi thì hỏi.

```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
T=<thư mục skill này>/tools/asset_checks
$B -b asset.blend --python $T/mesh_check.py       -- --spec task/spec.json --out ev/mesh.json
$B -b asset.blend --python $T/uv_check.py         -- --spec task/spec.json --out ev/uv.json
$B -b asset.blend --python $T/contact_check.py    -- --spec task/spec.json --out ev/contact.json
$B -b asset.blend --python $T/iou_check.py        -- --spec task/spec.json --out ev/iou.json
$B -b asset.blend --python $T/concept_coverage.py -- --spec task/spec.json --out ev/coverage.json
$B -b asset.blend --python $T/screen_tris_check.py -- --spec task/spec.json --out ev/screen_tris.json
$B -b asset.blend --python $T/render_rig.py       -- --spec task/spec.json --out ev/render.json --outdir ev/renders
$B -b asset.blend --python $T/export_check.py     -- --spec task/spec.json --out ev/export.json
```
Không có Blender app: `python3 $T/<script>.py --input asset.blend --spec ... --out ...` (module `bpy`).
Đường dẫn trong spec (concept, export) tính từ thư mục chứa file spec. Script không lưu đè file .blend.

Nguồn ngưỡng: spec trước. Một số check (ghi rõ bên dưới) lấy mặc định từ `config.yaml` khi spec thiếu key; note của check khi đó ghi `source: config_default (<key>)`. Spec thiếu key và config cũng không có → `info` hoặc `not_checked`, script không tự đặt ngưỡng.

| Script | Đo | Ghi chú |
|---|---|---|
| mesh_check | tris/material so budget, `budget_use` (fail khi dưới `budget.min_tris_ratio`), kích thước, pivot, mesh kín (`expect_closed`), số part (`expected_parts`), mặt suy biến, part bị lật, khoảng cách tới sàn. v0.3: số đỉnh sau export, tỷ lệ tách đỉnh, n-gon, mặt bị che, đỉnh trùng, mặt lật, cạnh smooth > 90° | Đo trên mesh sau modifier. Xem bảng v0.3 |
| uv_check | island, UV ngoài 0–1, overlap, khoảng cách island (px), texel density theo vùng. v0.3: padding mặc định theo độ phân giải, texel density px/m toàn cục và theo island, cạnh cứng phải là UV split (pbr) | Sai số khoảng 1 px |
| screen_tris_check (mới) | tam giác nhỏ (< `min_px_area` px²) và tam giác mảnh ở camera game, kèm `screen_tris.png` | Camera không cố định → info |
| contact_check | khoảng hở/độ lún giữa cặp khai báo, tỷ lệ đáy chạm sàn | v0.2: điểm trong mesh xét bằng ray parity (đúng với mesh kín); tam giác cắt nhau → khoảng cách 0; `vertex_depth_lower_bound_m` chỉ xét đỉnh, phải xem ảnh; lồng cho phép ghi `max_penetration_m` kèm lý do |
| iou_check | IoU silhouette so với concept, từ camera `ConceptCam`; theo từng object khi spec có `iou.polygons_from` (trỏ tới `m1.json` hoặc file cùng dạng) | Ngưỡng `iou.min_iou` (mặc định 0.90). Ảnh `iou_diff.png`: đỏ = thiếu so với concept, xanh = thừa |
| concept_coverage | phần diện tích nhìn thấy ở camera game đến từ mặt concept có vẽ: mặt hướng về `ConceptCam`, không bị che, nằm trong khung concept | Chỉ là thông tin rủi ro, trừ khi task đặt `min_visible`. Camera đọc `fov_v_deg`/`ortho_scale` như render_rig |
| render_rig | khung game kích thước thật, 4 góc × clay/albedo/lit/checker, `sheet.png` | v0.2: camera cố định (`distance_m` hoặc `ortho_scale`) thì check px có nghĩa; thiếu thì là chế độ hiệu chuẩn, check chỉ là info |
| export_check | export GLB (hoặc kiểm GLB có sẵn với `skip_export`), glTF-Validator, material có `KHR_materials_unlit` không (`expect_unlit`), import lại và so số liệu. v0.3: dung lượng file, số đỉnh trong file, chiều cao sau import (trục up, đơn vị), pivot đáy-giữa của file | Có vertex color trong file chưa chứng minh material engine dùng nó |

## Check mới trong v0.3
| Check (script) | Đo gì | Ngưỡng |
|---|---|---|
| `<obj>.exported_vertices` (mesh) | đỉnh GPU nhận: số bộ (material, đỉnh, normal theo góc, mọi lớp UV) khác nhau trên loop của mesh sau modifier, cách io_scene_gltf2 tách đỉnh. Seam UV, cạnh sharp/flat, ranh giới material đều tách đỉnh | `budget.max_vertices_exported`, thiếu thì config `budgets.max_vertices_exported` (65534, index 16-bit) |
| `<obj>.split_vertex_ratio` (mesh) | đỉnh export / đỉnh gốc | `mesh.max_split_vertex_ratio`; thiếu → info, note khi > 2× |
| `<obj>.ngons` (mesh) | mặt > 4 góc (exporter tự tam giác hóa, không kiểm soát được hướng chia) | `mesh.max_ngons`; thiếu → info |
| `<obj>.hidden_face_ratio` (mesh) | tỷ lệ tam giác không tia nào từ ngoài chạm tới: tâm mặt và 4 điểm giữa tâm–góc bắn tia theo 64 hướng (BVH của mọi object đích). Hai mặt: mặt quay lưng vẫn tính là thấy. Ước lượng | `mesh.max_hidden_face_ratio`; thiếu → info |
| `<obj>.duplicate_verts` (mesh) | đỉnh có đỉnh khác cùng object trong `mesh.duplicate_distance_m` (mặc định 1e-4 m) | `mesh.max_duplicate_verts`; thiếu → info |
| `<obj>.flipped_faces` (mesh) | trên từng part kín: tia từ mặt theo normal (và một tia nghiêng) cắt part đó số lẻ lần → normal quay vào trong. Bắt mặt lật lẻ mà `inverted_parts` (thể tích âm) bỏ sót | > 0 là fail (như `inverted_parts`); không có part kín → not_checked |
| `<obj>.smooth_edges_over_90` (mesh) | cạnh smooth có góc giữa 2 normal > 90° (Arm: góc smooth < 90°, đánh sharp) | `mesh.max_smooth_edges_over_90`; thiếu → info; toàn mặt flat → not_checked |
| `total.materials` (mesh) | đã có từ v0.2 | `budget.max_materials_total`; thiếu → info, ghi giá trị config `budgets.max_materials` |
| `screen.small_tri_ratio` (screen_tris) | tỷ lệ tam giác mặt trước, trong khung, diện tích < `min_px_area` px² ở camera game. Tam giác nghiêng quá 75° so với hướng nhìn (`grazing_deg`) không tính: mặt cong nào cũng có ở viền | `min_px_area`: `screen_tris.min_px_area` → `validate.sliver_min_px_area` (spec) → config `validate.sliver_min_px_area` (10). Tỷ lệ: `screen_tris.max_small_ratio`; thiếu → info |
| `screen.thin_tris` (screen_tris) | tam giác có chiều cao theo cạnh dài nhất < `thin_max_px` (1) và cạnh dài nhất > `thin_min_long_px` (50). Bao cả luật "cạnh ngắn nhất < 1 px" | `screen_tris.max_thin`; thiếu → info |
| `<obj>.min_island_gap_px` (uv) | như v0.2 | `uv.min_padding_px`; thiếu → config `texture.padding_px_by_res[uv.resolution]` (độ phân giải không có trong bảng: suy từ mục gần nhất theo tỷ lệ) |
| `<obj>.texel_density.global` / `.islands` (uv) | px/m toàn cục = √(diện tích UV px / diện tích thật); theo island: min, max, max/min. Island < 0.5 % diện tích chỉ liệt kê | `uv.texel_density_px_per_m` ± `uv.density_tolerance` (tỷ lệ); thiếu → info, kèm giá trị config để tham khảo |
| `<obj>.hard_edges_without_uv_split` (uv) | cạnh cứng (đánh sharp hoặc kề mặt flat, 2 normal lệch > 1°) mà 2 mặt dùng chung UV. Đọc từ tọa độ UV, không từ cờ seam | `style: pbr` → > 0 là fail; `hand_painted`/không ghi → info |
| `gltf_validator.errors` / `.warnings` / `.infos` (export) | Khronos glTF-Validator: `export.validator` → `gltf_validator` trên PATH → `node gltf_validate.mjs` (gói npm `gltf-validator` là thư viện, không có CLI; cài `npm i -g gltf-validator`) | errors > 0 fail; warnings, infos là info kèm mã lỗi; không tìm được → not_checked |
| `file.size_mb` (export) | dung lượng GLB | `validate.max_file_size_mb`; thiếu → config `validate.max_file_size_mb` |
| `file.vertices.<mesh>` (export) | tổng `count` của accessor POSITION trong file theo mesh | như `exported_vertices` |
| `file.height_m` (export) | chiều cao bbox sau khi import lại (glTF Y-up → Blender Z). Export Z-up hoặc theo cm lộ ra ở đây | `height_m` ± `dimensions_tolerance`; thiếu → info |
| `asset.pivot_bottom_center` (export) | đáy-giữa bbox của asset sau import so với gốc file; từng object là info | khi `pivot: bottom_center`: mọi trục ≤ 0.01 m |
| `file.reimport` (export) | file import lại được không (trước đây script chết, không ghi JSON) | lỗi import → fail |

Vì sao sliver là script riêng mà không nằm trong render_rig: không cần render (chiếu tam giác bằng ma trận camera, chạy dưới 1 s), cho số pass/fail chạy lại nhanh, còn render_rig là công cụ hỗ trợ xem ảnh và chậm nhất. Hai script dùng chung `ac_common.game_camera`/`place_camera`; ở chế độ hiệu chuẩn cả hai giải ra cùng khoảng cách (thử: 3.537 m và 4.2939 m).

## Camera game
Mọi script dựng camera bằng `ac_common.game_camera` từ `spec.camera`: `fov_v_deg` (FOV dọc, lấy từ engine) hoặc `lens_mm`; ortho cần `ortho_scale`; `distance_m`, `look_at`, `azimuth_deg`, `elevation_deg`. Camera cố định khi phối cảnh có `distance_m` hoặc ortho có `ortho_scale`; thiếu thì check pixel và coverage chỉ là info.

## Khóa camera game
Lần đầu chạy `render_rig` không có `distance_m`: script giải khoảng cách cho đúng `target_px_height` và ghi vào `data.camera`. Chép `distance_m` và `look_at` vào spec; từ đó mọi lần render dùng cùng camera và check px là phép kiểm thật.

## Thay đổi trong v0.3.0
- `mesh_check`: thêm 7 check ở bảng trên; `total.materials` ghi giá trị config khi spec thiếu ngưỡng; data có `materials_used` (material có mặt dùng).
- `uv_check`: padding mặc định theo config; texel density toàn cục và theo island; cạnh cứng ↔ UV split.
- `screen_tris_check.py` mới: tam giác nhỏ/mảnh ở camera game, ảnh `screen_tris.png`.
- `export_check`: validator qua `gltf_validate.mjs` (node), dung lượng file, số đỉnh trong file, chiều cao/trục up, pivot của file; file hỏng không làm script chết nữa.
- `ac_common`: `TOOL_VERSION` 0.3.0; `config_value`, `threshold`, `source_note` (đọc `config.yaml` qua `tools/lib/common.load_config`), `fibonacci_dirs`, `calibrate_distance`.
- Spec mới (tùy chọn): khối `mesh` {`max_split_vertex_ratio`, `max_ngons`, `max_hidden_face_ratio`, `duplicate_distance_m`, `max_duplicate_verts`, `max_smooth_edges_over_90`}, `budget.max_vertices_exported`, `screen_tris` {`min_px_area`, `max_small_ratio`, `max_thin`, `thin_max_px`, `thin_min_long_px`, `grazing_deg`}, `uv.texel_density_px_per_m`, `uv.density_tolerance`, `validate.max_file_size_mb`, `validate.sliver_min_px_area`; dùng sẵn `height_m`, `style`.

## Thay đổi từ v0.1.0
- `render_rig`: camera cố định; v0.1 tự giải camera nên check 250px luôn pass (INC-005 test rock-moss-01).
- `contact_check`: ray parity thay pháp tuyến mặt gần nhất; v0.1 báo lún 1.71 m sai (INC-007). `no_penetration` giờ cũng kiểm đỉnh nằm trong object kia.
- `export_check`: `skip_export`; đường dẫn tính theo spec (INC-017).
- Thêm `iou_check`, `concept_coverage`; `ac_common` thêm `concept_mask`, `render_alpha`.

Kết quả thử trên M1 cụm đá của bản v0.2 trước khi mất file (cloud, Blender 5.2.3, chưa chạy lại trên bản dựng lại): 7/7 script chạy; IoU 0.978 (RockS 0.992, RockL 0.969); coverage camera game 0.687, bên 0.024, sau 0.0; lún RockS–RockL 0.136 m (v0.1 báo 1.08 m).

## Kiểm bản dựng lại (2026-11-03, cloud, bpy 5.2.3, scene thử 2 khối cầu — không phải asset thật)
- 9 script chạy hết trên cùng spec mẫu.
- `budget_use` 0.107 < 0.3 → fail; `target_px_height` hiệu chuẩn → info, chép `distance_m`/`look_at` vào spec → pass 250 px.
- Lồng 2 khối: `no_penetration` không có `max_penetration_m` → fail; có 0.15 m → pass (đỉnh sâu nhất 0.095 m).
- `iou_check` với concept là silhouette của chính scene: 0.9999; theo object qua `polygons_from` ≥ 0.996.
- `export_check`: material Background → GLB có `KHR_materials_unlit`; `expect_unlit: false` → fail; `skip_export` đọc GLB có sẵn.
- `concept_compare.png` khớp vị trí concept. Chưa chạy: glTF-Validator, Mac, Godot, concept đá thật.


## Kiểm v0.3.0 (2026-11-03, container cloud, Python 3.13 + module bpy 5.2.3, node 22, gói npm gltf-validator 2.0.0-dev.3.10)
Scene thử dựng bằng bpy (không phải asset thật), spec viết từ `spec.template.json`:
- (1) `Barrel`: 832 tris, 1 material, UV tay (3 island, khe > 16 px), pivot đáy-giữa, cao 0.8 m, sườn smooth, nắp flat, viền nắp sharp = UV split.
- (2) `BadCrate`: 216 tris, 2 material, 5 n-gon, hộp kín nằm trong, núm không weld (24 đỉnh trùng), 2 mặt lật, vây smooth góc 140°, nẹp 2 mm (sliver), 12 bu-lông 6 mm (tam giác nhỏ), UV liền một hàm của vị trí (không split ở cạnh cứng, các part chồng UV), pivot ở góc, export `yup: false`.

Camera: chạy `render_rig` hiệu chuẩn 400 px, chép `distance_m`/`look_at` vào spec, rồi chạy lại mọi script với camera cố định.

| Check | (1) Barrel | (2) BadCrate |
|---|---|---|
| exported_vertices | 495 ≤ 65534 (config_default) pass | 406 > 300 (spec, thử nhánh fail) fail |
| split_vertex_ratio | 1.184 ≤ 2 pass | 2.57 fail |
| ngons | 0 pass | 5 fail |
| hidden_face_ratio | 0.0 pass | 0.194 (42/216 tris: hộp trong, mặt áp vào thân) fail |
| duplicate_verts | 0 pass | 24 fail |
| flipped_faces | 0 / 448 pass | 2 / 95 fail (`inverted_parts` vẫn pass: thể tích dương) |
| smooth_edges_over_90 | 0 pass | 3 fail |
| total.materials | 1 pass | 2 fail |
| screen.small_tri_ratio | 0 / 392 pass (8 tam giác viền nghiêng bị loại) | 48 / 106 = 0.45 fail |
| screen.thin_tris | 0 pass | 4 (nẹp) fail |
| min_island_gap_px (config 8 px) | > 16 pass | 1 fail |
| texel_density.global / .islands (540 ± 20 %) | 531.1 pass / 528.6–539.6 pass | 523.4 pass / min 104.8 fail |
| hard_edges_without_uv_split | 0 / 64 pass | 188 / 188 fail |
| gltf_validator.errors | 0 pass | 0 pass (file hợp lệ); GLB cố tình hỏng: 4 lỗi (ACCESSOR_TOO_LONG…) fail |
| file.size_mb | 0.021 ≤ 5 (config_default) pass | 0.016 > 0.01 (spec, thử nhánh fail) fail |
| file.vertices | 495 pass | 406 fail |
| file.height_m | 0.8 pass | 0.406 thay vì 1.25 (Z-up) fail |
| asset.pivot_bottom_center | [0,0,0] pass | [0.35, −0.625, −0.006] fail |

- Số đỉnh ước tính của `mesh_check` khớp số đỉnh thật trong GLB (validator `totalVertexCount` và accessor): 495 = 495, 406 = 406.
- Nhánh khác: không có node trên PATH → `gltf_validator` not_checked; spec thiếu khối `mesh`/`screen_tris`/density → info; `style: hand_painted` → info; `uv.resolution` 768 → padding 6 px suy từ 1024; GLB hỏng → `file.reimport` fail và vẫn ghi JSON.
- Hồi quy: `iou_check` (concept = silhouette của chính scene) 1.0; `concept_coverage` 0.929; `contact_check` pass; `render_rig` pass 400 px.
- Đã mở `sheet.png` cả hai scene và `screen_tris.png`: (2) nẹp vàng, 12 bu-lông đỏ; (1) không có đỏ/vàng.
- Chưa chạy: Blender app (chỉ module bpy), macOS, CLI `gltf_validator` gốc (chỉ qua node), asset thật, mesh lớn (mặt bị che dùng tia Python: 64 hướng × tối đa 5 điểm cho mặt bị che, có thể chậm với > 50k mặt).
