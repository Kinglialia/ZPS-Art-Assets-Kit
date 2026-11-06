"""Build inspection images an agent or artist must open: size/background sheet, tile repeat,
value study and side-by-side comparison with references. Produces evidence to look at; it does
not score art. Requires Pillow and numpy. Downscales in linear light with premultiplied alpha.
Refuses to overwrite --out."""
import argparse
import json
from pathlib import Path
import sys

BACKGROUNDS = {'light': (238, 238, 238), 'dark': (34, 34, 38), 'mid': (128, 128, 128)}
LABEL_H = 18  # enough for Pillow's default bitmap font plus padding
GAP = 8


def _image():
    from PIL import Image, ImageDraw, ImageFont
    return Image, ImageDraw, ImageFont


def parse_color(value):
    if value in BACKGROUNDS:
        return BACKGROUNDS[value]
    v = value.lstrip('#')
    if len(v) != 6:
        raise ValueError(f'background must be light/dark/mid or #RRGGBB, got {value!r}')
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def load(path):
    Image, _, _ = _image()
    with Image.open(path) as im:
        im.load()
        return im.convert('RGBA')


def resize_linear(im, size):
    """Resize in linear light with premultiplied alpha, the way a GPU filters a texture.
    A resize of gamma-encoded values darkens thin bright strokes; straight alpha lets the color
    of transparent pixels bleed into the edges (dark halo). Both make a small preview wrong."""
    import numpy as np
    Image, _, _ = _image()
    src = np.asarray(im.convert('RGBA'), dtype=np.float32) / 255
    rgb, a = src[..., :3], src[..., 3:]
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4) * a
    chans = [Image.fromarray(c, 'F').resize(size, Image.LANCZOS)
             for c in (lin[..., 0], lin[..., 1], lin[..., 2], a[..., 0])]
    lin2 = np.stack([np.asarray(c) for c in chans[:3]], -1)
    a2 = np.clip(np.asarray(chans[3]), 0, 1)[..., None]
    lin2 = np.clip(np.divide(lin2, a2, out=np.zeros_like(lin2), where=a2 > 1e-6), 0, 1)
    enc = np.where(lin2 <= 0.0031308, lin2 * 12.92, 1.055 * lin2 ** (1 / 2.4) - 0.055)
    out = np.concatenate([enc, a2], -1)
    return Image.fromarray(np.round(out * 255).astype(np.uint8), 'RGBA')


def fit(im, box, nearest=False):
    """Scale so the longer side equals box (the on-screen display size), keeping aspect."""
    Image, _, _ = _image()
    w, h = im.size
    s = box / max(w, h)
    size = (max(1, round(w * s)), max(1, round(h * s)))
    return im.resize(size, Image.NEAREST) if nearest else resize_linear(im, size)


def label(canvas, xy, text):
    _, ImageDraw, ImageFont = _image()
    draw = ImageDraw.Draw(canvas)
    draw.text(xy, text, fill=(255, 0, 255), font=ImageFont.load_default())


