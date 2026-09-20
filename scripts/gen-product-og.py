#!/usr/bin/env python3
"""
Generate OG/social-share images for devhandbook.io product pages
(finance-tracker, sovereign-stack) — these are plain HTML pages with no
YAML frontmatter, so the blog OG generator doesn't cover them.

Apple-style 1200x630 cards, matching the existing og-images/ design language.
Outputs PNGs into og-images/ (already an Eleventy passthrough dir).

Usage: python3 scripts/gen-product-og.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "og-images"

CARD_W, CARD_H = 1200, 630
BG = (251, 251, 253)          # #fbfbfd
ACCENT = (0, 113, 227)        # #0071e3
TEXT = (29, 29, 31)           # #1d1d1f
SECONDARY = (110, 110, 115)   # #6e6e73
GRID = (240, 240, 242)

PRODUCTS = [
    {
        "out": "finance-tracker.png",
        "tag": "GOOGLE SHEETS TEMPLATE  ·  $15",
        "title": "Small Business Finance Tracker",
        "desc": "Know your numbers without the bookkeeping headache. Six automated sheets that talk to each other.",
    },
    {
        "out": "sovereign-stack.png",
        "tag": "FREE GUIDE",
        "title": "The Sovereign Finance Stack",
        "desc": "Self-host your money tools with a local AI that never sees your data. Six-part field guide.",
    },
]


def load_fonts():
    paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.dfont",
    ]

    def _load(size, bold=False):
        for p in paths:
            try:
                idx = 1 if (bold and ".ttc" in p) else 0
                return ImageFont.truetype(p, size, index=idx)
            except Exception:
                continue
        return ImageFont.load_default()

    return {
        "brand": _load(24, bold=True),
        "tag": _load(20, bold=True),
        "title": _load(56, bold=True),
        "desc": _load(28),
    }


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], []
    for w in words:
        test = " ".join(cur + [w])
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def main():
    fonts = load_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for p in PRODUCTS:
        img = Image.new("RGB", (CARD_W, CARD_H), BG)
        d = ImageDraw.Draw(img)

        # top accent bar
        d.rectangle([0, 0, CARD_W, 4], fill=ACCENT)
        # subtle grid
        for x in range(0, CARD_W, 60):
            d.line([(x, 0), (x, CARD_H)], fill=GRID, width=1)
        for y in range(0, CARD_H, 60):
            d.line([(0, y), (CARD_W, y)], fill=GRID, width=1)

        mx = 80
        cw = CARD_W - mx * 2

        # brand
        d.text((mx, 52), "devhandbook.io", font=fonts["brand"], fill=ACCENT)

        # tag pill
        tag_txt = f"  {p['tag']}  "
        bb = d.textbbox((0, 0), tag_txt, font=fonts["tag"])
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.rounded_rectangle(
            [mx, 110, mx + tw + 16, 110 + th + 14], radius=8,
            fill=(0, 113, 227, 20), outline=(0, 113, 227, 60), width=1,
        )
        d.text((mx + 8, 117), tag_txt, font=fonts["tag"], fill=ACCENT)

        # title
        ty = 190
        for line in wrap(d, p["title"], fonts["title"], cw)[:2]:
            d.text((mx, ty), line, font=fonts["title"], fill=TEXT)
            bb = d.textbbox((0, 0), line, font=fonts["title"])
            ty += (bb[3] - bb[1]) + 10

        # description
        dy = ty + 24
        for line in wrap(d, p["desc"], fonts["desc"], cw)[:2]:
            d.text((mx, dy), line, font=fonts["desc"], fill=SECONDARY)
            bb = d.textbbox((0, 0), line, font=fonts["desc"])
            dy += (bb[3] - bb[1]) + 8

        # footer dots
        for i in range(5):
            dx = CARD_W - 100 + i * 14
            d.ellipse([dx, CARD_H - 40, dx + 6, CARD_H - 34], fill=(0, 113, 227, 40))

        out = OUT_DIR / p["out"]
        img.save(out, "PNG")
        print(f"✅ {out.name} ({CARD_W}x{CARD_H})")


if __name__ == "__main__":
    main()
