"""Rank candidate images against reference images with objective style metrics, to choose
between variants (different prompts, references, edits or color corrections) of the same asset.

Metrics (lower is better):
- cast_shadows / cast_midtones / cast_highlights: distance in a*/b* between the candidate's and
  the references' mean color cast in each lightness band (catches "brown shadows", "orange light").
- dark_hue_gap: difference between the candidate's darkest 5% chroma and the references' (a*/b*).
- value_gap: mean absolute difference of lightness percentiles p2/p50/p98.
- off_palette: share of area farther than --max-delta from the style palette (only with --palette).
The total is a weighted sum. WEIGHTS are an uncalibrated first estimate; compare totals only
between candidates scored against the same references in the same run. It is a gate and
tie-breaker, NOT an art verdict: always open the top candidates and review them visually.
References must be the same kind of deliverable as the candidates (icon vs approved icons,
scene vs scene screenshots, texture render vs approved texture render).
Transparent pixels (alpha < 128) are ignored, so icons and sprites are measured on the asset only.
Requires Pillow and numpy."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tone_match import load, mask_of, band_cast, BANDS  # noqa: E402
from palette_report import report as palette_report, load_palette, DEFAULT_MAX_DELTA  # noqa: E402

# Uncalibrated estimate: band casts and dark chroma decide the "feel" of the style most.
WEIGHTS = {'cast_shadows': 1.5, 'cast_midtones': 1.0, 'cast_highlights': 0.5,
           'dark_hue_gap': 1.0, 'value_gap': 0.5, 'off_palette': 20.0}
DARK_SHARE = 0.05  # darkest 5% of pixels define the shadow color


def profile(path):
    import numpy as np
    L, a, b, alpha = load(path)
    mask = mask_of(alpha)
    casts = band_cast(L, a, b, mask)
    keep = np.ones(L.size, bool) if mask is None else mask.ravel()
    if not keep.any():
        raise ValueError(f'{path}: no opaque pixels')
    flat, fa, fb = L.ravel()[keep], a.ravel()[keep], b.ravel()[keep]
    dark = flat <= np.quantile(flat, DARK_SHARE)
    from PIL import Image
    with Image.open(path) as im:
        rgb = np.asarray(im.convert('RGB')).reshape(-1, 3)[keep]
    mean = rgb[dark].mean(axis=0)
    return {'casts': casts, 'dark_hex': '#%02x%02x%02x' % tuple(int(round(v)) for v in mean),
            'dark_ab': (float(fa[dark].mean()), float(fb[dark].mean())),
            'value': [float(np.percentile(flat, q)) for q in (2, 50, 98)]}


def dist(p, q):
    return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5


def score(candidates, references, palette=None, max_delta=DEFAULT_MAX_DELTA):
    import numpy as np
    refs = [profile(r) for r in references]
    ref_casts = [tuple(np.mean([r['casts'][i][k] for r in refs]) for k in (0, 1)) for i in range(len(BANDS))]
    ref_dark = tuple(np.mean([r['dark_ab'][k] for r in refs]) for k in (0, 1))
    ref_value = [float(np.mean([r['value'][i] for r in refs])) for i in range(3)]
    rows = []
    for c in candidates:
        p = profile(c)
        m = {f'cast_{name}': round(dist(p['casts'][i], ref_casts[i]), 2) for i, (name, _) in enumerate(BANDS)}
        m['dark_hue_gap'] = round(dist(p['dark_ab'], ref_dark), 2)
        m['value_gap'] = round(sum(abs(x - y) for x, y in zip(p['value'], ref_value)) / 3, 2)
        if palette:
            m['off_palette'] = palette_report(c, 10, palette, max_delta)['off_palette_share']
        m['total'] = round(sum(WEIGHTS[k] * v for k, v in m.items() if k in WEIGHTS), 2)
        rows.append({'candidate': str(Path(c)), **m})
    rows.sort(key=lambda r: r['total'])
    for i, r in enumerate(rows, 1):
        r['rank'] = i
    return {'tool': 'art_score_variants', 'references': [str(Path(r)) for r in references],
            'weights': WEIGHTS, 'ranking': rows,
            'next': 'Open the top candidates and review visually; metrics cannot see drawing errors or extra details.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('candidates', nargs='*', type=Path)
    p.add_argument('--profile', action='store_true', help='only describe the references (dark color, band casts, value) for the style sheet')
    p.add_argument('--reference', type=Path, action='append', required=True)
    p.add_argument('--palette', nargs='+', help='#RRGGBB values or JSON file (style palette)')
    p.add_argument('--max-delta', type=float, default=DEFAULT_MAX_DELTA)
    a = p.parse_args()
    try:
        if a.profile:
            out = []
            for r in a.reference:
                pr = profile(r)
                out.append({'reference': str(r), 'dark5_mean_hex': pr['dark_hex'], 'dark5_ab': [round(v, 1) for v in pr['dark_ab']],
                            'band_casts_ab': {n: [round(v, 1) for v in pr['casts'][i]] for i, (n, _) in enumerate(BANDS)},
                            'value_p2_p50_p98': [round(v, 1) for v in pr['value']]})
            print(json.dumps({'tool': 'art_reference_profile', 'references': out}, indent=2))
            return 0
        if not a.candidates:
            p.error('candidates required unless --profile')
        print(json.dumps(score(a.candidates, a.reference, load_palette(a.palette) if a.palette else None, a.max_delta), indent=2))
        return 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e), 'hint': 'Requires Pillow and numpy.'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
