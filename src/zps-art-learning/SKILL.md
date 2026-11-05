---
name: zps-art-learning
description: "Record tool results and real reviewer feedback in a project ledger, and propose improvements from repeated issues. Use only when asked to capture lessons (\"ghi bài học\", \"lưu feedback\")."
metadata:
  version: 0.5.6
  validation: pending
---

# ZPS - Art Learning

**Not for:** automatic self-training or routine asset approval.

Keep learning as project data first. Use the [ledger CLI](references/ledger.md) when the user requests learning capture or the project explicitly enables it. No background tasks, global memory, automatic skill edits or implicit approval are installed.

Record measured results separately from reviewer verdicts. A saved report and hash establish identity/integrity, not that its claims are correct. Human feedback must come from an actual human response; deterministic verdicts must come from a known executed check. Never relabel agent self-review as human or deterministic. Silence, an empty reply and missing checks are not pass.

Record candidate lessons with the artifact/version, trigger, correction and supporting run/verdict. Repeated copies or retries of the same asset are not independent confirmation. Supersede old verdicts explicitly and preserve history. Only retrieve lessons relevant to the current task; do not load a whole ledger into prompts.

Use review output to propose a scoped change to a check, fixture, config or instruction. Require adequate examples, a regression test reproducing the issue and held-out cases appropriate to the change before claiming general improvement. Keep stylistic preferences scoped to the project. Existing authorization can cover implementation, but collecting a lesson alone never authorizes changing installed skills or lowering thresholds.

The CLI records and reviews evidence; it does not train, calibrate or change anything by itself. Commands and limits: [ledger CLI](references/ledger.md).
