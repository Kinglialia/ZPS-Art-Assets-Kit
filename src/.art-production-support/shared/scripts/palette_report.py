"""Report the dominant colors of an image and, when a palette is given, how far each is from the
nearest palette color (CIE76 delta E in Lab). Diagnostic: palette match is not style approval."""
import argparse
import json
import math
from pathlib import Path
import sys

# CIE76 dE ~2.3 is the classic just-noticeable difference; 10 is clearly visible side by side.
# Default threshold 10 flags colors an observer would call "a different color", not subtle shifts.
DEFAULT_MAX_DELTA = 10.0
# Pixels with alpha below this are background/antialias fringe, not part of the painted asset.
ALPHA_MIN = 128


def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    if len(h) != 6:
        raise ValueError(f'invalid hex color {h!r}')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_lab(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b):
    return math.dist(rgb_to_lab(a), rgb_to_lab(b))


def load_palette(values):
    colors = []
    for v in values:
        p = Path(v)
        if p.suffix == '.json' and p.is_file():
            data = json.loads(p.read_text())
            items = data.get('colors', data) if isinstance(data, dict) else data
            colors += [i['hex'] if isinstance(i, dict) else i for i in items]
        else:
            colors.append(v)
    return [hex_to_rgb(c) for c in colors]


def report(path, n_colors=8, palette=None, max_delta=DEFAULT_MAX_DELTA):
    from PIL import Image
    with Image.open(path) as im:
        rgba = im.convert('RGBA')
    data = rgba.get_flattened_data() if hasattr(rgba, 'get_flattened_data') else rgba.getdata()
    pixels = [p[:3] for p in data if p[3] >= ALPHA_MIN]
    if not pixels:
        raise ValueError('no opaque pixels to analyse')
    strip = Image.new('RGB', (len(pixels), 1))
    strip.putdata(pixels)
    quant = strip.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)
    pal = quant.getpalette()
    counts = sorted(quant.getcolors(), reverse=True)
    dominant = []
    for count, idx in counts:
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        entry = {'hex': '#%02x%02x%02x' % rgb, 'share': round(count / len(pixels), 4)}
        if palette:
            nearest = min(palette, key=lambda c: delta_e(rgb, c))
            d = delta_e(rgb, nearest)
            entry.update(nearest='#%02x%02x%02x' % nearest, delta_e=round(d, 2),
                         status='pass' if d <= max_delta else 'off_palette')
        dominant.append(entry)
    result = {'tool': 'art_palette_report', 'image': str(Path(path).resolve()), 'opaque_pixels': len(pixels),
              'dominant': dominant,
              'scope': 'Median-cut clusters of opaque pixels; antialias and lighting create in-between colors that may be valid.'}
    if palette:
        off = sum(e['share'] for e in dominant if e['status'] == 'off_palette')
        result.update(max_delta_e=max_delta, off_palette_share=round(off, 4))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--colors', type=int, default=8)
    p.add_argument('--palette', nargs='+', help='#RRGGBB values or a JSON file with a colors list')
    p.add_argument('--max-delta', type=float, default=DEFAULT_MAX_DELTA)
    p.add_argument('--fail-share', type=float, help='exit 1 when off-palette share exceeds this fraction')
    a = p.parse_args()
    try:
        r = report(a.image, a.colors, load_palette(a.palette) if a.palette else None, a.max_delta)
        print(json.dumps(r, indent=2))
        if a.fail_share is not None and r.get('off_palette_share', 0) > a.fail_share:
            return 1
        return 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
