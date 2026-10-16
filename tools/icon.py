# Draws the Ledger app icon: an ink page with faint ledger rules, a heavy "L" whose foot is the
# baseline, and the green endpoint dot from the app's charts.
from PIL import Image, ImageDraw
S = 1024
def draw(pad=0.0):
    im = Image.new("RGB", (S, S), (19, 20, 22))
    d = ImageDraw.Draw(im)
    def X(v): return int(S*pad + v*(S*(1-2*pad)))
    for y in (0.30, 0.42, 0.54):
        d.rounded_rectangle([X(0.20), X(y), X(0.80), X(y)+max(3, int(S*0.008))], radius=4, fill=(70, 72, 76))
    paper = (244, 244, 241)
    d.rounded_rectangle([X(0.25), X(0.20), X(0.39), X(0.76)], radius=int(S*0.02), fill=paper)   # stem
    d.rounded_rectangle([X(0.25), X(0.64), X(0.70), X(0.76)], radius=int(S*0.02), fill=paper)   # foot
    r = (X(0.80)-X(0.70))*0.55
    cx, cy = X(0.775), X(0.70)
    d.ellipse([cx-r*1.9, cy-r*1.9, cx+r*1.9, cy+r*1.9], fill=(40, 62, 50))
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(116, 194, 154))
    return im
import sys
out = sys.argv[1]
full = draw(0.0)
for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (32, "favicon-32.png")]:
    full.resize((size, size), Image.LANCZOS).save(f"{out}/{name}")
draw(0.10).resize((512, 512), Image.LANCZOS).save(f"{out}/icon-maskable-512.png")
print("icons written")
