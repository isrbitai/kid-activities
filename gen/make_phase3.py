#!/usr/bin/env python3
"""Phase 3 assets: first/then morning cards and identical apple quantity cards.

Wake and eat scenes are illustrated sources in gen/src/phase3/.
Quantity cards stamp the same cut-out apple one, two, or three times so the
only difference is the count, with a large numeral glyph beside the pictures.
"""
import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
SRC = Path(__file__).resolve().parent / "src" / "phase3"

spec = importlib.util.spec_from_file_location(
    "shapes", Path(__file__).resolve().parent / "make_shapes_colors.py"
)
shapes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shapes)

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 108)


def save(name, img):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size}")


def cut_apple():
    im = Image.open(SRC / "qty_apple_src.jpg").convert("RGB")
    w, h = im.size
    px = im.load()
    bg = px[8, 8]

    def close(c):
        return abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) < 48

    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    stack = [(0, 0)]
    seen = set()
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or (x, y) in seen:
            continue
        seen.add((x, y))
        if not close(px[x, y]):
            continue
        mp[x, y] = 255
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    alpha = Image.eval(mask, lambda v: 0 if v else 255)
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    bbox = rgba.getbbox()
    return rgba.crop(bbox)


def paste_apple(card, apple, box):
    sprite = apple.copy()
    sprite.thumbnail((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    x = box[0] + (box[2] - box[0] - sprite.size[0]) // 2
    y = box[1] + (box[3] - box[1] - sprite.size[1]) // 2
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        [x + 18, y + sprite.size[1] - 28, x + sprite.size[0] - 18, y + sprite.size[1] + 10],
        fill=(80, 50, 30, 50),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    card.alpha_composite(shadow)
    card.alpha_composite(sprite, (x, y))


def digit_badge(card, n):
    badge = Image.new("RGBA", card.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    cx, cy, r = 1148, 148, 72
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 248, 236, 245), outline=(196, 92, 48, 255), width=8)
    text = str(n)
    box = d.textbbox((0, 0), text, font=FONT)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text((cx - tw / 2 - box[0], cy - th / 2 - box[1] - 6), text, font=FONT, fill=(176, 64, 36, 255))
    card.alpha_composite(badge)


def quantity_card(apple, n):
    card = shapes.make_card((214, 96, 58), (255, 248, 236), (255, 236, 214)).convert("RGBA")
    layouts = {
        1: [(390, 170, 830, 600)],
        2: [(140, 190, 560, 590), (600, 190, 1020, 590)],
        3: [(60, 210, 380, 570), (400, 210, 720, 570), (740, 210, 1060, 570)],
    }
    for box in layouts[n]:
        paste_apple(card, apple, box)
    digit_badge(card, n)
    return card.convert("RGB")


def main():
    for src_name, out_name in (("ft_wake.jpg", "ft_wake.png"), ("ft_eat.jpg", "ft_eat.png")):
        img = Image.open(SRC / src_name).convert("RGB")
        if img.size != (1280, 720):
            img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        save(out_name, img)

    apple = cut_apple()
    for n in (1, 2, 3):
        save(f"qty_apple_{n}.png", quantity_card(apple, n))


if __name__ == "__main__":
    main()
