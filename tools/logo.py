"""Draw the logo tile from Mount Timpanogos elevation data and build the SVG logo kit.

    python3 tools/logo.py

Writes brand/svg/: the tile in three colorways (plus heavier-lined -small versions for
16-48 px), the tile beside the name, and the stacked logo. The name is converted to
outlines from Newsreader and Geist (SIL Open Font License), downloaded to
tools/.cache/fonts. Run tools/logo_png.sh afterwards for PNGs and icons.
"""
import math
import pathlib
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / ".cache"
OUT = ROOT / "brand" / "svg"
LAT, LON = 40.3908, -111.6458   # Mount Timpanogos summit
PINE, PAPER, NIGHT, MINT = "#3d6b4f", "#f7f8f4", "#141813", "#82bf96"
FONTS = {
    "Newsreader.ttf": "https://github.com/google/fonts/raw/main/ofl/newsreader/Newsreader%5Bopsz,wght%5D.ttf",
    "Geist.ttf": "https://github.com/google/fonts/raw/main/ofl/geist/Geist%5Bwght%5D.ttf",
}


def get_tile(z, x, y):
    path = CACHE / "tiles" / f"{z}_{x}_{y}.png"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png", path)
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def blur(a, r):
    k = np.exp(-np.arange(-2 * r, 2 * r + 1) ** 2 / (2 * r * r)); k /= k.sum()
    f = lambda v: np.convolve(np.pad(v, 2 * r, mode="edge"), k, "valid")
    return np.apply_along_axis(f, 1, np.apply_along_axis(f, 0, a))


def tile_paths():
    """Five heavy contour lines from a tight crop around the summit (140 x 140 px at zoom 14, ~7 m each)."""
    z = 14
    n = 2 ** z
    fx = (LON + 180) / 360 * n
    fy = (1 - math.asinh(math.tan(math.radians(LAT))) / math.pi) / 2 * n
    tx, ty = int(fx), int(fy)
    dem = np.vstack([np.hstack([get_tile(z, tx + dx, ty + dy) for dx in (-1, 0, 1)]) for dy in (-1, 0, 1)])
    px, py = int((fx - tx + 1) * 256), int((fy - ty + 1) * 256)
    win = dem[py - 20:py + 21, px - 20:px + 21]          # snap to the true high point
    dy_, dx_ = np.unravel_index(win.argmax(), win.shape)
    px, py = px - 20 + dx_, py - 20 + dy_
    r = 70
    b = blur(dem[py - r:py + r, px - r:px + r], 5)
    top = b.max()
    cs = plt.contour(b, levels=sorted(top - np.array([30, 150, 280, 420, 570])))
    out = []
    for segs in cs.allsegs:
        for seg in segs:
            if len(seg) < 10:
                continue
            pts, last = [], None
            for x, y in seg:
                if last is None or abs(x - last[0]) + abs(y - last[1]) > 2:
                    pts.append((x, y)); last = (x, y)
            closed = abs(seg[0][0] - seg[-1][0]) + abs(seg[0][1] - seg[-1][1]) < 1e-6
            out.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if closed else "") + '"/>')
    plt.close("all")
    return "".join(out)


def font(name, axes):
    path = CACHE / "fonts" / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FONTS[name], path)
    return instantiateVariableFont(TTFont(path), axes)


def text_path(f, text, size, tracking=0.0):
    """Outline text; returns (path d, width, cap height) with the baseline at y=0."""
    cmap, gs, upm = f.getBestCmap(), f.getGlyphSet(), f["head"].unitsPerEm
    s = size / upm
    pen = SVGPathPen(gs)
    x = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        x += gs[g].width * s + tracking * size
    x -= tracking * size
    bp = BoundsPen(gs); gs[cmap[ord("H")]].draw(bp)
    return pen.getCommands(), x, bp.bounds[3] * s


def main():
    lines = tile_paths()

    def tile(ink, stroke, bg):
        return (f'<rect width="140" height="140" fill="{bg}"/><g fill="none" stroke="{ink}" stroke-width="{stroke}" '
                f'stroke-linecap="round" stroke-linejoin="round">{lines}</g>')

    def svg(w, h, body):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">'
                f'<title>Utah AI Safety Hub</title>{body}</svg>\n')

    serif = font("Newsreader.ttf", {"opsz": 24, "wght": 400})
    sans = font("Geist.ttf", {"wght": 500})
    word_d, word_w, cap = text_path(serif, "Utah AI Safety Hub", 100)
    caps_d, caps_w, caps_cap = text_path(sans, "UTAH AI SAFETY HUB", 40, tracking=0.32)

    files = {}
    colorways = {  # name: (tile, lines, text)
        "pine": (PINE, PAPER, "#1f241f"),
        "paper": (PAPER, PINE, PAPER),
        "mint": (MINT, NIGHT, "#e5e8e3"),
    }
    for name, (bg, ink, text_color) in colorways.items():
        files[f"uash-tile-{name}.svg"] = svg(140, 140, tile(ink, 5, bg))
        files[f"uash-tile-{name}-small.svg"] = svg(140, 140, tile(ink, 9, bg))
        m, gap = 160, 40
        body = (f'<g transform="scale({m / 140})">{tile(ink, 6, bg)}</g>'
                f'<path transform="translate({m + gap} {m / 2 + cap / 2:.1f})" fill="{text_color}" d="{word_d}"/>')
        files[f"uash-logo-horizontal-{name}.svg"] = svg(m + gap + word_w + 4, m, body)
        t = 240
        w = max(t, caps_w) + 40
        body = (f'<g transform="translate({(w - t) / 2:.1f} 0) scale({t / 140})">{tile(ink, 5, bg)}</g>'
                f'<path transform="translate({(w - caps_w) / 2:.1f} {t + 56 + caps_cap:.1f})" fill="{text_color}" d="{caps_d}"/>')
        files[f"uash-logo-stacked-{name}.svg"] = svg(w, t + 56 + caps_cap + 6, body)

    OUT.mkdir(parents=True, exist_ok=True)
    for fn, content in files.items():
        (OUT / fn).write_text(content)
    print(f"Wrote {len(files)} SVG files to brand/svg/.")


if __name__ == "__main__":
    main()
