# Cơ chế tự học cho skill art — nghiên cứu và thiết kế đề xuất

Ngày 2026-11-04. Tổng hợp từ 3 nhánh nghiên cứu: (1) học thuật về agent tự cải thiện, (2) những gì đã có trên máy (qstack, skill-creator, 3d-artist), (3) thực tế studio và pipeline sản phẩm AI. Nhãn: **[C]** đọc từ nguồn gốc, **[S]** từ tóm tắt/blog, **[I]** suy luận của em. Nhiều host (arxiv, gdcvault, langfuse) bị chặn trong session nên số liệu học thuật lấy từ abstract.

---

## 1. Kết luận chính

**Bài học phải sống đầu tiên dưới dạng dữ liệu, lên thành check trong code khi lặp lại có người xác nhận, và chỉ thành câu chữ trong SKILL.md khi không đo được.** Đây là ngược với cách đa số team làm (viết thêm rule vào prompt) và là điểm hội tụ của cả ba nhánh.

Bốn bằng chứng:

1. **Prompt dài làm agent tuân thủ kém.** IFScale: model tốt nhất còn ~68% tuân thủ ở 500 chỉ dẫn, ưu tiên những dòng đầu [C-abstract, [arXiv 2507.11538](https://arxiv.org/html/2507.11538v1)]. Tài liệu Claude Code: CLAUDE.md nên dưới 200 dòng, "dài hơn thì giảm tuân thủ", hai rule mâu thuẫn thì Claude chọn tùy ý, và CLAUDE.md là "context, không phải cấu hình được thực thi" — muốn chặn thì dùng hook [C, [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)].
2. **Học từ phán đoán của chính agent làm hỏng bộ nhớ.** LLM tự chấm thiên vị output của mình [C-abstract, [Panickssery NeurIPS 2024](https://arxiv.org/pdf/2404.13076v1)]; tự sửa không có phản hồi ngoài thường làm tệ hơn [C-abstract, [Huang ICLR 2024](https://arxiv.org/abs/2310.01798)]; một nghiên cứu VLM: agent tin bộ nhớ thô "chết nhiều gấp đôi" agent không có bộ nhớ [S, [arXiv 2608.04574](https://papers.cool/arxiv/2608.04574)]. Mọi hệ có kết quả tốt (Reflexion, Voyager, SkillRevise) đều phụ thuộc vào oracle bên ngoài: unit test, môi trường, người.
3. **Chưa có ngưỡng nào của skill 3d-artist từng được chỉnh từ dữ liệu.** 16 ngưỡng gắn nhãn `[guess]` trong config, 23 nữa trong code. Trong 15 commit hôm qua: bug vào code (10 commit), quy tắc vào docs (4), config chỉ *thêm key*. Không có sổ chạy xuyên session, không đếm số lần lặp, không liên kết bài học với check thực thi nó. [C, git log repo]
4. **Studio và sản phẩm AI đều chốt cùng một mô hình:** rule = (phạm vi, thuộc tính đo, ngưỡng, mức độ, auto-fix); tín hiệu để chỉnh lại là **độ lệch giữa metric tự động và người review** (Langfuse heatmap, κ Cohen), không phải cảm tính [C, [Langfuse score analytics](https://langfuse.com/docs/evaluation/scores/score-analytics.md)].

## 2. Những gì học thuật nói (rút gọn)

| Hệ | Lưu gì | Kết quả đo được | Bài học cho mình |
|---|---|---|---|
| Reflexion (2023) | Tự phản tỉnh sau lần thất bại, theo từng task | 91% HumanEval vs ~80% [C-abs] | Chỉ có giá trị khi có oracle (test). Không chuyển task. |
| ExpeL (AAAI 2024) | Cả trajectory thô lẫn rule chắt lọc, rule có ADD/EDIT/UPVOTE/DOWNVOTE và **giới hạn số lượng** | +1–9 điểm; rule tốt cho task kiến thức, trajectory tốt cho task thao tác [C-abs] | Cần cả hai kho; phải có cap và cơ chế hạ cấp. |
| Voyager (2023) | Skill là **code** đã được môi trường xác nhận | 3,3× item, 15× nhanh hơn [C] | Bài học dạng code bền hơn dạng chữ. |
| AutoGuide (2024) | Rule có điều kiện "khi ở trạng thái X thì làm Y", chỉ nạp rule khớp trạng thái | [S] | Không đổ hết rule vào prompt; nạp theo bước. |
| Mem0 (2025) | Mỗi ký ức mới phải ADD/UPDATE/DELETE/NOOP so với ký ức cũ | +26% LOCOMO (tự báo) [C-abs] | Mâu thuẫn xử lý bằng supersession tường minh. |
| Letta/MemGPT | Khối bộ nhớ trong context **có giới hạn ký tự**, buộc agent biên tập thay vì nối thêm | 5× ít compute hơn với sleep-time [C-abs] | Cap kích thước là cơ chế chống phình. |
| SkillRevise, AFTER (2026) | Sửa SKILL.md từ execution trace, vòng COLLECT→DIAGNOSE→REVISE | 36%→62% SkillsBench [S-abs] | "Phụ thuộc phản hồi mà verifier thấy được". Trace đa dạng chuyển tốt hơn. |
| GEPA (2025) | Đột biến prompt từ phản hồi văn bản, Pareto front | Thắng GRPO 6–10%, ít rollout 35× [C-abs] | Nhưng case study: train 90→95%, **test 95→85%** [S]. Luôn giữ tập val chưa thấy. |
| Claude Managed Agents "dreaming" (5/2026) | Viết lại bộ nhớ offline từ nhiều session, có tùy chọn người duyệt trước khi áp | 1 số liệu khách hàng, không tách riêng [C] | Mô hình "đề xuất diff, người duyệt" là chuẩn ngay cả ở Anthropic. |

Hiệu chỉnh ngưỡng (thống kê cổ điển, [C]): Youden's J với bootstrap CI vì cutpoint tối ưu dao động mạnh ở n nhỏ; Platt thắng isotonic dưới ~2000 mẫu; cần ~35 mẫu dương để sensitivity ±10%; rule-of-three: 0 lỗi trong n mẫu → tỷ lệ lỗi < 3/n. Đo đồng thuận metric–người bằng **κ**, không dùng % thô (95% đồng thuận có thể κ≈0); κ ≥ 0,6 dùng được, ≥ 0,75 mới làm gate; κ tuần dao động 0,41–0,63 nên dùng cửa sổ ≥ 50 ca. Chưa có nguồn nào cho tiêu chí "nghỉ hưu" một metric; đề xuất [I]: κ < 0,4 hai cửa sổ liên tiếp thì hạ xuống `warn`.

## 3. Những gì đã có trên máy, tái dùng được

| Mảnh | Ở đâu | Tái dùng |
|---|---|---|
| Hợp đồng result JSON (`checks[{check,status,value,threshold,note}]`, `source_sha256`, `spec_sha256`, `warnings`) | `3d-artist/tools/lib/common.py`, `asset_checks/ac_common.py` | Đây là **ổ cắm** cho cơ chế học: skill nào ghi JSON dạng này là cắm được. |
| Sổ keep/revert với snapshot, hash code, `tried_fixes` có lý do | `tools/self_build/apply_edit.py` | Mẫu cho ledger; nhưng chỉ trong một asset, không ai đọc lại. |
| Định dạng bài học có độ tin cậy `candidate / recurring / strong`, "Skip when / Do not skip when / Example signal / Source", có mục inbox | `q-mode/references/bugbot-triage.md` | Kho bài học có cấp bậc duy nhất đang có; thiếu bộ đếm. |
| Bảng rule ↔ enforcer, "chứng minh check fail trên lỗi cũ" | `correct/SKILL.md` | Nguyên tắc liên kết bài học với check. |
| Sync-commit, "cố ý làm hỏng để chứng minh check vẫn bắt được" | `maintain-formal-verification-skill` | Kỷ luật kiểm chứng bài học. |
| Vòng đo → đề xuất → đo lại → chọn theo tập held-out, lịch sử bị che điểm test | `skill-creator/scripts/run_loop.py` | Hình dạng đúng của vòng tối ưu, hiện chỉ dùng cho một chuỗi mô tả. |
| Ba góc nhìn review transcript + tiêu chí synthesizer (bền, hội tụ 2+, "cơ chế cấu trúc thắng prose") | `reflect/references/*.md` | Bước chắt lọc bài học từ transcript. |
| Nhãn `[guess]`/`[src]`, `sweep.py --calibrate`, `_reason` trong spec | `3d-artist/config.yaml`, spec | Nguồn gốc ngưỡng; hiện chỉ là comment, không script nào đọc. |

## 4. Thực tế studio và sản phẩm AI

- Unreal `EditorValidatorBase` có bốn trạng thái pass / warn / fail / **không kiểm** — đáng chép nguyên [C, [docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorValidatorBase)]. Mọi add-on validator Blender hội tụ cùng danh sách check và trả PASS/WARN/FAIL kèm auto-fix [S].
- Riot (Wild Rift, GDC 2021): công cụ phân tích asset "không quy trình mới cho artist, không công nghệ mới cho engineer" — vòng học bám vào dữ liệu có sẵn [C-abstract].
- Active learning trong sản xuất: lấy mẫu % inference, lọc theo độ tin cậy thấp hoặc lớp hiếm, có cap theo ngày (Roboflow) [C]. Lấy mẫu phân tầng bắt lỗi đuôi tốt hơn ngẫu nhiên [S].
- Mô hình dữ liệu chung của MLflow / W&B / LangSmith / Langfuse / OTel GenAI: tách **run** (input hash, config version, metrics) khỏi **verdict** (key, score, source = người|rule|judge, comment, **correction**). Trường `correction` hầu hết schema có mà team hiếm khi điền [C].
- Vendor 3D: Tripo nói rating "ảnh hưởng học theo tài khoản" (chỉ là tuyên bố), Kaedim dùng người review topology/UV rồi đưa bản sửa vào lại, Meshy không có tính năng phản hồi tài liệu hóa [C/S].
- Ngưỡng SSIM thực tế được chọn thực nghiệm rồi kiểm bằng forced-choice với người (87–92% đồng thuận) [S/C]. Hausdorff chỉ giải thích ~10–15% sở thích người xem giữa các decimator: "metric đẹp mà mắt thấy xấu" [S]. Kết luận cho mình: IoU/Hausdorff là gate lỗi thô, không phải thước đo thẩm mỹ.

## 5. Anti-pattern đã có bằng chứng

1. Rule tích lũy tới mức prompt không đọc nổi (IFScale, Lost-in-the-Middle, cap 200 dòng của Claude).
2. Bài học một lần được ghi như quy luật (ExpeL cap rule; AFTER: trace hẹp chuyển kém).
3. Vòng tự duyệt (Panickssery, Huang).
4. Học từ phán đoán chưa kiểm chứng (AWM online, STALE, MemFail).
5. Rule mâu thuẫn (Claude chọn tùy ý; Mem0 và Letta là hai cách trả lời).
6. Viết lại prompt bị overfit (OPRO lệch train/test 5–20%; GEPA 20/10 split).

---

## 6. Thiết kế đề xuất: `art-learn`

Một cơ chế dùng chung cho mọi skill art, cắm qua hợp đồng result JSON. 3d-artist là skill đầu tiên dùng. Tên tạm `art-learn` (skill + thư viện nhỏ).

### 6.1 Nguyên tắc

1. **Dữ liệu trước, code sau, prose cuối.** Bài học là một dòng; lặp ≥ 2 lần có người xác nhận thì thành check / ngưỡng / fixture; chỉ vào SKILL.md khi không đo được, và SKILL.md có cap 200 dòng.
2. **Chỉ học từ verdict đã kiểm chứng:** người, hoặc check tất định. Không bao giờ từ pass/fail do agent tự chấm.
3. **Tự động chỉ làm việc đảo ngược được;** mọi thay đổi ngưỡng, check, prose là *đề xuất diff* chờ người gõ "yes".
4. **Mỗi bài học trỏ tới cái thực thi nó;** `doctor` fail khi enforcer biến mất.
5. **Ghi bài học < 30 giây:** một lệnh, một câu hỏi.

### 6.2 Dữ liệu (JSONL, append-only, trong `~/.claude/art-learn/<skill>/`, có thể commit vào repo)

**runs.jsonl** — một dòng mỗi lần chạy, tự ghi từ result JSON:
```
run_id, skill, skill_version (git hash), asset, asset_class, inputs_sha, config_sha,
checks[{id, status, value, threshold, source}], metrics, warnings, evidence_path, started, seconds
```
**verdicts.jsonl** — một dòng mỗi phán quyết:
```
run_id, check_id, auto (pass|warn|fail|not_checked), human (pass|fail|skip), who, correction (≤140 ký tự), seconds
```
Dẫn xuất, không lưu: `disagreement = auto != human`, số lần fire, lần cuối fire.

**lessons.jsonl** — bài học:
```
id, skill, trigger (check_id hoặc tình huống), observation, correction, evidence [run_ids],
count, status (candidate → recurring → encoded → prose), enforced_by (check_id | config key | fixture path | SKILL.md anchor),
supersedes (id cũ), created, last_seen, expiry
```

**golden/<check_id>/** — fixture phản ví dụ: asset thật bị check bắt sai (false positive) hoặc bỏ sót (false negative). Mọi đề xuất đổi ngưỡng phải replay qua đây.

### 6.3 Ba lệnh người dùng

| Khi nào | Lệnh | Làm gì |
|---|---|---|
| Sau một lần chạy | `art-learn judge <asset dir>` | Liệt kê verdict tự động, mỗi dòng một; hỏi **một câu**: "Dòng nào sai? (số, hoặc Enter nếu không)". Mỗi số mở ô correction ≤ 140 ký tự. Enter không gõ gì vẫn ghi `human: pass` cho mọi check — đó là thứ làm được biểu đồ acceptance rate. |
| Khi check bắt sai | `art-learn flag <check_id> --run <id>` | Đánh dấu false positive/negative, chụp asset vào `golden/<check_id>/`, tăng bộ đếm disagreement. |
| Hàng tuần | `art-learn review` | In: acceptance rate theo check và asset_class so 4 tuần trước; bảng 2×2 metric–người cho check có lệch > 15%; κ với cửa sổ ≥ 50; check không fire 60 ngày (ứng viên bỏ); correction chia sẻ n-gram ≥ 3 dòng (ứng viên gộp thành một rule); đề xuất cutpoint Youden + bootstrap CI khi ≥ 35/35 mẫu mỗi phía. **Kết quả là một diff đề xuất** cho `config.yaml` (đổi nhãn `[guess]` → `[data: n=…, date]`) và cho SKILL.md, không tự áp. |

Thêm hai lệnh nội bộ: `art-learn ingest <asset dir>` (tự gọi cuối mỗi run bởi `report.py`), `art-learn doctor` (kiểm mọi `enforced_by` còn tồn tại, replay `golden/`, kiểm SKILL.md dưới 200 dòng).

### 6.4 Tự động vs đề xuất

| Tự động | Chỉ đề xuất, cần "yes" |
|---|---|
| Ghi dòng run/verdict; đếm fire, disagreement, acceptance | Mọi thay đổi ngưỡng (cần ≥ 35/35 mẫu trong asset_class đó và replay golden không tăng lệch) |
| Hạ check từ `fail` → `warn` sau 3 false positive liên tiếp được người xác nhận (rule-of-three, đảo ngược được, ghi lý do) | Thăng một correction lặp lại thành check code mới (qua review) |
| Đánh dấu `stale` check 60 ngày không fire | Xóa check, sửa prose SKILL.md, tách ngưỡng theo asset_class |
| Chụp golden phản ví dụ | Thay đổi rubric của critic |

### 6.5 Vòng đời một bài học (ví dụ từ hôm qua)

1. Run rock-moss: `param_fit` hạ chiều cao RockL 11% dù brief ghi 1,6 m. Em ghi `judge`: check `fit.height_respected` = fail, correction "brief fixes height; fit must not touch".
2. Lần 2 xảy ra ở asset khác → `count=2`, status `recurring`. `review` đề xuất: thêm `fixed_params` vào param_fit (code) + fixture golden là graph rock-moss.
3. Người gõ yes → bài học thành `encoded`, `enforced_by: tools/self_build/param_fit.py:fixed_params`, fixture replay pass. Dòng prose về nó trong `self_build.md` giữ 1 câu trỏ tới cơ chế, không mô tả lại.
4. `doctor` mỗi tuần: nếu ai xóa `fixed_params`, doctor fail và nêu bài học bị mất enforcer.

### 6.6 Dùng chung cho skill art khác

Điều kiện duy nhất: skill ghi result JSON theo hợp đồng `common.write_result` (có `checks[]`, `source_sha256`, `spec_sha256`). 2D artist, concept artist, UI artist chỉ cần (a) đặt check id ổn định, (b) gọi `art-learn ingest` cuối run, (c) có `config.yaml` với nhãn `[guess]`/`[data]`. Phần `judge`/`review`/`doctor` không cần biết skill làm gì.

Với skill không có số đo (ví dụ 2D hand-paint), verdict chỉ có `human` và bài học đi thẳng tới `recurring → prose` với cap dòng; `review` vẫn gộp correction lặp và báo check nào đáng viết thành script.

### 6.7 Cái gì em tin, cái gì là đoán

- Tin (có bằng chứng mạnh): ledger + fixture hồi quy; bài học thành validator thay vì prose; chỉ học từ verdict kiểm chứng; κ thay vì % đồng thuận; mọi thay đổi là diff đề xuất.
- Hợp lý nhưng chưa có nguồn: ngưỡng 15% lệch 2×2, 60 ngày stale, κ 0,4 để hạ cấp, 35/35 mẫu. Em ghi chúng là `[guess]` trong config của chính art-learn, để `review` sau này tự chỉnh.
- Chưa làm ở bước đầu: GEPA-style tự viết lại SKILL.md từ trace (cần tập val ≥ 30 asset thật mới an toàn; làm sau khi ledger có dữ liệu).

### 6.8 Khối lượng

Khoảng 1–2 ngày: thư viện ledger (ingest/judge/flag/review/doctor, ~5 script Python thuần, không Blender), skill `art-learn/SKILL.md` ngắn, hook vào `report.py` của 3d-artist, chuyển các `[guess]` sang định dạng máy đọc được, 3 fixture golden từ các lỗi hôm qua, và test bằng chính dữ liệu đã có (12 run hôm qua).

Rủi ro chính: nếu anh không chạy `judge` sau mỗi run, ledger chỉ có verdict tự động và không học được gì ngoài acceptance rate. Vì vậy `judge` phải thật sự dưới 30 giây, và `report.py` nhắc đúng một dòng ở cuối.

---

## Nguồn chính

Học thuật: [Reflexion](https://arxiv.org/pdf/2303.11366) · [ExpeL](https://arxiv.org/html/2308.10144v3) · [Voyager](https://github.com/minedojo/voyager) · [AWM](https://arxiv.org/abs/2409.07429v1) · [AutoGuide](https://arxiv.org/abs/2403.08978v1) · [Mem0](https://arxiv.org/abs/2504.19413) · [Letta sleep-time](https://arxiv.org/html/2504.13171v1) · [Dynamic Cheatsheet](https://arxiv.org/abs/2504.07952v1) · [SkillRevise](https://huggingface.co/papers/2606.01139) · [AFTER](https://huggingface.co/papers/2606.23127) · [GEPA](https://arxiv.org/abs/2507.19457v2) · [OPRO](https://arxiv.org/pdf/2309.03409) · [IFScale](https://arxiv.org/html/2507.11538v1) · [STALE](https://arxiv.org/abs/2605.06527) · [Self-preference bias](https://arxiv.org/pdf/2404.13076v1) · [Self-correction limits](https://arxiv.org/abs/2310.01798) · [cutpointr/Youden](https://arxiv.org/pdf/2002.09209) · [Platt vs isotonic](https://arxiv.org/pdf/1207.1403) · [κ vs agreement](https://arxiv.org/html/2606.00093v1)

Thực hành: [Claude Code memory](https://code.claude.com/docs/en/memory) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Managed Agents dreaming](https://claude.com/blog/new-in-claude-managed-agents) · [Managed Agents outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes.md) · [SRE postmortem](https://sre.google/sre-book/postmortem-culture/) · [Unreal EditorValidatorBase](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorValidatorBase) · [Langfuse scores](https://langfuse.com/docs/evaluation/scores/data-model.md) · [LangSmith feedback](https://docs.langchain.com/langsmith/feedback-data-format.md) · [MLflow run](https://docs.databricks.com/api/experiments/v1/run/object.md) · [Roboflow active learning](https://docs.roboflow.com/deploy/active-learning) · [Riot GDC 2021](https://gdcvault.com/play/1027061/Technical-Artist-Summit-The-Art) · [Hausdorff vs preference](https://80.lv/articles/testing-4-free-mesh-simplification-tools)

Trên máy: `/root/.claude/skills/{reflect,correct,automate-me,show-me-your-work,q-mode/references/bugbot-triage.md}`, `skill-creator/scripts/run_loop.py`, `3d-artist/tools/lib/common.py`, `tools/self_build/apply_edit.py`.
