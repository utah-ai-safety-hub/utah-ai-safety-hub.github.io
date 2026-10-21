"""Draw the home page contours of Mount Timpanogos and the elevation grid behind them.

    python3 tools/hero_contours.py

Writes images/contours-timpanogos.svg (contour lines every 100 m, heavier every 500 m,
used as a CSS mask) and images/timpanogos-elevation.bin (140 x 105 cells of elevation
in feet, uint16 little-endian, read by site.js for the live readout). Elevation data
comes from AWS Terrain Tiles (built mainly from USGS 3DEP) and is cached in
tools/.cache/tiles.
"""
import math
import pathlib
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
TILES = ROOT / "tools" / ".cache" / "tiles"
LAT, LON = 40.3908, -111.6458        # Mount Timpanogos summit
Z, W, H = 13, 560, 420               # zoom level and crop size in pixels (~14.5 m each)


def get_tile(x, y):
    path = TILES / f"{Z}_{x}_{y}.png"
    if not path.exists():
        TILES.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png", path)
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768   # meters


def blur(a, r):
    k = np.exp(-np.arange(-2 * r, 2 * r + 1) ** 2 / (2 * r * r)); k /= k.sum()
    f = lambda v: np.convolve(np.pad(v, 2 * r, mode="edge"), k, "valid")
    return np.apply_along_axis(f, 1, np.apply_along_axis(f, 0, a))


def main():
    n = 2 ** Z
    fx = (LON + 180) / 360 * n
    fy = (1 - math.asinh(math.tan(math.radians(LAT))) / math.pi) / 2 * n
    tx, ty = int(fx), int(fy)
    mosaic = np.vstack([np.hstack([get_tile(tx + dx, ty + dy) for dx in (-1, 0, 1)]) for dy in (-1, 0, 1)])
    px, py = int((fx - tx + 1) * 256), int((fy - ty + 1) * 256)
    # Summit right of center so the lines sweep in from the left.
    x0, y0 = px - int(W * 0.58), py - H // 2
    crop = mosaic[y0:y0 + H, x0:x0 + W]

    # Contours.
    sm = blur(crop, 3)
    lo, hi = math.floor(sm.min() / 100) * 100, math.ceil(sm.max() / 100) * 100
    cs = plt.contour(sm, levels=np.arange(lo, hi + 1, 100))
    paths = []
    for level, segs in zip(cs.levels, cs.allsegs):
        cls = "index" if level % 500 == 0 else "minor"
        for seg in segs:
            if len(seg) < 6:
                continue
            pts, last = [], None
            for x, y in seg:
                if last is None or abs(x - last[0]) + abs(y - last[1]) > 3.2:
                    pts.append((x, y)); last = (x, y)
            if len(pts) >= 3:
                paths.append(f'<path class="{cls}" d="M' + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + '"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" fill="none" stroke="#000">\n'
           '<style>.minor{stroke-width:.7;stroke-opacity:.55}.index{stroke-width:1.3;stroke-opacity:.9}</style>\n'
           f'<!-- Mount Timpanogos ({LAT}, {LON}). Contours every 100 m, heavier every 500 m. Data: AWS Terrain Tiles (USGS 3DEP and others). -->\n'
           + "\n".join(paths) + "\n</svg>\n")
    (ROOT / "images" / "contours-timpanogos.svg").write_text(svg)

    # Elevation grid for the live readout, averaged over 4 x 4 pixel cells, in feet.
    grid = crop.reshape(H // 4, 4, W // 4, 4).mean(axis=(1, 3)) * 3.28084
    np.round(grid).astype("<u2").tofile(ROOT / "images" / "timpanogos-elevation.bin")
    print(f"Wrote {len(paths)} contour paths and a {W // 4} x {H // 4} elevation grid "
          f"(summit {crop.max() * 3.28084:,.0f} ft).")


if __name__ == "__main__":
    main()
