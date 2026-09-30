#!/usr/bin/env python3
"""World-folder covers for the home screen.

Composites the existing preschool illustrations (white knocked out) onto a
soft scene so each world reads as one picture: animals, food, home,
shapes-and-colors, play. No text — the Hebrew label sits under the tile.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = 1024


def lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(len(a)))


def knock_out(path, tol=42):
    im = Image.open(ASSETS / path).convert("RGBA")
    arr = np.array(im)
    rgb = arr[:, :, :3].astype(np.int16)
    alpha = arr[:, :, 3]
    if alpha.min() < 8 and alpha[0, 0] < 8 and alpha[-1, -1] < 8:
        return im
    border = np.concatenate(
        [rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]], axis=0
    )
    bg = np.median(border, axis=0)
    dist = np.abs(rgb - bg).sum(axis=2)
    like = dist < tol
    reach = np.zeros(like.shape, dtype=bool)
    reach[0, :] = like[0, :]
    reach[-1, :] = like[-1, :]
    reach[:, 0] = like[:, 0]
    reach[:, -1] = like[:, -1]
    h, w = like.shape
    for _ in range(max(h, w)):
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        grown &= like
        if np.array_equal(grown, reach):
            break
        reach = grown
    arr[:, :, 3] = np.where(reach, 0, alpha)
    out = Image.fromarray(arr, "RGBA")
    # Soften the cut so pale fur does not look scissored.
    a = out.getchannel("A").filter(ImageFilter.GaussianBlur(0.6))
    out.putalpha(a)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out


def fit(sprite, height):
    ratio = height / sprite.size[1]
    w = max(1, int(sprite.size[0] * ratio))
    return sprite.resize((w, height), Image.Resampling.LANCZOS)


def scene(top, bottom):
    img = Image.new("RGB", (SIZE, SIZE))
    px = img.load()
    cx = cy = (SIZE - 1) / 2
    for y in range(SIZE):
        t = y / (SIZE - 1)
        row = lerp(top, bottom, t)
        for x in range(SIZE):
            dx = (x - cx) / SIZE
            dy = (y - cy) / SIZE
            light = max(0.0, 1 - (dx * dx + dy * dy) * 1.35)
            px[x, y] = lerp(row, (255, 252, 245), light * 0.28)
    return img.convert("RGBA")


def hill(base, color, top_y):
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([-80, top_y, SIZE + 80, SIZE + 280], fill=color + (255,))
    shade = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(shade).ellipse(
        [-40, top_y + 36, SIZE + 40, SIZE + 320], fill=(0, 0, 0, 28)
    )
    shade = shade.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(shade)
    base.alpha_composite(layer)
    return base


def sun(base, xy, radius, color):
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    x, y = xy
    ImageDraw.Draw(layer).ellipse(
        [x - radius, y - radius, x + radius, y + radius], fill=color + (230,)
    )
    glow = layer.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(glow)
    base.alpha_composite(layer)
    return base


def paste(base, sprite, cx, cy):
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sw, sh = sprite.size
    x = int(cx - sw / 2)
    y = int(cy - sh / 2)
    blob = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(blob).ellipse(
        [x + sw * 0.18, y + sh * 0.78, x + sw * 0.82, y + sh * 0.98],
        fill=(50, 40, 30, 70),
    )
    blob = blob.filter(ImageFilter.GaussianBlur(10))
    shadow.alpha_composite(blob)
    base.alpha_composite(shadow)
    base.alpha_composite(sprite, (x, y))


def build(name, top, bottom, ground, items, sun_at=None):
    base = scene(top, bottom)
    if sun_at:
        base = sun(base, sun_at[0], sun_at[1], sun_at[2])
    base = hill(base, ground, 560)
    for path, height, cx, cy in items:
        paste(base, fit(knock_out(path), height), cx, cy)
    out = ASSETS / name
    base.convert("RGB").save(out, "PNG", optimize=True)
    print(f"wrote {out.name} {base.size}")


def main():
    build(
        "world_animals.png",
        (214, 236, 206),
        (142, 186, 146),
        (108, 166, 112),
        [
            ("bird.png", 300, 250, 430),
            ("fish.png", 280, 790, 450),
            ("cat.png", 430, 340, 690),
            ("dog.png", 420, 710, 700),
        ],
        sun_at=((180, 170), 78, (255, 236, 170)),
    )
    build(
        "world_food.png",
        (255, 236, 206),
        (244, 186, 132),
        (214, 146, 86),
        [
            ("food_banana.png", 340, 250, 470),
            ("food_orange.png", 280, 800, 460),
            ("food_apple.png", 400, 390, 700),
            ("veg_carrot.png", 360, 700, 710),
        ],
        sun_at=((820, 160), 70, (255, 214, 140)),
    )
    build(
        "world_home.png",
        (206, 230, 248),
        (168, 204, 232),
        (154, 186, 120),
        [
            ("close_house.png", 520, 400, 600),
            ("car.png", 280, 800, 720),
            ("nest.png", 220, 180, 430),
            ("bone.png", 180, 760, 480),
        ],
        sun_at=((840, 150), 72, (255, 244, 190)),
    )
    build(
        "world_shapes.png",
        (236, 226, 252),
        (196, 176, 230),
        (154, 176, 214),
        [
            ("shape_circle.png", 280, 280, 430),
            ("shape_star.png", 280, 760, 420),
            ("shape_square.png", 260, 300, 720),
            ("color_red_ball.png", 250, 560, 640),
            ("shape_triangle.png", 250, 790, 730),
        ],
        sun_at=((160, 150), 64, (255, 236, 186)),
    )
    build(
        "world_play.png",
        (255, 244, 206),
        (255, 206, 140),
        (232, 164, 96),
        [
            ("puzzle_dog_head.png", 420, 360, 560),
            ("emo_happy.png", 340, 760, 500),
            ("odd_ball.png", 230, 220, 730),
            ("odd_teddy.png", 280, 800, 740),
        ],
        sun_at=((180, 160), 80, (255, 228, 150)),
    )


if __name__ == "__main__":
    main()
