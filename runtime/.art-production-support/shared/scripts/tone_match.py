"""Shift the color cast of an image toward reference images, separately for shadows, midtones
and highlights, without changing lightness or shapes. Use when structure is right but colors
drift (e.g. brown shadows where the style has cool gray ones). Deterministic: no generation.

Method: convert to CIE Lab (Pillow ImageCms), split pixels into three soft lightness bands,
measure the mean a*/b* (color cast) of each band in the image and in the references, and move
each pixel's a*/b* by the band difference times --strength. L* is untouched, so values,
silhouettes and detail stay identical. Transparent pixels (alpha < 128) are ignored in every
measurement and the alpha channel is copied unchanged to the output, so icons and sprites keep
their transparency. Requires Pillow and numpy. Refuses to overwrite --out."""
import argparse
import json
from pathlib import Path
import sys

# Band centers in L* (0-100). Soft triangular weights between them avoid visible seams.
BANDS = (('shadows', 20.0), ('midtones', 50.0), ('highlights', 80.0))
# Same opacity cut as palette_report: antialiased fringe and empty canvas are not the asset.
ALPHA_MIN = 128


def load(path):
    """Return (L, a, b, alpha) where alpha is a uint8 array or None for opaque formats."""
    import numpy as np
    from PIL import Image
    with Image.open(path) as im:
        has_alpha = 'A' in im.getbands() or 'transparency' in im.info
        rgba = im.convert('RGBA')
    alpha = np.asarray(rgba.getchannel('A')) if has_alpha else None
    L, a, b = _lab(rgba.convert('RGB'))
    return L, a, b, alpha


def mask_of(alpha):
    return None if alpha is None else alpha >= ALPHA_MIN


def to_lab(path):
    L, a, b, _ = load(path)
    return L, a, b


def _lab(rgb):
    import numpy as np
    from PIL import ImageCms
    lab = ImageCms.applyTransform(rgb, ImageCms.buildTransform(
        ImageCms.createProfile('sRGB'), ImageCms.createProfile('LAB'), 'RGB', 'LAB'))
    arr = np.asarray(lab)
    L = arr[..., 0].astype(np.float32) * 100.0 / 255.0
    # Pillow stores a*/b* as signed 8-bit values in unsigned bytes (two's complement).
    a = arr[..., 1].view(np.int8).astype(np.float32)
    b = arr[..., 2].view(np.int8).astype(np.float32)
    return L, a, b


def from_lab(L, a, b):
    import numpy as np
    from PIL import Image, ImageCms
    l8 = np.clip(L * 255.0 / 100.0, 0, 255).round().astype(np.uint8)
    a8 = np.clip(a, -128, 127).round().astype(np.int8).view(np.uint8)
    b8 = np.clip(b, -128, 127).round().astype(np.int8).view(np.uint8)
    arr = np.stack([l8, a8, b8], axis=-1)
    lab = Image.fromarray(arr, 'LAB')
    return ImageCms.applyTransform(lab, ImageCms.buildTransform(
        ImageCms.createProfile('LAB'), ImageCms.createProfile('sRGB'), 'LAB', 'RGB'))


def weights(L):
    import numpy as np
    centers = [c for _, c in BANDS]
    w = []
    for i, c in enumerate(centers):
        left = centers[i - 1] if i else None
        right = centers[i + 1] if i + 1 < len(centers) else None
        wi = np.ones_like(L)
        if left is not None:
            wi = np.where(L < c, np.clip((L - left) / (c - left), 0, 1), wi)
        if right is not None:
            wi = np.where(L > c, np.clip((right - L) / (right - c), 0, 1), wi)
        w.append(wi)
    total = sum(w)
    return [wi / total for wi in w]


def band_cast(L, a, b, mask=None):
    """Mean a*/b* per band, weighted; transparent pixels excluded when mask is given."""
    out = []
    for wi in weights(L):
        if mask is not None:
            wi = wi * mask
        s = float(wi.sum()) or 1.0
        out.append((float((a * wi).sum() / s), float((b * wi).sum() / s)))
    return out


def match(image, references, strength=0.8, bands=None):
    import numpy as np
    L, a, b, alpha = load(image)
    if alpha is not None and not (alpha >= ALPHA_MIN).any():
        raise ValueError('image has no opaque pixels')
    src = band_cast(L, a, b, mask_of(alpha))
    ref_casts = []
    for r in references:
        rl, ra, rb, ralpha = load(r)
        ref_casts.append(band_cast(rl, ra, rb, mask_of(ralpha)))
    tgt = [(float(np.mean([c[i][0] for c in ref_casts])), float(np.mean([c[i][1] for c in ref_casts])))
           for i in range(len(BANDS))]
    active = set(bands or [n for n, _ in BANDS])
    w = weights(L)
    da = sum(wi * (t[0] - s[0]) * (strength if n in active else 0) for wi, s, t, (n, _) in zip(w, src, tgt, BANDS))
    db = sum(wi * (t[1] - s[1]) * (strength if n in active else 0) for wi, s, t, (n, _) in zip(w, src, tgt, BANDS))
    out = from_lab(L, a + da, b + db)
    if alpha is not None:
        from PIL import Image
        out = out.convert('RGBA')
        out.putalpha(Image.fromarray(alpha))
    report = {name: {'image_ab': [round(s[0], 1), round(s[1], 1)], 'reference_ab': [round(t[0], 1), round(t[1], 1)],
                     'applied': name in active}
              for (name, _), s, t in zip(BANDS, src, tgt)}
    return out, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', type=Path)
    p.add_argument('--reference', type=Path, action='append', required=True)
    p.add_argument('--strength', type=float, default=0.8, help='0..1 share of the cast difference to remove')
    p.add_argument('--bands', nargs='+', choices=[n for n, _ in BANDS], help='limit correction to these bands')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    try:
        if not 0 <= a.strength <= 1:
            raise ValueError('--strength must be between 0 and 1')
        out, report = match(a.image, a.reference, a.strength, a.bands)
        with a.out.open('xb') as f:
            out.save(f, format='PNG')
        print(json.dumps({'tool': 'art_tone_match', 'out': str(a.out.resolve()), 'strength': a.strength,
                          'bands': report, 'note': 'Lightness unchanged. Open the result and compare; this is not a style verdict.'}, indent=2))
        return 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Requires Pillow and numpy; --out must not exist.'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
