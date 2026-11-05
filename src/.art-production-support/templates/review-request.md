# Review request — hand a review to another person/agent/session

Send all the fields. The reviewer scores against the **attached criteria**, not from memory or an old version.

```markdown
# Review <asset> <version> — read-only, no generating, no file edits

- Image: <path on the reviewer's machine> (+ source image if it is an edit)
- Style sheet/Bible: <version> — paste the applicable lines, including the standard measurements (darkest 5% color, cast, value, palette)
- Reference of the same deliverable type: <path>
- Scoring criteria (pass/partial/fail + 1 sentence of evidence): <id: measurable criterion>
- Measurements: score_variants / palette / value / structure_diff (if it is an edit) — record the commands
- Element inventory: allowed list = <…>
- Return: table of measurements, scoring table, inventory, generated-image faults. Do not send images through base64.
```

The reviewer must open the image themselves. For a criterion without standard measurements, score `insufficient_evidence`. Do not guess.
