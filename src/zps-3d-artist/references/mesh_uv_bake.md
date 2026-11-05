> Vai trò trong skill này: "người giao việc", "người giữ chuẩn hình ảnh", "người duyệt" = người dùng. "Review độc lập" chỉ khi có reviewer tách biệt thực sự; không mặc định gọi subagent. Ngưỡng nằm trong `task/spec.json`; số đo lấy từ script trong `tools/`. Nguồn: skill art-3d-artist v0.1.0.

## B. Hoàn thiện mesh / chỉnh model
**Nhận:** blockout/nguồn đúng phiên bản, mốc duyệt có liên quan và delta cần làm.
- Ghi Gốc/Giữ/Đổi; làm khối chính → phụ → chi tiết. Parametric phù hợp sửa số; sculpt phục vụ hình hữu cơ; retopo theo nhu cầu tái cấu trúc mesh, không bắt buộc theo loại asset; modular theo grid/snap. Không bắt mọi asset từ primitives hoặc image-to-3D.
- Chọn topology theo shading, silhouette, subdivision/deformation và export. Không ép all-quads/watertight cho mọi asset. Chỉ giữ intersect/open surfaces có chủ đích và hợp pipeline; bỏ lỗi degenerates, mặt trùng, normals ngược, z-fighting, phần nổi/lọt ngoài ý muốn.
- Kiểm soát scale và modifier theo kết quả; không apply tất cả transforms/modifiers vào rig/nguồn một cách máy móc. Thao tác phá hủy thực hiện trên bản riêng khi cần giữ nguồn. Giảm geometry bằng cách phù hợp, kể cả retopo/decimate nếu giữ yêu cầu; kiểm tra lại silhouette/shading/UV.
- Budget triangle/material/vertex lấy theo task; kiểm triangles sau modifier ngay từ blockout và ở mốc hoàn thiện khối, không chờ export mới đo. Nếu dựng script, để số segment/bevel/subdivision và mật độ chi tiết thành tham số dễ chỉnh; không cần mở report sau mỗi tool. Đo lại bản export khi có. LOD/collision/deformation chỉ làm khi được giao. Kiểm tra chuyển động cần thiết bằng bằng chứng thực, không nhận đạt chỉ vì có edge loops.
- Với bộ phận gắn/lắp ghép: kiểm tra mặt tựa, đầu nối và giao điểm bằng góc cận hoặc mặt cắt phù hợp trước khi chuyển texture. Phân biệt khe có chủ đích với lỗi hở; tránh xử lý z-fighting bằng cách đặt nổi toàn bộ chi tiết mà không kiểm tra lại kết cấu. Ghi bằng chứng cho mối nối quan trọng, không suy từ silhouette/UV pass.
**Giao:** mesh/source phiên bản mới, số liệu, ảnh clay/wire hoặc matcap theo vấn đề; so phần giữ/đổi, lỗi còn lại và phần downstream cần kiểm tra lại.

## Giảm mặt và retopo khi cần

Sửa nguyên nhân dư mặt trước: giảm segment/modifier quá cao, dissolve cạnh không đóng góp, bỏ geometry nhỏ có thể thể hiện bằng bề mặt theo 00-style-method.md. Bỏ mặt trong/đáy/bị che chỉ sau khi xác nhận không cần cho toàn bộ góc nhìn, bóng, chuyển động và tương tác của task; giữ cấu tạo cần thiết.

Mesh có cấu trúc đơn giản: chỉnh trực tiếp trước. Mesh sinh từ AI/sculpt quá dày, khó sửa hoặc không đáp ứng deformation: cân nhắc retopo để bố trí lại mặt. Giảm nhanh cho khoảng nhìn xa có thể thử decimate/LOD khi phù hợp. Không mặc định dựng dày rồi retopo mọi asset, không coi auto-remesh là bảo đảm giữ hình hoặc giảm triangles.