def sheet(image, sizes, backgrounds, nearest=False):
    """Rows = backgrounds, columns = display sizes. Shows the asset as the player sees it."""
    Image, _, _ = _image()
    src = load(image)
    cell = max(sizes) + GAP
    canvas = Image.new('RGB', (cell * len(sizes) + GAP, (cell + LABEL_H) * len(backgrounds) + GAP), (255, 255, 255))
    for r, bg in enumerate(backgrounds):
        color = parse_color(bg)
        for c, size in enumerate(sizes):
            x, y = GAP + c * cell, GAP + r * (cell + LABEL_H)
            tile = Image.new('RGB', (cell - GAP, cell - GAP), color)
            scaled = fit(src, size, nearest)
            tile.paste(scaled, ((tile.width - scaled.width) // 2, (tile.height - scaled.height) // 2), scaled)
            canvas.paste(tile, (x, y + LABEL_H))
            label(canvas, (x, y + 2), f'{size}px {bg}')
    return canvas


def tile(image, repeat=3):
    """Repeat a tile NxN to expose seams and repeating landmarks."""
    Image, _, _ = _image()
    src = load(image)
    canvas = Image.new('RGBA', (src.width * repeat, src.height * repeat))
    for y in range(repeat):
        for x in range(repeat):
            canvas.paste(src, (x * src.width, y * src.height))
    return canvas


def value(image, small=64):
    """Grayscale at working size and at a small display size: checks value hierarchy and silhouette."""
    Image, _, _ = _image()
    src = load(image)
    flat = Image.new('RGBA', src.size, BACKGROUNDS['mid'] + (255,))
    flat.alpha_composite(src)
    gray = flat.convert('L').convert('RGB')
    tiny = fit(gray, small)
    canvas = Image.new('RGB', (gray.width + tiny.width + GAP * 3, max(gray.height, tiny.height) + GAP * 2 + LABEL_H), (255, 255, 255))
    canvas.paste(gray, (GAP, GAP + LABEL_H))
    canvas.paste(tiny, (gray.width + GAP * 2, GAP + LABEL_H))
    label(canvas, (GAP, 2), 'value (on mid gray)')
    label(canvas, (gray.width + GAP * 2, 2), f'{small}px')
    return canvas


def compare(candidate, references, height=256, small=None, background='mid'):
    """Candidate first, then references, all at the same height; optional second row at small size."""
    Image, _, _ = _image()
    items = [('candidate', load(candidate))] + [(Path(r).stem, load(r)) for r in references]
    rows = [height] + ([small] if small else [])
    color = parse_color(background)
    scaled_rows = []
    for h in rows:
        scaled_rows.append([(name, resize_linear(im, (max(1, round(im.width * h / im.height)), h))) for name, im in items])
    width = max(sum(im.width + GAP for _, im in row) + GAP for row in scaled_rows)
    total_h = sum(h + LABEL_H + GAP for h in rows) + GAP
    canvas = Image.new('RGB', (width, total_h), color)
    y = GAP
    for h, row in zip(rows, scaled_rows):
        x = GAP
        for name, im in row:
            canvas.paste(im, (x, y + LABEL_H), im)
            label(canvas, (x, y + 2), name[:24])
            x += im.width + GAP
        y += h + LABEL_H + GAP
    return canvas


def save(canvas, out):
    with Path(out).open('xb') as f:
        canvas.save(f, format='PNG')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sheet'); s.add_argument('image', type=Path)
    s.add_argument('--sizes', nargs='+', type=int, default=[64, 128, 256])
    s.add_argument('--backgrounds', nargs='+', default=['light', 'dark'])
    s.add_argument('--nearest', action='store_true', help='pixel art: no smoothing')
    t = sub.add_parser('tile'); t.add_argument('image', type=Path); t.add_argument('--repeat', type=int, default=3)
    v = sub.add_parser('value'); v.add_argument('image', type=Path); v.add_argument('--small', type=int, default=64)
    c = sub.add_parser('compare'); c.add_argument('candidate', type=Path); c.add_argument('references', nargs='+', type=Path)
    c.add_argument('--height', type=int, default=256); c.add_argument('--small', type=int)
    c.add_argument('--background', default='mid')
    for q in (s, t, v, c):
        q.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    try:
        if a.cmd == 'sheet':
            canvas = sheet(a.image, a.sizes, a.backgrounds, a.nearest)
        elif a.cmd == 'tile':
            canvas = tile(a.image, a.repeat)
        elif a.cmd == 'value':
            canvas = value(a.image, a.small)
        else:
            canvas = compare(a.candidate, a.references, a.height, a.small, a.background)
        save(canvas, a.out)
        print(json.dumps({'tool': 'art_preview', 'command': a.cmd, 'out': str(a.out.resolve()), 'size': list(canvas.size),
                          'next': 'Open this image and inspect it; the file itself is not a quality verdict.'}))
        return 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Pillow required; --out must not exist.'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
