# UI accessibility by task

Set the goal and the check method for the task. Do not claim a general standard from a checklist.

- Touch area after scaling, spacing between actions that are easy to confuse, repeated actions, occlusion by the hand.
- Enlarged text/UI within the supported range, so that content and actions stay usable.
- Contrast on the real background (gameplay background, image, motion), not only on a flat background.
- Important states have a signal other than color: label, shape, pattern.
- Do not signal an important result by sound only.
- Non-essential motion has a reduce/off option when it is in the requirements. Avoid flashing that causes discomfort.
- A button with only an icon needs a clear meaning. Record the label, focus order and semantics when assistive technology is required.

Use W3C to understand the problem ([color](https://github.com/w3c/wcag/blob/main/understanding/20/use-of-color.html), [contrast](https://github.com/w3c/wcag/blob/main/understanding/20/contrast-minimum.html), [touch area](https://github.com/w3c/wcag/blob/main/understanding/22/target-size-minimum.html), [motion](https://github.com/w3c/wcag/blob/main/understanding/21/animation-from-interactions.html)). These are web criteria. Do not assign a CSS pixel directly to a Godot unit. They do not certify a native game. Record the unit and the source of the project target. Check screen reader/focus against the actual Godot version, operating system and device.
