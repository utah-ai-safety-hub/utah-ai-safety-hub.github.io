#!/bin/zsh
# Render the PNG exports and icons from brand/svg/ with headless Chrome.
#
#     zsh tools/logo_png.sh
#
# Writes brand/png/ (tiles, lockups, og-image.png), favicon.ico, favicon.svg, and
# apple-touch-icon.png. Needs Google Chrome and Python with Pillow (tools/requirements.txt).
# Set CHROME to use a different browser binary.
set -e
cd "$(dirname "$0")/.."
ROOT=$PWD
CHROME=${CHROME:-"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}
PY=${PYTHON:-python3}
SVG=$ROOT/brand/svg
PNG=$ROOT/brand/png
mkdir -p $PNG

# render <svg> <out.png> <width> <height> [background]
render() {
    local html=$(mktemp -t render).html
    print -r -- "<!doctype html><html><body style=\"margin:0;background:${5:-transparent};width:${3}px;height:${4}px;display:grid;place-items:center\"><img src=\"file://$1\" style=\"width:${3}px;height:${4}px;object-fit:contain\"></body></html>" > $html
    "$CHROME" --headless=new --hide-scrollbars --default-background-color=00000000 --window-size=$3,$4 --screenshot=$2 "file://$html" 2>/dev/null
    rm -f $html
}
# height for a given width, from the SVG's viewBox
height() { $PY -c "import re,sys;w,h=map(float,re.search(r'viewBox=\"0 0 ([\d.]+) ([\d.]+)',open(sys.argv[1]).read()).groups());print(round(int(sys.argv[2])*h/w))" $1 $2; }

for c in pine paper mint; do
    for s in 512 1024 2048; do render $SVG/uash-tile-$c.svg $PNG/uash-tile-$c-$s.png $s $s; done
    render $SVG/uash-logo-horizontal-$c.svg $PNG/uash-logo-horizontal-$c.png 1600 $(height $SVG/uash-logo-horizontal-$c.svg 1600)
    render $SVG/uash-logo-stacked-$c.svg $PNG/uash-logo-stacked-$c.png 1000 $(height $SVG/uash-logo-stacked-$c.svg 1000)
done
for s in 16 32 48 180 192; do render $SVG/uash-tile-pine-small.svg $PNG/uash-tile-pine-small-$s.png $s $s; done

# Link-preview image: the horizontal logo on paper, 1200 x 630.
html=$(mktemp -t og).html
print -r -- "<!doctype html><html><body style=\"margin:0;width:1200px;height:630px;background:#f7f8f4;display:grid;place-items:center\"><img src=\"file://$SVG/uash-logo-horizontal-pine.svg\" style=\"width:820px\"></body></html>" > $html
"$CHROME" --headless=new --hide-scrollbars --window-size=1200,630 --screenshot=$PNG/og-image.png "file://$html" 2>/dev/null
rm -f $html

# Site icons.
cp $SVG/uash-tile-pine-small.svg $ROOT/favicon.svg
cp $PNG/uash-tile-pine-small-180.png $ROOT/apple-touch-icon.png
$PY - "$PNG" "$ROOT/favicon.ico" <<'PY'
import sys
from PIL import Image
png, out = sys.argv[1], sys.argv[2]
imgs = [Image.open(f"{png}/uash-tile-pine-small-{s}.png").convert("RGBA") for s in (16, 32, 48)]
imgs[2].save(out, sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
PY
echo "Rendered PNGs and icons."
