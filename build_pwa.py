#!/usr/bin/env python3
"""
NBA 2K27 Cap Breaker & Pro Build Architect PWA Builder
Generates index.html, 2k27-lab-portable.html, manifest.json, sw.js, icon.svg, and PNG icons.
All data is sourced from NBA2KLab, LockerCodes, LGC, and official 2K27 Season 2 / Patch 2.0 notes.
"""
import json, os, base64, subprocess, shutil, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(ROOT, exist_ok=True)
os.makedirs(os.path.join(ROOT, "screenshots"), exist_ok=True)

VERSION = "2k27-s2-v1"

# ---------- 1. ICON SVG & PNGs ----------
icon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#060911"/>
      <stop offset="50%" stop-color="#0D1526"/>
      <stop offset="100%" stop-color="#05070C"/>
    </linearGradient>
    <linearGradient id="neon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#00FF87"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFE066"/>
      <stop offset="100%" stop-color="#F59E0B"/>
    </linearGradient>
    <linearGradient id="leg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FF4D6D"/>
      <stop offset="100%" stop-color="#A855F7"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="110" fill="url(#bg)"/>
  <rect x="16" y="16" width="480" height="480" rx="94" fill="none" stroke="url(#gold)" stroke-width="6" stroke-opacity="0.65"/>
  <polygon points="256,50 434,132 398,384 256,462 114,384 78,132" fill="#0A1220" stroke="url(#neon)" stroke-width="8"/>
  <circle cx="256" cy="210" r="88" fill="none" stroke="url(#gold)" stroke-width="5" stroke-opacity="0.45" stroke-dasharray="12,6"/>
  <text x="256" y="228" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-weight="900" font-size="98" fill="#F8FAFC" letter-spacing="-4">2K27</text>
  <rect x="116" y="256" width="280" height="48" rx="12" fill="url(#gold)"/>
  <text x="256" y="289" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-weight="900" font-size="27" fill="#060911" letter-spacing="2.5">CAP ARCHITECT</text>
  <rect x="148" y="322" width="216" height="34" rx="8" fill="url(#leg)"/>
  <text x="256" y="345" text-anchor="middle" font-family="monospace" font-weight="800" font-size="20" fill="#FFFFFF" letter-spacing="1.5">S2 · PATCH 2.0 · LAB</text>
</svg>'''

open(os.path.join(ROOT, "icon.svg"), "w", encoding="utf-8").write(icon_svg)

def render_png(size, out):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome: return False
    d = tempfile.mkdtemp()
    h = os.path.join(d, "i.html")
    svg_sized = icon_svg.replace("<svg ", '<svg width="%d" height="%d" ' % (size, size), 1)
    open(h, "w").write('<html><body style="margin:0;background:#060911">' + svg_sized + '</body></html>')
    try:
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={size},{size}", f"--screenshot={out}", "file://" + h],
                       check=True, capture_output=True, timeout=60)
        return os.path.exists(out)
    except Exception:
        return False

pngs = {}
for sz, name in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")]:
    if render_png(sz, os.path.join(ROOT, name)):
        pngs[sz] = name

icons = [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]
for sz in (192, 512):
    if sz in pngs:
        icons.append({"src": pngs[sz], "sizes": f"{sz}x{sz}", "type": "image/png", "purpose": "any"})

manifest = {
    "name": "NBA 2K27 Cap Breaker & Pro Build Architect",
    "short_name": "2K27 Lab",
    "description": "NBA 2K27 Season 2 (Patch 2.0) Cap Breaker Simulator (+1 to +28), 53-Badge & Animation Gate Matrix, Synergy Fuse (+1/+2 to Legend) & Token Loadout Planner.",
    "id": "./index.html",
    "start_url": "./index.html#tab=simulator",
    "scope": "./",
    "display": "standalone",
    "background_color": "#060911",
    "theme_color": "#060911",
    "orientation": "any",
    "icons": icons,
}
json.dump(manifest, open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8"), indent=2)

assets = ["./", "./index.html", "./manifest.json", "./icon.svg"] + [f"./{v}" for v in pngs.values()]
sw_js = """const CACHE_NAME = 'nba2k27-lab-%s';
const ASSETS = %s;
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((r) => {
      if (r && r.status === 200 && r.type === 'basic') {
        const copy = r.clone(); caches.open(CACHE_NAME).then((c) => c.put(e.request, copy));
      }
      return r;
    }).catch(() => caches.match('./index.html')))
  );
});
""" % (VERSION, json.dumps(assets))
open(os.path.join(ROOT, "sw.js"), "w", encoding="utf-8").write(sw_js)
print("Generated icons, manifest.json, sw.js")

# ---------- 2. DATA + APP ----------
subprocess.run(["python3", os.path.join(ROOT, "gen_data.py")], check=True)
SRC = os.path.join(ROOT, "src")
data = json.load(open(os.path.join(SRC, "data.json"), encoding="utf-8"))
css = open(os.path.join(SRC, "base.css"), encoding="utf-8").read() + "\n" + open(os.path.join(SRC, "app.css"), encoding="utf-8").read()
js = open(os.path.join(SRC, "app.js"), encoding="utf-8").read()
tpl = open(os.path.join(SRC, "index.template.html"), encoding="utf-8").read()
data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
SW_REG = """<script>if('serviceWorker' in navigator && location.protocol.startsWith('http')){addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));}</script>"""
def page(portable):
    icon = ("data:image/svg+xml;base64," + base64.b64encode(icon_svg.encode()).decode()) if portable else "icon.svg"
    touch = icon if portable else ("apple-touch-icon.png" if 180 in pngs else "icon.svg")
    h = tpl
    for k, v in {"__MANIFEST_LINK__": "" if portable else '<link rel="manifest" href="manifest.json">', "__ICON_HREF__": icon, "__TOUCH_HREF__": touch,
                 "__CHECKED__": data["checked"], "__SW__": "" if portable else SW_REG}.items():
        h = h.replace(k, v)
    h = h.replace("__CSS__", css).replace("__DATA__", data_js).replace("__JS__", js)
    return h
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page(False))
open(os.path.join(ROOT, "2k27-lab-portable.html"), "w", encoding="utf-8").write(page(True))
print("index.html", os.path.getsize(os.path.join(ROOT, "index.html")), "bytes · portable", os.path.getsize(os.path.join(ROOT, "2k27-lab-portable.html")))
