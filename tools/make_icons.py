"""Render the Neraki app icons (an evil-eye water drop on the Greek-flag blue) with Pillow.
Usage: python make_icons.py web/icons"""
import math
import sys

from PIL import Image, ImageDraw

BLUE = (13, 94, 175, 255)       # #0d5eaf, the widely cited blue of the Greek flag
LIGHT = (90, 169, 230, 255)     # #5aa9e6
NAVY = (11, 45, 91, 255)        # #0b2d5b


def bez(p0, p1, p2, p3, n=60):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1])
            for t in [i / n for i in range(n + 1)]]


def drop_outline():
    # Same shape as the app logo (viewBox 24x30): M12 2 C8 9 3 13.5 3 19 A9 9 0 0 0 21 19 C21 13.5 16 9 12 2 Z
    arc = [(12 + 9 * math.cos(math.radians(a)), 19 - 9 * math.sin(math.radians(a))) for a in range(180, 361, 3)]
    return bez((12, 2), (8, 9), (3, 13.5), (3, 19)) + arc + bez((21, 19), (21, 13.5), (16, 9), (12, 2))


def render(size, maskable):
    S = size * 4                                            # supersample for smooth edges
    img = Image.new("RGBA", (S, S), BLUE)
    if not maskable:                                        # "any" icon: rounded square
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
        bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        bg.paste(img, (0, 0), mask)
        img = bg
    d = ImageDraw.Draw(img)
    scale = S * (0.50 if maskable else 0.62) / 30           # maskable keeps the mark inside the central safe zone
    ox, oy = (S - 24 * scale) / 2, (S - 30 * scale) / 2 + S * 0.01
    pts = [(ox + x * scale, oy + y * scale) for x, y in drop_outline()]
    d.polygon(pts, fill="white")                            # white drop on the blue square
    cx, cy = ox + 12 * scale, oy + 19 * scale
    for r, col in ((6.3, BLUE), (4.7, "white"), (3.3, LIGHT), (1.8, NAVY)):   # evil-eye rings inside the drop
        d.ellipse([cx - r * scale, cy - r * scale, cx + r * scale, cy + r * scale], fill=col)
    return img.resize((size, size), Image.LANCZOS)


out = sys.argv[1]
render(192, False).save(f"{out}/icon-192.png")
render(512, False).save(f"{out}/icon-512.png")
render(192, True).save(f"{out}/maskable-192.png")
render(512, True).save(f"{out}/maskable-512.png")
render(180, True).convert("RGB").save(f"{out}/apple-touch-icon.png")
print("icons written")