Retopo chỉ thực hiện khi lợi ích về budget, khả năng sửa hoặc deformation bù được công dựng lại/UV/bake. Giữ bản gốc, đối chiếu trước/sau ở camera và các góc cần dùng: silhouette, tỷ lệ, đặc điểm nhận diện, normals/shading và chuyển động nếu có. Texture/UV có thể cần chuyển hoặc làm lại; kiểm các map bị ảnh hưởng. Bake chi tiết bề mặt khi cần, không dùng normal để bù khối/đường viền đã mất. Dùng cùng tiêu chí và mốc kiểm hiện hành, không thêm một workflow/reviewer riêng.

## Bevel và custom/weighted normals

### Khi dùng

Dùng bevel khi cạnh cần có mặt vát thật để bắt sáng hoặc giữ hình ở góc nhìn gần. Dùng custom/weighted normals khi cần điều chỉnh shading, như giữ mặt lớn trông phẳng trong khi vùng cạnh chuyển sáng mềm.

Hai kỹ thuật có thể phối hợp. Weighted normals không tạo mặt vát, không sửa silhouette và không thay việc xử lý geometry lỗi. Với style cố ý để mặt phẳng hoặc cạnh sắc, giữ cách thể hiện đã duyệt.

### Cách làm

1. **Xác định cạnh cần xử lý.** Chọn theo concept, cấu tạo, vật liệu và camera đích; không bevel toàn bộ cạnh một cách máy móc.
2. **Chọn độ rộng bevel.** Dựa trên tỷ lệ thiết kế và độ hiện rõ ở kích thước sử dụng. Kiểm scale và ảnh hưởng của transforms/modifier trước khi chỉnh; không apply phá hủy nguồn một cách mặc định.
3. **Chọn số segment vừa đủ.** Bắt đầu ít rồi tăng khi đường cong hoặc highlight còn gãy ngoài ý đồ. Không mặc định một segment phù hợp mọi cạnh.
4. **Thiết lập shading.** Chọn vùng smooth/sharp có chủ đích. Thử custom/weighted normals khi cần giữ mặt lớn sạch; kiểm modifier order và kết quả thực theo phiên bản Blender.
5. **Kiểm vùng khó.** Xem góc lõm, cạnh ngắn, giao nhiều cạnh và kết quả Boolean; sửa bevel bị chồng, bóp méo hoặc tạo mặt suy biến.
6. **Kiểm tác động downstream.** Nếu dùng normal bake, thống nhất trạng thái geometry, triangulation và normals trước bake. Thay các dữ liệu này sau bake phải kiểm lại map liên quan.

### Cách kiểm

Xem model ở camera/kích thước đích và góc cận cần thiết. Dùng ánh sáng hoặc matcap giúp đọc mặt và cạnh; kiểm highlight liên tục, mặt lớn không lõm/phồng ngoài ý đồ và silhouette vẫn đúng.

So bật/tắt bevel hoặc weighted normals khi cần xác định tác dụng. Kiểm lại bản export để xác nhận geometry và normals được giữ, đồng thời đo triangles/vertices thực theo budget task.

### Lỗi thường gặp

| Dấu hiệu | Cần kiểm |
|---|---|
| Mặt phẳng trông lõm hoặc phồng | Geometry, smooth/sharp, normals và modifier order |
| Bevel rộng không đều | Scale, thiết lập bevel và cấu trúc cạnh |
| Góc bị bóp hoặc giao nhau | Cạnh quá ngắn, độ rộng bevel, cách xử lý góc và topology |
| Cạnh vẫn gãy ở góc cần nhìn | Segment, normals và hình dạng thực |
| Thêm nhiều mặt nhưng hình không cải thiện | Độ hiện rõ ở camera đích; giảm hoặc bỏ bevel không có giá trị |
| Blender đúng nhưng export lệch | Normals, triangulation, modifier được xuất và import settings |

