"""Generate a construction SVG from known camera-space points. Does not edit or evaluate art."""
import argparse
import html
import json
import math
from pathlib import Path
import sys


def project(scene):
    w, h = scene['size']
    if not all(isinstance(v, int) and 0 < v <= 16384 for v in (w, h)):
        raise ValueError('size must be positive integers <= 16384')
    kind = scene['projection']
    if kind == 'perspective':
        fov = scene['vertical_fov_deg']
        if not math.isfinite(fov) or not 0 < fov < 180:
            raise ValueError('vertical FOV must be between 0 and 180 degrees')
        fy = h / (2 * math.tan(math.radians(fov) / 2))
    elif kind == 'orthographic':
        span = scene['vertical_span']
        if not math.isfinite(span) or span <= 0:
            raise ValueError('vertical_span must be positive')
        fy = h / span
    else:
        raise ValueError('projection must be perspective or orthographic')
    near = scene.get('near', 0.001)
    if not math.isfinite(near) or near <= 0:
        raise ValueError('near must be positive')
    out = []
    for x, y, z in scene['points']:
        if not all(math.isfinite(v) for v in (x, y, z)) or z <= near:
            raise ValueError('points must be finite and in front of the near plane; clipping is not implemented')
        scale = fy / z if kind == 'perspective' else fy
        out.append([w / 2 + x * scale, h / 2 - y * scale])
    if not out:
        raise ValueError('points cannot be empty')
    for a, b in scene['edges']:
        if not all(isinstance(i, int) and 0 <= i < len(out) for i in (a, b)):
            raise ValueError('edge index out of range')
    return out


def svg(scene, points):
    w, h = scene['size']
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
             '<rect width="100%" height="100%" fill="white"/>', '<g stroke="#24708a" stroke-width="2">']
    for a, b in scene['edges']:
        x1, y1 = points[a]; x2, y2 = points[b]
        parts.append(f'<line x1="{x1:.4f}" y1="{y1:.4f}" x2="{x2:.4f}" y2="{y2:.4f}"/>')
    parts.append('</g>')
    for i, (x, y) in enumerate(points):
        parts.append(f'<text x="{x+3:.4f}" y="{y-3:.4f}" font-size="12">{i}</text>')
    parts.append('<text x="8" y="18" font-size="12">' + html.escape(scene.get('label', 'Camera-space construction guide')) + '</text></svg>')
    return '\n'.join(parts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('scene', type=Path)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    try:
        scene = json.loads(a.scene.read_text())
        points = project(scene)
        with a.out.open('x') as f:
            f.write(svg(scene, points))
        print(json.dumps({'projection': scene['projection'], 'points_px': points,
                          'output': str(a.out.resolve()), 'scope': 'Known camera-space geometry only'}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({'error': str(e)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
