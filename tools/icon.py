# Draws the Ledger app icon: three rising bars on a soft charcoal gradient, the tallest in green.
# Usage: python3 tools/icon.py <output dir>
import sys
from PIL import Image, ImageDraw

S = 1024
PAPER, GREY, GREEN = (244, 244, 241), (150, 153, 157), (116, 194, 154)

def draw(pad=0.0):
    im = Image.new("RGB", (S, S)); px = im.load()
    for y in range(S):
        t = y / (S - 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((34, 36, 40), (12, 13, 14)))
        for x in range(S): px[x, y] = c
    d = ImageDraw.Draw(im)
    k = 1 - 2 * pad
    P = lambda v: S * (pad + v * k)
    base, w = 0.78, 0.15
    for x, h, col in [(0.22, 0.30, GREY), (0.42, 0.44, PAPER), (0.62, 0.60, GREEN)]:
        d.rounded_rectangle([P(x), P(base - h), P(x + w), P(base)], radius=int(S * 0.045 * k), fill=col)
    return im

out = sys.argv[1]
full = draw()
for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (32, "favicon-32.png")]:
    full.resize((size, size), Image.LANCZOS).save(f"{out}/{name}")
draw(0.10).resize((512, 512), Image.LANCZOS).save(f"{out}/icon-maskable-512.png")
print("icons written")