Sửa nguyên nhân hình học trước khi dùng normals để điều chỉnh shading. Giữ source chỉnh sửa được và ghi phần chưa kiểm chứng.
## C. UV → bàn giao texture/bake
**Nhận:** mesh tương đối ổn định, cách texture (unique/tiling/trim/atlas/palette), resolution và yêu cầu bake được chốt hoặc đề xuất còn mở.
- Phân bổ UV theo ưu tiên đọc trong brief và các góc sử dụng: vùng nhận diện/tương tác/mặt chính cần pixel phù hợp, phần ít thấy có thể giảm. Dùng mirror/stack/tái sử dụng khi phù hợp, giữ chi tiết unique cần thiết. Chọn seam theo hình/shading/cách bake; kiểm checker, distortion và độ rõ vùng ảnh hưởng. Không ép density như nhau hoặc tăng toàn atlas để bù vùng ưu tiên đang quá nhỏ. Đo chi tiết theo điều kiện kiểm sau sửa ở dưới.
- Padding theo resolution/mip/pipeline; overlap/stack/mirror/UV ngoài 0–1 chỉ khi có chủ đích và phù hợp cách texture/bake. UV lightmap/UDIM không tự thêm nếu đích không cần/hỗ trợ.
- Nếu bake: chuẩn bị high/low, triangulation/tangent basis tương thích và test bake khi task có giao; ghi các phần chưa thử. Không bake ánh sáng vào base color như mặc định cho mọi style.
**Giao:** source/mesh+UV có phiên bản, material slots/tên vùng, kết quả kiểm UV/checker và padding/overlap liên quan; density kèm phương pháp/đơn vị khi task cần đo. Giao thiết lập bake nếu có. Bên texture/material nhận phần texture; 3D Artist chỉ tự làm texture khi được giao. Sửa mesh/UV thì nêu texture/bake/rig bị ảnh hưởng.


**Owner bake:** 3D Artist chuẩn bị high/low, UV và geometry/tangent; bên texture/material chuyển look/map/procedural. High→low bake chỉ có một owner do người giao việc chỉ định, kèm input/output version; không mặc định cả hai cùng thực hiện.

**Kiểm sau sửa/repack UV theo ảnh hưởng:** kiểm checker, distortion, padding và độ rõ tại camera/kích thước đích ở vùng đã đổi. Đo density/occupancy/diện tích theo vùng khi task có ngưỡng, đổi phân bổ lớn, nguy cơ thiếu độ rõ hoặc đang chẩn đoán lỗi; không bắt đo đầy đủ mọi material sau chỉnh nhỏ. Khi đo, ghi units, resolution thực, phương pháp và UV version; số cũ liên quan hết hiệu lực. Dùng lại kiểm tra vùng không đổi. Zero-overlap hoặc pack margin không chứng minh độ rõ/padding đã đạt. Thiếu độ rõ thì điều chỉnh phân bổ trong quyền hoặc trình ngoại lệ trước full bake.

## Chuẩn bị và kiểm normal bake high→low

### Khi dùng

Dùng khi cần chuyển chi tiết bề mặt từ high-poly sang low-poly để giữ phản ứng ánh sáng với ít geometry hơn. Normal map không thay silhouette, độ dày, khoảng hở hoặc bóng đổ hình học thật.

Dùng lại bằng chứng bake còn phù hợp; khi có rủi ro mới, thử vùng đại diện trước toàn asset để xác nhận chi tiết còn đọc được ở camera, kích thước hiển thị và shader đích. Không mặc định mọi asset đều cần high-poly hoặc normal map.

### Trách nhiệm

3D Artist chuẩn bị high/low, UV, normals/tangent và trạng thái triangulation. Người giao việc chỉ định một owner thực hiện bake và giữ thiết lập có thể chạy lại. Bên texture/material phối hợp kiểm map và look; 3D Artist kiểm lỗi liên quan geometry/UV và bản export.

