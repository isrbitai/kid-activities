#!/usr/bin/env python3
"""Phase 1 assets: size balls, 3-piece dog puzzle, food/animal sort bin.

Size balls match the preschool card style of gen/make_shapes_colors.py.
Puzzle pieces are rendered from gen/svg/puzzle_dog_*.svg.
The animal-home bin is normalized from the illustrated source in gen/src/.
"""
from pathlib import Path
import random

import cairosvg
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
SVG = Path(__file__).resolve().parent / "svg"
SRC = Path(__file__).resolve().parent / "src"

W, H = 1280, 720
RX = 72
BORDER = 22
MARGIN = 14


def lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def make_card(border_rgb, bg_rgb, bg2_rgb=None):
    bg2 = bg2_rgb or bg_rgb
    img = Image.new("RGB", (W, H), (255, 255, 255))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [MARGIN + 3, MARGIN + 8, W - MARGIN - 1, H - MARGIN + 4], radius=RX, fill=(0, 0, 0, 42)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([MARGIN, MARGIN, W - MARGIN - 1, H - MARGIN - 1], radius=RX, fill=border_rgb)

    inner = [MARGIN + BORDER, MARGIN + BORDER, W - MARGIN - BORDER - 1, H - MARGIN - BORDER - 1]
    ir = RX - 14
    grad = Image.new("RGB", (W, H), bg_rgb)
    gd = ImageDraw.Draw(grad)
    ih = inner[3] - inner[1]
    for y in range(inner[1], inner[3] + 1):
        t = (y - inner[1]) / max(ih, 1)
        gd.line([(inner[0], y), (inner[2], y)], fill=lerp(bg_rgb, bg2, t))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(inner, radius=ir, fill=255)
    img.paste(grad, (0, 0), mask)

    rng = random.Random(7)
    px = img.load()
    for _ in range(14000):
        x = rng.randint(inner[0] + 4, inner[2] - 4)
        y = rng.randint(inner[1] + 4, inner[3] - 4)
        c = px[x, y]
        n = rng.randint(-5, 5)
        px[x, y] = (
            max(0, min(255, c[0] + n)),
            max(0, min(255, c[1] + n)),
            max(0, min(255, c[2] + n)),
        )
    return img


def soft_ellipse_shadow(img, bbox, blur=12, alpha=48):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(bbox, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def draw_face(draw, cx, cy, scale=1.0, color=(26, 26, 26)):
    e = int(14 * scale)
    gap = int(36 * scale)
    draw.ellipse([cx - gap // 2 - e, cy - e, cx - gap // 2 + e, cy + e], fill=color)
    draw.ellipse([cx + gap // 2 - e, cy - e, cx + gap // 2 + e, cy + e], fill=color)
    h = max(3, int(5 * scale))
    draw.ellipse(
        [cx - gap // 2 - e + int(3 * scale), cy - e + int(3 * scale),
         cx - gap // 2 - e + int(3 * scale) + h * 2, cy - e + int(3 * scale) + h * 2],
        fill=(255, 255, 255),
    )
    draw.ellipse(
        [cx + gap // 2 - e + int(3 * scale), cy - e + int(3 * scale),
         cx + gap // 2 - e + int(3 * scale) + h * 2, cy - e + int(3 * scale) + h * 2],
        fill=(255, 255, 255),
    )
    sw = max(3, int(4.5 * scale))
    bbox = [cx - int(20 * scale), cy + int(6 * scale), cx + int(20 * scale), cy + int(36 * scale)]
    draw.arc(bbox, start=20, end=160, fill=color, width=sw)


def paint_ellipse_grad(img, bbox, c_top, c_bot, outline=None, ow=5):
    x0, y0, x1, y1 = [int(v) for v in bbox]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    grad = Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1))
    gd = ImageDraw.Draw(grad)
    h = y1 - y0
    for y in range(h + 1):
        gd.line([(0, y), (x1 - x0, y)], fill=lerp(c_top, c_bot, y / max(h, 1)))
    mask = Image.new("L", (x1 - x0 + 1, y1 - y0 + 1), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, x1 - x0, y1 - y0], fill=255)
    layer.paste(grad, (x0, y0), mask)
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    if outline:
        ImageDraw.Draw(out).ellipse(bbox, outline=outline, width=ow)
    return out


def make_size_ball(scale):
    """Same red ball as the color pack, drawn smaller or larger on an identical card."""
    img = make_card((210, 90, 90), (255, 240, 238), (255, 220, 214))
    cx, cy = W // 2, H // 2 + 8
    # Full-size reference radius is ~260 (the color-pack ball).
    r = 250 * scale
    bbox = [cx - r, cy - r, cx + r, cy + r]
    shadow = [cx - r * 0.92, cy + r * 0.72, cx + r * 0.92, cy + r * 0.92]
    img = soft_ellipse_shadow(img, shadow, blur=max(8, int(14 * scale)), alpha=50)
    ow = max(4, int(8 * scale))
    img = paint_ellipse_grad(img, bbox, (255, 120, 110), (200, 40, 40), outline=(150, 25, 25), ow=ow)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.ellipse(
        [cx - r * 0.42, cy - r * 0.62, cx - r * 0.02, cy - r * 0.18],
        fill=(255, 255, 255, 110),
    )
    hd.ellipse(
        [cx + r * 0.28, cy + r * 0.16, cx + r * 0.52, cy + r * 0.38],
        fill=(255, 255, 255, 50),
    )
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, cx, cy + int(8 * scale), 1.55 * scale)
    return img.convert("RGB")


def render_svg(name, out_name, scale=2):
    png = cairosvg.svg2png(url=str(SVG / name), scale=scale)
    path = OUT / out_name
    path.write_bytes(png)
    im = Image.open(path)
    print(f"wrote {path} {im.size}")


def save_sort_home():
    src = Image.open(SRC / "sort_home_kennel.jpg").convert("RGB")
    src = src.resize((1280, 720), Image.Resampling.LANCZOS)
    path = OUT / "sort_home.png"
    src.save(path, "PNG", optimize=True)
    print(f"wrote {path} {src.size}")


def save(name, img):
    path = OUT / name
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path} {img.size}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    save("size_ball_big.png", make_size_ball(1.0))
    save("size_ball_mid.png", make_size_ball(0.68))
    save("size_ball_small.png", make_size_ball(0.42))
    render_svg("puzzle_dog_head.svg", "puzzle_dog_head.png")
    render_svg("puzzle_dog_body.svg", "puzzle_dog_body.png")
    render_svg("puzzle_dog_tail.svg", "puzzle_dog_tail.png")
    save_sort_home()
    print("done")


if __name__ == "__main__":
    main()
