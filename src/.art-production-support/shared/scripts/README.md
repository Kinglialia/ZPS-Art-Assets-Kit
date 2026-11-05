# Công cụ — chạy theo thao tác, không là stage bắt buộc

Python 3.10+. Pillow cần cho preview/palette/sprite/inspect; generate_image và check_gate dùng standard library; render_model cần `bpy`. Chạy bằng đường dẫn tuyệt đối tới scripts của package:

```sh
ART_TOOLS=/absolute/path/to/skills/.art-production-support/shared/scripts
# Resolve this path from the actual install root.
```

Mọi tool ghi file đều từ chối ghi đè: đặt tên có version (`icon_sword_v3.png`).

<a id="generate"></a>
## Gen/edit ảnh — tốn tiền mỗi lần gọi

```sh
echo '{"max": 3, "used": 0}' > task-budget.json   # budget do task/user duyệt
python "$ART_TOOLS/generate_image.py" --provider gemini --model "$ART_IMAGE_MODEL" \
  --prompt-file prompt_v1.txt --image style_anchor.png --image asset_mau.png \
  --out icon_sword_v1.png --budget-file task-budget.json
```

Luôn chạy `--dry-run` trước khi đổi cấu trúc yêu cầu. Key chỉ lấy từ biến môi trường `GEMINI_API_KEY` / `OPENAI_API_KEY`. Mỗi output kèm file `.json` ghi prompt, input hash, model — chép vào task record. Hết budget: exit 3, dừng và chẩn đoán. Mask chỉ dùng với OpenAI (vùng trong suốt là vùng được sửa); Gemini sửa theo mô tả vùng nên phải kiểm vùng giữ bằng `inspect_image.py --lock-mask`. Viết prompt theo [chuẩn chất lượng](../../rules/art-quality.md).

<a id="preview"></a>
## Preview để tự nhìn

```sh
python "$ART_TOOLS/preview.py" sheet icon_v2.png --sizes 48 64 128 --backgrounds light dark "#2b2140" --out sheet_v2.png
python "$ART_TOOLS/preview.py" compare icon_v2.png ref_R1.png ref_R2.png --height 256 --small 64 --out cmp_v2.png
python "$ART_TOOLS/preview.py" value concept_v3.png --small 96 --out value_v3.png
python "$ART_TOOLS/preview.py" tile ground_v1.png --repeat 3 --out tile_v1.png
```

Output là ảnh **phải mở ra xem**; tool không chấm điểm. `--nearest` cho pixel art.

<a id="score"></a>
## Chấm và chọn phương án

```sh
python "$ART_TOOLS/score_variants.py" cand_a.png cand_b.png cand_c.png --reference ref_a.jpg --reference ref_b.jpg --palette style_palette.json
```

`--profile` (không cần candidate) in màu trung bình 5% pixel tối nhất, cast từng dải và value của từng reference — dùng khi lập style sheet.

Xếp hạng theo độ lệch cast màu từng dải sáng, màu vùng tối, value và palette so với Execution reference **cùng loại deliverable**. Thấp = gần reference. Trọng số là ước lượng chưa calibrate: chỉ so total trong cùng lần chấm. Là gate/tie-breaker: vẫn mở top 2–3 và review mắt. Bỏ qua pixel trong suốt. Cần numpy.

<a id="tone-match"></a>
## Chỉnh màu theo reference (không gen)

```sh
python "$ART_TOOLS/tone_match.py" scene_v3.png --reference ref_a.jpg --reference ref_b.jpg --bands shadows midtones --strength 0.8 --out scene_v3_tm1.png
python "$ART_TOOLS/structure_diff.py" scene_v3.png scene_v3_tm1.png --max-lightness-changed 0.02 --min-edge-agreement 0.95
```

Dời cast màu (a*/b* trong Lab) của dải tối/trung/sáng về cast của reference; giữ nguyên độ sáng, hình và alpha. Dùng khi cấu trúc đạt nhưng màu lệch. Không chỉnh dải sáng nếu trời/highlight đã đúng. Cần numpy.

`structure_diff.py` xác nhận bản edit giữ hình: % pixel đổi độ sáng quá `--l-tol` và tỷ lệ cạnh còn khớp (Sobel trên L*). Dùng cho mọi edit "chỉ đổi màu" hoặc phải giữ hình; giữ pixel tuyệt đối thì dùng `inspect_image --lock-mask`.

<a id="palette"></a>
## Palette

```sh
python "$ART_TOOLS/palette_report.py" icon_v2.png --palette bible_palette.json --max-delta 10
```

Báo màu chủ đạo, màu gần nhất trong palette và ΔE (CIE76). `off_palette` là dấu hiệu cần nhìn, không tự là lỗi: antialias và ánh sáng tạo màu trung gian hợp lệ.

<a id="sprites"></a>
## Frame sequence

```sh
python "$ART_TOOLS/sprite_check.py" walk_*.png --max-baseline-shift 1
python "$ART_TOOLS/sprite_check.py" walk_sheet.png --grid 8 1
```

Kiểm canvas đồng nhất, frame rỗng và độ trôi baseline/tâm theo alpha. Không đánh giá pose hay nhịp.

```sh
python "$ART_TOOLS/anim_preview.py" walk_*.png --height 128 --fps 12 --out walk_v2
python "$ART_TOOLS/anim_preview.py" walk_sheet.png --grid 8 1 --nearest --step 2 --out walk_v2
```

