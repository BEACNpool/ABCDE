#!/usr/bin/env python3
"""Generate 1200x630 Open Graph share cards + per-hook permalink pages.

Shared links (X / Discord / Telegram) unfurl with a branded image + the
headline, which is what actually drives clicks. One card per hook plus a main
card. Rendered with Pillow (no browser — deterministic and deploy-safe).

Reads  web/dist/data/hooks.json + stats.json
Writes web/dist/og/<slug>.png  and  web/dist/r/<slug>.html   (gitignored)

Run with the system Python that has Pillow:  python3 scripts/build_og_cards.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "web" / "dist"
OG = DIST / "og"
R = DIST / "r"
BASE = "https://beacnpool.github.io/ABCDE"
W, H = 1200, 630

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)

CYAN = (34, 211, 238); TEXT = (241, 245, 249); MUTED = (148, 163, 184)
MUTED2 = (100, 116, 139); GREEN = (52, 211, 153); AMBER = (251, 191, 36)

def grade_color(g):
    if "FACT" in g: return GREEN
    if "STRONG" in g: return CYAN
    return AMBER

def gradient_bg():
    top, bot = (12, 28, 56), (2, 6, 23)
    img = Image.new("RGB", (W, H), bot)
    px = img.load()
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return img

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def hexagon(draw, cx, cy, r, color, width=4):
    import math
    pts = [(cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a)))
           for a in range(0, 360, 60)]
    draw.polygon(pts, outline=color, width=width)

def card(slug, kicker, grade, headline, sub):
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=CYAN)  # top accent
    pad = 64
    # brand
    with Image.open(DIST / "brand/beacn-20260904.png") as source:
        badge = source.convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
        img.paste(badge, (pad - 8, 50), badge)
    d.text((pad + 70, 58), "ABCDE", font=font(30), fill=TEXT)
    d.text((pad + 72, 92), "BEACN DATA EXPLORER", font=font(13), fill=CYAN)
    # grade chip (top-right)
    gc = grade_color(grade)
    gf = font(17)
    gw = d.textlength(grade, font=gf)
    chip_w = gw + 40
    d.rounded_rectangle([W - pad - chip_w, 60, W - pad, 104], radius=22,
                        outline=gc, width=2, fill=(gc[0] // 8, gc[1] // 8, gc[2] // 8))
    d.text((W - pad - chip_w + 20, 72), grade, font=gf, fill=gc)
    # kicker
    d.text((pad, 210), kicker.upper(), font=font(20), fill=CYAN)
    # headline (scale down if long)
    size = 62 if len(headline) <= 46 else (52 if len(headline) <= 66 else 44)
    hf = font(size)
    lines = wrap(d, headline, hf, W - 2 * pad)
    y = 250
    for ln in lines:
        d.text((pad, y), ln, font=hf, fill=TEXT)
        y += int(size * 1.12)
    # sub
    sf = font(24, bold=False)
    y = max(y + 14, 430)
    for ln in wrap(d, sub, sf, W - 2 * pad)[:3]:
        d.text((pad, y), ln, font=sf, fill=MUTED)
        y += 34
    # footer
    d.text((pad, H - 58), "beacnpool.github.io/ABCDE  ·  on-chain, graded, reproducible",
           font=font(19, bold=False), fill=MUTED2)
    vt = "Verify it yourself →"
    d.text((W - pad - d.textlength(vt, font=font(19)), H - 58), vt, font=font(19), fill=CYAN)
    OG.mkdir(parents=True, exist_ok=True)
    img.save(OG / f"{slug}.png")

def permalink(slug, headline, sub):
    t, dsc = html.escape(headline), html.escape(sub)
    img, url = f"{BASE}/og/{slug}.png", f"{BASE}/r/{slug}.html"
    R.mkdir(parents=True, exist_ok=True)
    (R / f"{slug}.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{t} — ABCDE</title>
<meta property="og:type" content="website">
<meta property="og:site_name" content="ABCDE — A BEACN Cardano Data Explorer">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{dsc}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{dsc}">
<meta name="twitter:image" content="{img}">
<meta http-equiv="refresh" content="0; url={BASE}/#reveal">
<link rel="canonical" href="{BASE}/#reveal">
</head><body style="background:#020617;color:#94a3b8;font-family:system-ui;padding:40px">
Redirecting to <a style="color:#22d3ee" href="{BASE}/#reveal">the ABCDE explorer</a>…
<script>location.replace({json.dumps(BASE + '/#reveal')})</script></body></html>\n""")

def main():
    hooks = json.loads((DIST / "data/hooks.json").read_text())
    stats = json.loads((DIST / "data/stats.json").read_text())
    for p in (OG, R):
        if p.exists():
            for f in p.iterdir(): f.unlink()
    card("main", f"genesis ADA · NIGHT · SecondFi · epoch {stats['tip_epoch']}",
         "FACT", "The whole chain, one clone away.",
         "Clone the dataset and point your AI at it — genesis ADA, NIGHT, SecondFi, tracers. On-chain, graded, reproducible.")
    for h in hooks:
        card(h["slug"], h["kicker"], h["grade"], h["headline"], h["sub"])
        permalink(h["slug"], h["headline"], h["sub"])
    print(f"done. {len(hooks)+1} cards -> web/dist/og/, {len(hooks)} permalinks -> web/dist/r/")

if __name__ == "__main__":
    main()
