"""Build inspection images for a frame sequence: a filmstrip and an onion skin for an agent to open,
and a GIF for a person to play. An agent sees still images only, so the GIF is for human review.
Produces evidence to look at; it does not score motion. Requires Pillow. Refuses to overwrite."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preview import BACKGROUNDS, GAP, LABEL_H, label, parse_color  # noqa: E402
from sprite_check import frames_from  # noqa: E402


def _image():
    from PIL import Image
    return Image


def scale(im, height, nearest):
    Image = _image()
    w = max(1, round(im.width * height / im.height))
    return im.resize((w, height), Image.NEAREST if nearest else Image.LANCZOS)


def strip(frames, height, background, nearest):
    """All frames in order, same display height, numbered from 1."""
    Image = _image()
    scaled = [scale(im, height, nearest) for _, im in frames]
    width = sum(im.width + GAP for im in scaled) + GAP
    canvas = Image.new('RGB', (width, height + LABEL_H + GAP * 2), parse_color(background))
    x = GAP
    for i, im in enumerate(scaled, 1):
        canvas.paste(im, (x, GAP + LABEL_H), im)
        label(canvas, (x, GAP), str(i))
        x += im.width + GAP
    return canvas


def onion(frames, height, background, nearest, tint):
    """Frames stacked on one canvas. Early frames are faint, the last frame is opaque, so the
    order and the path of motion stay readable. With tint, early frames lean blue, late frames red."""
    Image = _image()
    sizes = {im.size for _, im in frames}
    if len(sizes) != 1:
        raise ValueError(f'frames differ in canvas size {sorted(sizes)}; run sprite_check.py first')
    n = len(frames)
    base = Image.new('RGBA', frames[0][1].size, parse_color(background) + (255,))
    for i, (_, im) in enumerate(frames):
        t = i / (n - 1) if n > 1 else 1.0
        layer = im.copy()
        if tint:
            color = Image.new('RGBA', im.size, (round(255 * t), 60, round(255 * (1 - t)), 255))
            layer = Image.blend(layer, color, 0.35)
            layer.putalpha(im.getchannel('A'))
        alpha = layer.getchannel('A').point(lambda v, k=0.25 + 0.75 * t: round(v * k))
        layer.putalpha(alpha)
        base.alpha_composite(layer)
    return scale(base, height, nearest).convert('RGB')


def gif(frames, height, background, nearest, fps):
    """Frames composited on the background at the given fps, looping. GIF has no smooth alpha."""
    Image = _image()
    bg = parse_color(background) + (255,)
    out = []
    for _, im in frames:
        flat = Image.new('RGBA', im.size, bg)
        flat.alpha_composite(im)
        out.append(scale(flat, height, nearest).convert('RGB'))
    return out, round(1000 / fps)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs', nargs='+', type=Path, help='frame files in order, or one sheet with --grid')
    p.add_argument('--grid', nargs=2, type=int, metavar=('COLS', 'ROWS'))
    p.add_argument('--out', type=Path, required=True, help='prefix: writes <out>_strip.png, <out>_onion.png, <out>.gif')
    p.add_argument('--height', type=int, default=128, help='display height in px (use the in-game size)')
    p.add_argument('--fps', type=float, default=12)
    p.add_argument('--step', type=int, default=1, help='onion skin: use every Nth frame for long cycles')
    p.add_argument('--background', default='mid', help=f"{'/'.join(BACKGROUNDS)} or #RRGGBB")
    p.add_argument('--nearest', action='store_true', help='pixel art: no smoothing')
    p.add_argument('--no-tint', action='store_true')
    a = p.parse_args()
    paths = {k: Path(f'{a.out}{s}') for k, s in (('strip', '_strip.png'), ('onion', '_onion.png'), ('gif', '.gif'))}
    try:
        if a.fps <= 0 or a.step < 1 or a.height < 1:
            raise ValueError('--fps, --step and --height must be positive')
        existing = [str(v) for v in paths.values() if v.exists()]
        if existing:
            raise OSError(f'output exists: {existing}')
        frames = frames_from(a.inputs, a.grid)
        if not frames:
            raise ValueError('no frames')
        s = strip(frames, a.height, a.background, a.nearest)
        o = onion(frames[::a.step], a.height, a.background, a.nearest, not a.no_tint)
        g, ms = gif(frames, a.height, a.background, a.nearest, a.fps)
        with paths['strip'].open('xb') as f:
            s.save(f, format='PNG')
        with paths['onion'].open('xb') as f:
            o.save(f, format='PNG')
        with paths['gif'].open('xb') as f:
            g[0].save(f, format='GIF', save_all=True, append_images=g[1:], duration=ms, loop=0)
        print(json.dumps({'tool': 'art_anim_preview', 'frames': len(frames), 'fps': a.fps, 'frame_ms': ms,
                          'out': {k: str(v.resolve()) for k, v in paths.items()},
                          'next': 'Open the strip and the onion skin. The GIF is for a person to play; '
                                  'record timing and feel as not_checked unless a person reviewed it.'}))
        return 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Pillow required; outputs must not exist; frames need one canvas size.'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