### Chuẩn bị

1. **Khóa đầu vào cho lần bake.** Ghi phiên bản high/low, units, transforms, UV set và các modifier ảnh hưởng kết quả. Hai bản phải khớp vị trí và hình khối cần chuyển.
2. **Chuẩn bị low-poly.** Giữ silhouette và cấu tạo cần thiết; kiểm normals, vùng smooth/sharp và triangulation sẽ dùng khi export. Thay topology, UV, normals hoặc triangulation sau bake phải kiểm lại phần ảnh hưởng.
3. **Chuẩn bị UV.** Unique bake cần vùng ghi không xung đột. Mirror/stack chỉ dùng có chủ đích và có cách tránh ghi đè; không coi mọi overlap đều sai. Với tangent-space bake, tách UV tại hard edge để có padding riêng; UV seam không bắt buộc phải là hard edge.
4. **Chọn resolution và padding.** Dựa trên phân bổ UV, độ rõ cần thiết, mip và budget. Không áp một số pixel margin cho mọi resolution; kiểm khoảng cách và dilation thực sau bake.
5. **Khớp quy ước đích.** Xác nhận tangent basis, normal convention, UV set và cách import. Không suy chỉ từ tên engine hoặc tên file.

### Thực hiện

1. Chọn đúng source high-poly, low-poly nhận bake và ảnh đích; kiểm bằng một lần bake nhỏ trước khi chạy rộng.
2. Thiết lập cage hoặc ray distance để bắt đủ bề mặt cần chuyển và tránh lấy nhầm chi tiết lân cận. Cage tùy chỉnh phải đáp ứng yêu cầu topology của công cụ.
3. Với phần sát nhau, điều chỉnh cage, tách nhóm bake hoặc dùng cơ chế matching khả dụng. Không tăng ray distance toàn asset để che lỗi cục bộ.
4. Bake tangent-space normal khi phù hợp pipeline; ghi channel convention và thiết lập đã dùng.
5. Gán map vào đúng slot, xử lý như dữ liệu normal thay vì texture màu; xác nhận shader thực sự sử dụng map.

### Cách kiểm

Kiểm cả map và kết quả trên low-poly. So bật/tắt normal trong cùng camera, ánh sáng và material; xem vùng đại diện ở kích thước sử dụng và góc cận để tìm lỗi.

Kiểm seam, chi tiết bị lệch, vệt projection, vùng mất dữ liệu, hướng lồi/lõm và bleed khi xem xa. Mở bản export tại đích theo scope để kiểm normal convention, tangent và compression.

Ảnh map trông sạch chưa đủ chứng minh bake đạt. Chưa kiểm tại đích phải ghi rõ giới hạn.

### Lỗi thường gặp

| Dấu hiệu | Cần kiểm |
|---|---|
| Chi tiết lồi thành lõm hoặc bắt sáng sai hướng | Channel convention, cách gán map và thiết lập import |
| Vệt ở seam hoặc cạnh cứng | UV/padding, normals, tangent basis và triangulation |
| Chi tiết kéo dài, lệch hoặc lấy nhầm bộ phận | Cage, ray direction/distance và nhóm bake |
| Vùng đen, trống hoặc thiếu chi tiết | Source/target, độ bao phủ ray, normals và ảnh đích |
| Gần đẹp nhưng xa bị bẩn hoặc nhấp nháy | Mip, padding, compression và chi tiết quá nhỏ |
| DCC đúng nhưng engine sai | Material, tangent, convention, import và dữ liệu export thực |

Chẩn đoán bằng thử ít biến. Không mặc định lật kênh xanh hoặc tăng resolution cho mọi lỗi.

### Bàn giao

Giao normal map, phiên bản high/low và UV, resolution thực, channel convention, thiết lập cage/ray và bằng chứng kiểm. Ghi rõ owner, phần đạt, lỗi còn tồn và điều kiện phải bake lại.
