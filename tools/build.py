"""Builds the installable Ledger app from the shared Freedom Ledger page.

The page source (the same file published inside Claude) is split into its head part
(title, fonts, styles) and its body, then wrapped with what a home-screen app needs:
iOS/Android app metadata, a manifest, icons and a service worker for offline use.

Usage: python3 tools/build.py <path to shared index.html> <output dir>
"""
import hashlib, json, pathlib, shutil, sys

src_path, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
src = src_path.read_text()
cut = src.index('<header class="top">')
head_part, body_part = src[:cut], src[cut:]
icons_dir = pathlib.Path(__file__).resolve().parent.parent / "icons"
icon_v = hashlib.sha1(b"".join(f.read_bytes() for f in sorted(icons_dir.glob("*.png")))).hexdigest()[:8]
version = hashlib.sha1(src.encode() + icon_v.encode()).hexdigest()[:10]

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Ledger">
<meta name="application-name" content="Ledger">
<meta name="theme-color" content="#F4F4F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E0F10" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png?v={icon_v}">
<link rel="icon" type="image/png" href="icons/favicon-32.png?v={icon_v}">
<style>
:root{{padding-top:env(safe-area-inset-top,0px)}}
body{{margin:0}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
html,body{{overscroll-behavior-y:none}}
</style>
{head_part.strip()}
</head>
<body>
{body_part.strip()}
<script>
if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {{}}));
try {{ navigator.storage && navigator.storage.persist && navigator.storage.persist(); }} catch (e) {{}}
</script>
</body>
</html>
"""

manifest = {
    "name": "Freedom Ledger",
    "short_name": "Ledger",
    "description": "Net worth, budget, debt payoff and goals.",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0E0F10",
    "theme_color": "#131416",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

sw = f"""// Ledger offline support. Cache name changes with every build so updates replace old files.
const CACHE = "ledger-{version}";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/favicon-32.png"];
self.addEventListener("install", e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); }});
self.addEventListener("activate", e => {{ e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener("fetch", e => {{
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {{
    // App files: try the network first so updates arrive, fall back to the saved copy offline.
    e.respondWith(fetch(req).then(res => {{ const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res; }})
      .catch(() => caches.match(req).then(r => r || caches.match("index.html"))));
  }} else if (url.host.endsWith("fonts.googleapis.com") || url.host.endsWith("fonts.gstatic.com")) {{
    // Fonts: saved copy first, refreshed in the background.
    e.respondWith(caches.open(CACHE).then(c => c.match(req).then(hit => {{
      const net = fetch(req).then(res => {{ c.put(req, res.clone()); return res; }}).catch(() => hit);
      return hit || net;
    }})));
  }}
}});
"""

out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(html)
(out / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2))
(out / "sw.js").write_text(sw)
(out / ".nojekyll").write_text("")
icons_src = icons_dir
if icons_src.resolve() != (out / "icons").resolve():
    shutil.copytree(icons_src, out / "icons", dirs_exist_ok=True)
print(f"built {out} (version {version})")
