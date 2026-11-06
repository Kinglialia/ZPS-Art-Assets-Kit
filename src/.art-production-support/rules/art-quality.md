# Quality standard — do not deliver "random AI output"

Apply this to every image that the role creates or edits before delivery, including test samples. The level of record-keeping follows the scale of the change. A beautiful image that has details without a reason is still a defect. Before you call a generate/edit tool, read [gen craft](../shared/gen-craft.md).

## 1. Detail budget and element inventory

Before you create the image, set a detail budget. Base it on the function, the display size, and the visual focus of the asset. Compare it with the style sheet and the Execution reference at the same size. If there is no other reason, keep the detail level close to the reference. Increase detail only when the function or focus needs it, and record the reason.

After each output, **check for added elements**. Every visible object, accessory, motif, effect, text, and light source must trace back to the brief, the style sheet, the function/construction, or an agreed story. If it cannot be traced, remove it or fix it. Write the full inventory table, as in the example below, when you create a new asset, make a set, or deliver a final version. For a small edit, record only the elements you added, removed, or changed.

```text
Inventory — sword_icon_v3
- Blade, hilt, guard: brief "novice iron sword" ✓
- Red gem on the hilt: not in the brief → remove
- Sparkle at the top corner: style sheet does not use sparkle → remove
```

## 2. Revision round

1. Create/edit. 2. Preview at the target size and compare with a reference of the same deliverable type. 3. Open the image and check: the inventory, the generated-image fault table in gen craft, and the [6-dimension self-check](../templates/review.md). 4. Choose the fix method from the [fix playbook](../shared/fix-playbook.md). Use the cheapest method that has evidence. If the structure is acceptable, try a script or a local edit before you regenerate. 5. Record the round in the task record.

If you have many hypotheses and budget remains, you can test several options. In each branch, change one factor. Score all branches at the same time. Choose by eye first. Use measurements to eliminate options and to break ties.

## 3. Budget

Use the budget and limits that were assigned. Do not extend the budget on your own when you change branch or because one round made progress. If there is no limit yet, do only the part that was requested. Do not run a loop of many variants on your own. If needed, propose a small test step.
Stop regardless of budget when two rounds in a row show no progress on the same defect. Diagnose it and report to the user with options. Do not deliver the "least bad" version as if it passed.

## 4. Honest report

Deliver these with the image: the element inventory (full or changed parts, per section 1), the fixed defects, the remaining defects, and the previews you opened. A passing self-check is only `self-check`. Art approval belongs to the AD/user. Do not call an image "on style", "game-ready", or "finished" before you compare it with the reference at the same size.