Xuất `<out>_strip.png` (filmstrip), `<out>_onion.png` (onion skin: frame đầu mờ, frame cuối đậm; ngả xanh → đỏ theo thứ tự) và `<out>.gif` theo fps. Agent mở filmstrip và onion skin để xem quỹ đạo, khoảng cách pose, chỗ giật. GIF dành cho người xem; agent không xem được chuyển động, nên nhịp và cảm giác ghi `not_checked` nếu chưa có người xem. Frame khác cỡ canvas thì dừng; chạy `sprite_check.py` trước. Không ghi đè file có sẵn.

<a id="svg"></a>
## SVG → PNG cho UI

```sh
python "$ART_TOOLS/svg_render.py" btn_play_normal.svg btn_play_pressed.svg --scales 1 2 --out-dir export/ui
```

Xuất `<tên>.png` (1x = width/height px của SVG) và `<tên>@2x.png`, nền trong suốt. Dùng resvg (`pip install --user resvg-py==0.5.0`); không có thì dùng Chrome headless nếu tìm thấy. Báo cảnh báo khi SVG có `<text>`, filter, mask, script, foreignObject. Không ghi đè file có sẵn. PNG này là file giao cho engine theo mặc định; mở bằng `preview.py sheet` để kiểm ở kích thước hiển thị.

<a id="model"></a>
## Đánh giá model (Blender headless)

```sh
python "$ART_TOOLS/inspect_model.py" prop_v4.glb --texture-size 1024
```

Báo số tam giác, kích thước, material, UV set, UV coverage/overlap (tính cả chồng giữa các object dùng chung ảnh)/out-of-range, vertex color, texel density ở kích thước texture dự kiến. Chỉ đọc. Dùng cho texture planning; overlap và out-of-range có thể có chủ đích (mirror, tileable, trim).

<a id="render"></a>
## Render model (Blender headless)

```sh
python "$ART_TOOLS/render_model.py" prop_v4.glb --mode checker --views 4 --out-dir renders_checker_v4
python "$ART_TOOLS/render_model.py" prop_v4.glb --mode textured --texture albedo_v2.png --out-dir renders_tex_v2
```

Chạy bằng Python có `bpy` (môi trường đã có module bpy phù hợp) hoặc `blender -b -P render_model.py -- ...` trên Mac. `clay`: form; `checker`: UV distortion/density; `textured`: texture trên model. Cycles CPU ánh sáng trung tính — không thay kiểm trong Godot.

<a id="image-checks"></a>
## Kiểm file ảnh khi cần số đo

```sh
python "$ART_TOOLS/inspect_image.py" /path/output.png --size 1024 1024 --require-alpha
python "$ART_TOOLS/inspect_image.py" /path/revision.png --reference /path/source.png --lock-mask /path/locked.png --out /path/image-checks-v2.json
```

Mask grayscale khác 0 là vùng cần giữ RGBA chính xác. Đây không phải yêu cầu mặc định cho mọi edit: giữ thiết kế/nhận diện khác với giữ từng pixel. Mask trống/khác size bị từ chối; không auto-resize. Báo cáo ghi hash của output và reference/mask đã đo, không sửa ảnh. --out chỉ tạo file mới để giữ bằng chứng bản cũ.

Alpha channel có thể hoàn toàn opaque; pass không chứng minh transparency, mép sạch hay đúng premultiplication. Exit 0 cho checks đã chạy đạt; 1 có fail; 2 lỗi input/dependency. Không nhận art đạt từ decode pass. Thiếu Pillow chỉ chặn số đo này; dùng metadata/visual inspection tương đương khi đủ cho task, ghi phần chưa đo.

<a id="projection-guide"></a>
## Guide chỉ khi có camera-space geometry

```sh
python "$ART_TOOLS/projection_guide.py" "$ART_TOOLS/examples/camera-box.json" --out /path/new-guide.svg
```

X phải, Y lên, Z về phía cảnh; perspective dùng vertical FOV/aspect, ortho dùng vertical span. Không suy camera từ ảnh, không đo artwork/anatomy; không hỗ trợ clipping, lens shift/distortion/crop. Refuse overwrite. Khi không có tọa độ thật, dựng bằng guide quan sát hoặc DCC trong quyền, không bịa số để chạy tool.

<a id="evidence-gate"></a>
## Gate chỉ cho nghiệm thu tự động đã định nghĩa

Quick review không cần JSON/gate. Caller cần gate thì chốt required IDs và artifact version trước:

```json
{"required": ["decode", "locked_pixels"], "artifact_sha256": "<SHA256 của output cần nghiệm thu>"}
```

Dùng thẳng report inspector đã lưu, không ghép lại JSON:

```sh
python "$ART_TOOLS/check_gate.py" --spec /path/gate.json --measurement /path/image-checks-v2.json
```

--measurement kiểm identity của artifact/reference/mask và dùng chính file report làm evidence. Report format phải là art_image_inspector schema 1. Header này không phải chữ ký; tool kiểm tính toàn vẹn và trạng thái được báo, không xác nhận ai đã thực thi hoặc chất lượng ảnh.

Với nhiều loại bằng chứng, dùng --report thay --measurement: report có artifact {path, sha256}, inputs nếu cần, checks [{id, status, evidence: {path, sha256}, reason}]. Path tương đối theo report hoặc tuyệt đối. Required pass phải có evidence đúng hash; fail/not_checked/missing chặn; N/A cần allow_not_applicable trong spec và reason. Không tự bỏ required, đổi spec/version hoặc miễn trừ để lấy pass.

Exit 0 = required statuses/evidence hợp lệ; 1 = chưa đủ; 2 = input lỗi. Other checks được trả riêng. Gate không cấp art approval; lời nhận xét trong report vẫn cần reviewer chịu trách nhiệm.
