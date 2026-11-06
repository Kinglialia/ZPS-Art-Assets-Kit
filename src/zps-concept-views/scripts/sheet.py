"""Make a 3x2 sheet from 6 view images, or split a generated 3x2 sheet back into 6 views.

  python3 <SKILL>/scripts/sheet.py make  --dir <abs>/views_blockout --suffix _guide --out <abs>/guide_sheet.png
  python3 <SKILL>/scripts/sheet.py split --sheet <abs>/gen_sheet.png --out <abs>/views_gen

Layout (row by row): front, back, left / right, top, bottom.
Labels are NOT drawn on the sheet so the image AI does not copy them into its picture.
"""
import argparse
import os

from PIL import Image

ORDER = ["front", "back", "left", "right", "top", "bottom"]


def make(args):
    ims = [Image.open(os.path.join(args.dir, f"{v}{args.suffix}.png")).convert("RGBA") for v in ORDER]
    w, h = ims[0].size
    gap = args.gap
    sheet = Image.new("RGB", (3 * w + 4 * gap, 2 * h + 3 * gap), args.bg)
    for i, im in enumerate(ims):
        x = gap + (i % 3) * (w + gap)
        y = gap + (i // 3) * (h + gap)
        sheet.paste(im, (x, y), im)
    sheet.save(args.out)
    print(f"Sheet {sheet.size} -> {args.out}")


def split(args):
    sheet = Image.open(args.sheet).convert("RGB")
    W, H = sheet.size
    os.makedirs(args.out, exist_ok=True)
    cw, ch = W / 3, H / 2
    for i, v in enumerate(ORDER):
        x, y = (i % 3) * cw, (i // 3) * ch
        sheet.crop((round(x), round(y), round(x + cw), round(y + ch))).save(os.path.join(args.out, f"{v}.png"))
    print(f"Split into 6 views -> {args.out} (cells {cw:.0f}x{ch:.0f}px)")


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
m = sub.add_parser("make")
m.add_argument("--dir", required=True)
m.add_argument("--suffix", default="_guide")
m.add_argument("--out", required=True)
m.add_argument("--gap", type=int, default=32)
m.add_argument("--bg", default="#FFFFFF")
s = sub.add_parser("split")
s.add_argument("--sheet", required=True)
s.add_argument("--out", required=True)
a = p.parse_args()
make(a) if a.cmd == "make" else split(a)
