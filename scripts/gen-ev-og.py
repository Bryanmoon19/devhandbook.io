#!/usr/bin/env python3
"""Generate the OG image for the EV Dividend landing page (1200x630)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), (15, 23, 42))  # #0f172a
d = ImageDraw.Draw(img)

def font(size, bold=False):
    for path in [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

# Accent bar
d.rectangle([0, 0, W, 8], fill=(16, 185, 129))  # #10b981

# Eyebrow
d.text((80, 90), "devhandbook.io", font=font(30), fill=(148, 163, 184))

# Title
d.text((80, 150), "EV Dividend Report", font=font(78, True), fill=(241, 245, 249))

# Subtitle
d.text((80, 280), "Know exactly what your EV is saving you —", font=font(42), fill=(203, 213, 225))
d.text((80, 340), "down to the penny per mile.", font=font(42), fill=(203, 213, 225))

# Three metric cards
card_y = 460
card_w = 320
card_h = 110
cards = [
    ("CHARGING COST", "$101", (100, 116, 139)),
    ("GAS-EQUIVALENT", "$235", (100, 116, 139)),
    ("YOUR EV DIVIDEND", "$134", (52, 211, 153)),
]
x = 80
for label, value, vcolor in cards:
    d.rounded_rectangle([x, card_y, x + card_w, card_y + card_h], radius=14, fill=(30, 41, 59))
    d.text((x + 24, card_y + 22), label, font=font(22), fill=(148, 163, 184))
    d.text((x + 24, card_y + 50), value, font=font(46, True), fill=vcolor)
    x += card_w + 20

img.save("/Users/walle/Projects/devhandbook.io/og-images/ev-dividend.png")
print("Wrote og-images/ev-dividend.png")
