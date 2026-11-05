"""Check that an edit kept the structure of the original: same lightness layout and edges,
even if colors changed on purpose. Use after "change only colors" edits, tone_match, or any
edit that must preserve shapes. inspect_image --lock-mask is for exact pixel locks; this tool
is for "keep the drawing, colors may change".

Metrics on the opaque area (alpha >= 128 in the original):
- lightness_changed: share of pixels whose L* moved more than --l-tol (default 10 L* units,
  roughly the step between clearly different values; tone_match keeps L* so expects ~0).
- edge_agreement: share of the original's edge pixels that are still edges in the edit
  (Sobel on L*, edges = top --edge-share of gradient magnitude). 1.0 = identical outlines.
- alpha_changed: share of pixels whose opacity class changed (only when either image has alpha).
Same canvas size is required; no implicit resize. Requires Pillow and numpy."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tone_match import load, ALPHA_MIN  # noqa: E402

DEFAULT_L_TOL = 10.0
# Top 10% gradient magnitude ~ silhouettes and major form edges, not flat-area noise.
DEFAULT_EDGE_SHARE = 0.10


def edges(L, share):
    import numpy as np
    gx = np.zeros_like(L); gy = np.zeros_like(L)
    gx[1:-1, 1:-1] = (L[:-2, 2:] + 2 * L[1:-1, 2:] + L[2:, 2:]) - (L[:-2, :-2] + 2 * L[1:-1, :-2] + L[2:, :-2])
    gy[1:-1, 1:-1] = (L[2:, :-2] + 2 * L[2:, 1:-1] + L[2:, 2:]) - (L[:-2, :-2] + 2 * L[:-2, 1:-1] + L[:-2, 2:])
    mag = np.hypot(gx, gy)
    cut = np.quantile(mag, 1 - share)
    return mag >= max(cut, 1e-6)


def compare(original, edited, l_tol=DEFAULT_L_TOL, edge_share=DEFAULT_EDGE_SHARE):
    import numpy as np
    L0, _, _, a0 = load(original)
    L1, _, _, a1 = load(edited)
    if L0.shape != L1.shape:
        raise ValueError(f'size differs {L0.shape[::-1]} vs {L1.shape[::-1]}; no implicit resize')
    opaque0 = np.ones(L0.shape, bool) if a0 is None else a0 >= ALPHA_MIN
    opaque1 = np.ones(L1.shape, bool) if a1 is None else a1 >= ALPHA_MIN
    area = opaque0
    if not area.any():
        raise ValueError('original has no opaque pixels')
    l_changed = float((np.abs(L1 - L0) > l_tol)[area].mean())
    e0 = edges(L0, edge_share) & area
    e1 = edges(L1, edge_share)
    # Allow one-pixel shifts from resampling/compression: dilate the edit's edges by 1 px.
    e1d = e1.copy()
    e1d[1:, :] |= e1[:-1, :]; e1d[:-1, :] |= e1[1:, :]; e1d[:, 1:] |= e1[:, :-1]; e1d[:, :-1] |= e1[:, 1:]
    agreement = float(e1d[e0].mean()) if e0.any() else 1.0
    result = {'lightness_changed': round(l_changed, 4), 'edge_agreement': round(agreement, 4),
              'l_tol': l_tol, 'edge_share': edge_share}
    if a0 is not None or a1 is not None:
        result['alpha_changed'] = round(float((opaque0 != opaque1).mean()), 4)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('original', type=Path)
    p.add_argument('edited', type=Path)
    p.add_argument('--l-tol', type=float, default=DEFAULT_L_TOL)
    p.add_argument('--edge-share', type=float, default=DEFAULT_EDGE_SHARE)
    p.add_argument('--max-lightness-changed', type=float, help='fail (exit 1) above this share')
    p.add_argument('--min-edge-agreement', type=float, help='fail (exit 1) below this share')
    a = p.parse_args()
    try:
        r = compare(a.original, a.edited, a.l_tol, a.edge_share)
        checks = []
        if a.max_lightness_changed is not None:
            checks.append({'id': 'lightness_kept', 'status': 'pass' if r['lightness_changed'] <= a.max_lightness_changed else 'fail'})
        if a.min_edge_agreement is not None:
            checks.append({'id': 'edges_kept', 'status': 'pass' if r['edge_agreement'] >= a.min_edge_agreement else 'fail'})
        print(json.dumps({'tool': 'art_structure_diff', 'original': str(a.original), 'edited': str(a.edited),
                          **r, 'checks': checks,
                          'note': 'Structure evidence only; open both images to judge the change.'}, indent=2))
        return 1 if any(c['status'] == 'fail' for c in checks) else 0
    except (ImportError, OSError, ValueError) as e:
        print(json.dumps({'error': str(e)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
