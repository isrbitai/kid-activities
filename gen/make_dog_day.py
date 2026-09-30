#!/usr/bin/env python3
"""A Dog's Day sequence cards — clear single-action scenes, animals-pack style."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path
import math
import random

OUT = Path("/workspace/animal-match/assets")
W, H = 656, 376
RX = 48
BORDER = 14
MARGIN = 8

BODY = (168, 112, 72)
BODY_D = (138, 88, 54)
EAR = (92, 58, 36)
EAR_I = (120, 78, 55)
CREAM = (245, 230, 205)
CREAM_D = (230, 210, 180)
NOSE = (32, 28, 26)
INK = (26, 26, 26)
TONGUE = (240, 130, 150)
OUTLINE = (70, 48, 32)


def lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(len(a)))


def make_card(border_rgb, bg_rgb, bg2_rgb=None):
    bg2 = bg2_rgb or bg_rgb
    img = Image.new("RGB", (W, H), (255, 255, 255))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [MARGIN + 2, MARGIN + 5, W - MARGIN - 1, H - MARGIN + 2],
        radius=RX, fill=(0, 0, 0, 40),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [MARGIN, MARGIN, W - MARGIN - 1, H - MARGIN - 1],
        radius=RX, fill=border_rgb,
    )
    inner = [
        MARGIN + BORDER, MARGIN + BORDER,
        W - MARGIN - BORDER - 1, H - MARGIN - BORDER - 1,
    ]
    ir = RX - 10
    grad = Image.new("RGB", (W, H), bg_rgb)
    gd = ImageDraw.Draw(grad)
    ih = inner[3] - inner[1]
    for y in range(inner[1], inner[3] + 1):
        t = (y - inner[1]) / max(ih, 1)
        gd.line([(inner[0], y), (inner[2], y)], fill=lerp(bg_rgb, bg2, t))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(inner, radius=ir, fill=255)
    img.paste(grad, (0, 0), mask)
    rng = random.Random(42)
    px = img.load()
    for _ in range(5000):
        x = rng.randint(inner[0] + 2, inner[2] - 2)
        y = rng.randint(inner[1] + 2, inner[3] - 2)
        c = px[x, y]
        n = rng.randint(-4, 4)
        px[x, y] = (
            max(0, min(255, c[0] + n)),
            max(0, min(255, c[1] + n)),
            max(0, min(255, c[2] + n)),
        )
    return img


def soft_ellipse_shadow(img, bbox, blur=8, alpha=50):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(bbox, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def paint_ellipse_grad(img, bbox, c_top, c_bot, outline=None, ow=3):
    x0, y0, x1, y1 = bbox
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


def paint_roundrect_grad(img, xy, radius, c_top, c_bot, outline=None, ow=3):
    x0, y0, x1, y1 = xy
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    grad = Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1))
    gd = ImageDraw.Draw(grad)
    h = y1 - y0
    for y in range(h + 1):
        gd.line([(0, y), (x1 - x0, y)], fill=lerp(c_top, c_bot, y / max(h, 1)))
    mask = Image.new("L", (x1 - x0 + 1, y1 - y0 + 1), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, x1 - x0, y1 - y0], radius=radius, fill=255)
    layer.paste(grad, (x0, y0), mask)
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    if outline:
        ImageDraw.Draw(out).rounded_rectangle(xy, radius=radius, outline=outline, width=ow)
    return out


def draw_ear(d, cx, cy, side=1, scale=1.0):
    ew, eh = int(40 * scale), int(58 * scale)
    x0 = cx + side * int(44 * scale) - ew // 2
    y0 = cy - int(6 * scale)
    d.ellipse([x0, y0, x0 + ew, y0 + eh], fill=EAR, outline=OUTLINE, width=3)
    d.ellipse(
        [x0 + int(8 * scale), y0 + int(12 * scale),
         x0 + ew - int(8 * scale), y0 + eh - int(10 * scale)],
        fill=EAR_I,
    )


def draw_front_face(d, cx, cy, scale=1.0, mode="smile"):
    """mode: smile | yawn | sleepy | eating"""
    e = int(12 * scale)
    gap = int(30 * scale)
    if mode == "sleepy":
        for sx in (-1, 1):
            bx = cx + sx * gap // 2
            d.arc([bx - e, cy - e // 2, bx + e, cy + e],
                  start=200, end=340, fill=INK, width=max(3, int(3.5 * scale)))
    elif mode == "eating":
        for sx in (-1, 1):
            bx = cx + sx * gap // 2
            d.ellipse([bx - e, cy - e, bx + e, cy + e], fill=INK)
            h = max(2, int(3.5 * scale))
            d.ellipse([bx - e + int(2 * scale), cy - e + int(2 * scale),
                       bx - e + int(2 * scale) + h * 2, cy - e + int(2 * scale) + h * 2],
                      fill=(255, 255, 255))
    else:
        for sx in (-1, 1):
            bx = cx + sx * gap // 2
            d.ellipse([bx - e, cy - e, bx + e, cy + e], fill=INK)
            h = max(2, int(3.5 * scale))
            d.ellipse([bx - e + int(2 * scale), cy - e + int(2 * scale),
                       bx - e + int(2 * scale) + h * 2, cy - e + int(2 * scale) + h * 2],
                      fill=(255, 255, 255))
    nw, nh = int(15 * scale), int(12 * scale)
    d.ellipse([cx - nw // 2, cy + int(6 * scale), cx + nw // 2, cy + int(6 * scale) + nh], fill=NOSE)

    if mode == "yawn":
        d.ellipse([cx - int(18 * scale), cy + int(16 * scale),
                   cx + int(18 * scale), cy + int(40 * scale)],
                  fill=(40, 30, 28), outline=INK, width=2)
        d.ellipse([cx - int(11 * scale), cy + int(26 * scale),
                   cx + int(11 * scale), cy + int(38 * scale)], fill=TONGUE)
    elif mode == "smile":
        sw = max(2, int(3 * scale))
        d.arc([cx - int(18 * scale), cy + int(10 * scale),
               cx + int(18 * scale), cy + int(32 * scale)],
              start=20, end=160, fill=INK, width=sw)
        d.ellipse([cx - int(7 * scale), cy + int(22 * scale),
                   cx + int(7 * scale), cy + int(34 * scale)], fill=TONGUE)


def draw_sitting_dog(img, cx, cy, scale=1.0, face_mode="smile", stretch=False):
    s = scale
    img = soft_ellipse_shadow(
        img,
        [cx - int(72 * s), cy + int(95 * s), cx + int(72 * s), cy + int(120 * s)],
        blur=6, alpha=42,
    )
    img = paint_ellipse_grad(
        img,
        [cx - int(72 * s), cy - int(10 * s), cx + int(72 * s), cy + int(102 * s)],
        BODY, BODY_D, outline=OUTLINE, ow=3,
    )
    img = paint_ellipse_grad(
        img,
        [cx - int(40 * s), cy + int(5 * s), cx + int(40 * s), cy + int(88 * s)],
        CREAM, CREAM_D, outline=None,
    )
    for sx in (-1, 1):
        px = cx + sx * int(34 * s)
        img = paint_ellipse_grad(
            img,
            [px - int(22 * s), cy + int(78 * s), px + int(22 * s), cy + int(110 * s)],
            CREAM, CREAM_D, outline=OUTLINE, ow=2,
        )
    hx, hy = cx, cy - int(56 * s)
    img = paint_ellipse_grad(
        img,
        [hx - int(60 * s), hy - int(54 * s), hx + int(60 * s), hy + int(54 * s)],
        BODY, BODY_D, outline=OUTLINE, ow=3,
    )
    patch = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(patch).ellipse(
        [hx - int(56 * s), hy - int(32 * s), hx - int(4 * s), hy + int(26 * s)],
        fill=(*EAR, 230),
    )
    img = Image.alpha_composite(img.convert("RGBA"), patch)
    img = paint_ellipse_grad(
        img,
        [hx - int(34 * s), hy - int(4 * s), hx + int(34 * s), hy + int(44 * s)],
        CREAM, CREAM_D, outline=OUTLINE, ow=2,
    )
    d = ImageDraw.Draw(img)
    draw_ear(d, hx, hy - int(20 * s), side=-1, scale=s)
    draw_ear(d, hx, hy - int(20 * s), side=1, scale=s)
    draw_front_face(d, hx, hy + int(2 * s), scale=s * 1.05, mode=face_mode)

    if stretch:
        # raised paws stretching upward
        for sx in (-1, 1):
            ax = cx + sx * int(55 * s)
            ay0 = hy - int(10 * s)
            ay1 = hy - int(70 * s)
            d.rounded_rectangle(
                [ax - int(12 * s), ay1, ax + int(12 * s), ay0],
                radius=10, fill=BODY, outline=OUTLINE, width=2,
            )
            d.ellipse(
                [ax - int(18 * s), ay1 - int(16 * s), ax + int(18 * s), ay1 + int(10 * s)],
                fill=CREAM, outline=OUTLINE, width=2,
            )
    return img.convert("RGBA")


def draw_side_dog(img, cx, cy, scale=1.0, facing=1, mode="walk", mouth_open=False):
    """mode: walk | play | sleep_curl | eat"""
    s = scale
    d = ImageDraw.Draw(img)

    if mode == "sleep_curl":
        # curled sleeping dog — oval body + tucked head
        img = soft_ellipse_shadow(
            img,
            [cx - int(90 * s), cy + int(40 * s), cx + int(90 * s), cy + int(70 * s)],
            blur=7, alpha=45,
        )
        img = paint_ellipse_grad(
            img,
            [cx - int(95 * s), cy - int(35 * s), cx + int(75 * s), cy + int(55 * s)],
            BODY, BODY_D, outline=OUTLINE, ow=3,
        )
        # cream belly curl
        img = paint_ellipse_grad(
            img,
            [cx - int(50 * s), cy - int(5 * s), cx + int(40 * s), cy + int(45 * s)],
            CREAM, CREAM_D, outline=None,
        )
        # head tucked on left/right
        hx = cx - facing * int(55 * s)
        hy = cy - int(5 * s)
        img = paint_ellipse_grad(
            img,
            [hx - int(42 * s), hy - int(38 * s), hx + int(42 * s), hy + int(38 * s)],
            BODY, BODY_D, outline=OUTLINE, ow=3,
        )
        d = ImageDraw.Draw(img)
        # ear
        d.ellipse(
            [hx - int(10 * s), hy - int(55 * s), hx + int(28 * s), hy - int(8 * s)],
            fill=EAR, outline=OUTLINE, width=2,
        )
        # closed eye
        d.arc(
            [hx - int(8 * s), hy - int(10 * s), hx + int(18 * s), hy + int(10 * s)],
            start=200, end=340, fill=INK, width=3,
        )
        # nose
        d.ellipse(
            [hx - facing * int(28 * s) - int(8 * s), hy + int(2 * s),
             hx - facing * int(28 * s) + int(8 * s), hy + int(16 * s)],
            fill=NOSE,
        )
        # muzzle cream
        img = paint_ellipse_grad(
            img,
            [hx - int(28 * s), hy - int(2 * s), hx + int(10 * s), hy + int(28 * s)],
            CREAM, CREAM_D, outline=OUTLINE, ow=2,
        )
        d = ImageDraw.Draw(img)
        d.ellipse(
            [hx - facing * int(22 * s) - int(7 * s), hy + int(4 * s),
             hx - facing * int(22 * s) + int(7 * s), hy + int(16 * s)],
            fill=NOSE,
        )
        d.arc(
            [hx - int(12 * s), hy - int(8 * s), hx + int(14 * s), hy + int(12 * s)],
            start=200, end=340, fill=INK, width=3,
        )
        # tiny paw tucked
        d.ellipse(
            [cx + int(40 * s), cy + int(25 * s), cx + int(70 * s), cy + int(50 * s)],
            fill=CREAM, outline=OUTLINE, width=2,
        )
        return img.convert("RGBA")

    # body
    bx0 = cx - int(58 * s)
    by0 = cy - int(30 * s)
    bx1 = cx + int(58 * s)
    by1 = cy + int(38 * s)
    img = soft_ellipse_shadow(
        img,
        [cx - int(70 * s), cy + int(55 * s), cx + int(70 * s), cy + int(80 * s)],
        blur=6, alpha=40,
    )
    img = paint_ellipse_grad(img, [bx0, by0, bx1, by1], BODY, BODY_D, outline=OUTLINE, ow=3)
    d = ImageDraw.Draw(img)

    # legs — walking stride vs standing
    if mode == "walk":
        legs = [
            (cx - int(35 * s), cy + int(18 * s), -8),
            (cx - int(10 * s), cy + int(22 * s), 6),
            (cx + int(15 * s), cy + int(18 * s), -4),
            (cx + int(38 * s), cy + int(22 * s), 10),
        ]
    elif mode == "play":
        # front paws up / playful
        legs = [
            (cx - int(30 * s), cy + int(10 * s), -25),
            (cx - int(5 * s), cy + int(5 * s), -20),
            (cx + int(20 * s), cy + int(25 * s), 0),
            (cx + int(42 * s), cy + int(28 * s), 5),
        ]
    else:
        legs = [
            (cx - int(30 * s), cy + int(22 * s), 0),
            (cx + int(20 * s), cy + int(22 * s), 0),
        ]

    for lx, ly, lean in legs:
        d.rounded_rectangle(
            [lx - int(11 * s) + lean, ly, lx + int(11 * s) + lean, ly + int(48 * s)],
            radius=8, fill=BODY, outline=OUTLINE, width=2,
        )
        d.ellipse(
            [lx - int(15 * s) + lean, ly + int(38 * s),
             lx + int(15 * s) + lean, ly + int(58 * s)],
            fill=CREAM, outline=OUTLINE, width=2,
        )

    # head
    hx = cx + facing * int(58 * s)
    hy = cy - int(22 * s)
    if mode == "eat":
        # head lowered into bowl
        hx = cx + facing * int(50 * s)
        hy = cy + int(18 * s)
    img = paint_ellipse_grad(
        img,
        [hx - int(40 * s), hy - int(40 * s), hx + int(40 * s), hy + int(40 * s)],
        BODY, BODY_D, outline=OUTLINE, ow=3,
    )
    d = ImageDraw.Draw(img)
    # snout
    snx = hx + facing * int(30 * s)
    sny = hy + (int(8 * s) if mode == "eat" else 0)
    img = paint_ellipse_grad(
        img,
        [snx - int(24 * s), sny - int(10 * s), snx + int(24 * s), sny + int(24 * s)],
        CREAM, CREAM_D, outline=OUTLINE, ow=2,
    )
    d = ImageDraw.Draw(img)
    # ear
    ex = hx - facing * int(12 * s)
    d.ellipse(
        [ex - int(18 * s), hy - int(58 * s), ex + int(18 * s), hy - int(6 * s)],
        fill=EAR, outline=OUTLINE, width=2,
    )
    # eye
    eyx = hx + facing * int(8 * s)
    eyy = hy - int(8 * s)
    if mode == "eat":
        eyy = hy - int(14 * s)
    d.ellipse([eyx - int(10 * s), eyy - int(10 * s), eyx + int(10 * s), eyy + int(10 * s)], fill=INK)
    d.ellipse([eyx - int(5 * s), eyy - int(8 * s), eyx - int(1 * s), eyy - int(4 * s)], fill=(255, 255, 255))
    # nose
    nx = snx + facing * int(16 * s)
    d.ellipse([nx - int(8 * s), sny + int(0 * s), nx + int(8 * s), sny + int(14 * s)], fill=NOSE)
    if mouth_open or mode == "play":
        d.ellipse(
            [snx - int(6 * s), sny + int(12 * s), snx + int(14 * s), sny + int(28 * s)],
            fill=(40, 30, 28),
        )
        d.ellipse(
            [snx - int(2 * s), sny + int(18 * s), snx + int(10 * s), sny + int(28 * s)],
            fill=TONGUE,
        )
    elif mode != "eat":
        d.arc(
            [snx - int(10 * s), sny + int(6 * s), snx + int(16 * s), sny + int(24 * s)],
            start=20, end=160, fill=INK, width=2,
        )
        d.ellipse(
            [snx - int(4 * s), sny + int(14 * s), snx + int(8 * s), sny + int(26 * s)],
            fill=TONGUE,
        )
    # wagging / raised tail
    tx = cx - facing * int(58 * s)
    if mode == "play":
        d.arc(
            [tx - int(25 * s), cy - int(70 * s), tx + int(20 * s), cy],
            start=200 if facing == 1 else 20,
            end=340 if facing == 1 else 160,
            fill=BODY, width=max(7, int(9 * s)),
        )
    else:
        d.arc(
            [tx - int(30 * s), cy - int(50 * s), tx + int(12 * s), cy + int(10 * s)],
            start=200 if facing == 1 else 20,
            end=320 if facing == 1 else 140,
            fill=BODY, width=max(6, int(8 * s)),
        )
    # collar for walk
    if mode == "walk":
        d.arc(
            [hx - int(30 * s), hy + int(18 * s), hx + int(30 * s), hy + int(42 * s)],
            start=10, end=170, fill=(60, 120, 200), width=max(4, int(5 * s)),
        )
        # tag
        d.ellipse(
            [hx - int(6 * s), hy + int(32 * s), hx + int(6 * s), hy + int(44 * s)],
            fill=(255, 210, 60), outline=(180, 140, 30), width=1,
        )
    return img.convert("RGBA")


# ---------- Scenes ----------

def make_wake():
    """Dog waking / stretching on bed under big morning sun — unmistakable morning."""
    img = make_card((232, 168, 96), (255, 250, 235), (255, 232, 195))
    d = ImageDraw.Draw(img)

    # BIG sun top-right
    sx, sy, sr = 530, 100, 58
    for a in range(0, 360, 20):
        rad = math.radians(a)
        x0 = sx + int(math.cos(rad) * (sr + 6))
        y0 = sy + int(math.sin(rad) * (sr + 6))
        x1 = sx + int(math.cos(rad) * (sr + 36))
        y1 = sy + int(math.sin(rad) * (sr + 36))
        d.line([(x0, y0), (x1, y1)], fill=(255, 200, 70), width=6)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
              fill=(255, 214, 90), outline=(230, 170, 40), width=3)
    d.ellipse([sx - 20, sy - 24, sx - 6, sy - 10], fill=(255, 255, 220))

    # bed (large, clear)
    img = paint_roundrect_grad(
        img, [90, 230, 500, 330], 22,
        (255, 170, 150), (225, 110, 100), outline=(180, 80, 70), ow=3,
    )
    # pillow
    img = paint_ellipse_grad(
        img, [115, 205, 250, 265],
        (255, 255, 250), (235, 235, 245), outline=(180, 180, 200), ow=2,
    )
    # blanket fold
    d = ImageDraw.Draw(img)
    d.arc([180, 250, 470, 320], start=200, end=340, fill=(255, 210, 200), width=10)

    # dog sitting on bed, yawning + stretch paws
    img = draw_sitting_dog(img, 300, 185, scale=0.92, face_mode="yawn", stretch=True)
    return img.convert("RGB")


def make_eat():
    """Dog with head in food bowl — clearly eating."""
    img = make_card((196, 148, 100), (255, 248, 235), (245, 228, 200))

    # floor shadow oval
    img = soft_ellipse_shadow(img, [120, 300, 560, 350], blur=8, alpha=35)

    # BIG food bowl in center-right, dog head into it from left
    bx, by = 400, 250
    # bowl body
    img = paint_ellipse_grad(
        img, [bx - 95, by - 5, bx + 95, by + 55],
        (230, 95, 85), (185, 50, 45), outline=(140, 40, 35), ow=3,
    )
    # bowl rim
    img = paint_ellipse_grad(
        img, [bx - 105, by - 35, bx + 105, by + 5],
        (255, 165, 145), (230, 100, 90), outline=(140, 40, 35), ow=3,
    )
    d = ImageDraw.Draw(img)
    # kibble pile
    for (kx, ky) in [
        (bx - 35, by - 18), (bx, by - 28), (bx + 30, by - 16),
        (bx - 15, by - 5), (bx + 15, by - 2), (bx + 45, by - 8),
        (bx - 50, by - 5),
    ]:
        d.ellipse([kx - 12, ky - 9, kx + 12, ky + 9],
                  fill=(190, 125, 55), outline=(140, 90, 40), width=1)

    # steam squiggles
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    for i, ox in enumerate((-30, 0, 30)):
        hd.arc(
            [bx + ox - 12, by - 75 - i * 5, bx + ox + 12, by - 35 - i * 5],
            start=200, end=340, fill=(255, 255, 255, 140), width=4,
        )
    img = Image.alpha_composite(img.convert("RGBA"), hi)

    # dog side-view, head lowered INTO bowl
    img = draw_side_dog(img, 230, 200, scale=1.15, facing=1, mode="eat")

    # bone icon on bowl for extra "food" clarity
    d = ImageDraw.Draw(img)
    d.ellipse([bx - 55, by + 20, bx - 35, by + 40], fill=CREAM, outline=OUTLINE, width=1)
    d.ellipse([bx - 25, by + 20, bx - 5, by + 40], fill=CREAM, outline=OUTLINE, width=1)
    d.rounded_rectangle([bx - 48, by + 26, bx - 12, by + 34], radius=3, fill=CREAM)
    return img.convert("RGB")


def make_walk():
    """Dog walking outdoors on leash — clear walk action."""
    img = make_card((110, 160, 120), (232, 250, 238), (205, 236, 218))
    d = ImageDraw.Draw(img)

    # path
    d.ellipse([60, 275, 600, 345], fill=(210, 190, 150))
    # grass tufts
    for gx in range(80, 580, 28):
        d.polygon([(gx, 295), (gx + 7, 268), (gx + 14, 295)], fill=(80, 165, 95))
        d.polygon([(gx + 10, 300), (gx + 16, 275), (gx + 22, 300)], fill=(95, 175, 105))

    # tree
    d.rectangle([505, 165, 528, 290], fill=(140, 100, 60), outline=(100, 70, 40), width=2)
    d.ellipse([465, 100, 570, 210], fill=(70, 155, 85), outline=(45, 115, 55), width=3)
    d.ellipse([480, 115, 520, 155], fill=(115, 185, 120))

    # leash from hand to collar
    d.arc([150, 130, 360, 250], start=200, end=340, fill=(90, 70, 50), width=5)
    # person hand holding leash
    d.ellipse([145, 185, 185, 225], fill=(255, 210, 180), outline=(200, 150, 120), width=2)
    d.ellipse([155, 175, 175, 195], fill=(255, 210, 180), outline=(200, 150, 120), width=2)

    # walking dog with collar
    img = draw_side_dog(img, 300, 215, scale=1.12, facing=1, mode="walk")

    # paw prints on path behind dog
    d = ImageDraw.Draw(img)
    for (px, py) in [(160, 310), (200, 318), (240, 308)]:
        d.ellipse([px - 8, py - 6, px + 8, py + 6], fill=(160, 140, 110))
        d.ellipse([px - 14, py - 14, px - 6, py - 6], fill=(160, 140, 110))
        d.ellipse([px + 6, py - 14, px + 14, py - 6], fill=(160, 140, 110))
    return img.convert("RGB")


def make_play():
    """Dog playfully chasing a bright ball — clear play action."""
    img = make_card((120, 150, 200), (236, 244, 255), (210, 226, 250))
    d = ImageDraw.Draw(img)
    # grass
    d.ellipse([50, 285, 610, 355], fill=(175, 215, 145))
    for gx in range(70, 580, 35):
        d.polygon([(gx, 300), (gx + 8, 275), (gx + 16, 300)], fill=(90, 170, 100))

    # BIG bright ball mid-air / rolling
    bx, by, br = 470, 200, 48
    img = soft_ellipse_shadow(img, [bx - 40, by + 55, bx + 40, by + 75], blur=6, alpha=40)
    img = paint_ellipse_grad(
        img, [bx - br, by - br, bx + br, by + br],
        (255, 130, 110), (220, 45, 45), outline=(160, 30, 30), ow=3,
    )
    d = ImageDraw.Draw(img)
    d.arc([bx - 32, by - 32, bx + 32, by + 8], start=200, end=340, fill=(255, 255, 255), width=4)
    d.line([(bx - 8, by - 38), (bx + 12, by + 8)], fill=(255, 255, 255), width=3)
    d.ellipse([bx - 20, by - 26, bx - 6, by - 12], fill=(255, 210, 200))

    # motion dashes near ball
    for i, ox in enumerate((0, 14, 28)):
        d.line([(bx - 85 - ox, by - 5 + i * 10), (bx - 60 - ox, by - 5 + i * 10)],
               fill=(140, 165, 200), width=4)

    # playful dog leaping toward ball
    img = draw_side_dog(img, 230, 200, scale=1.15, facing=1, mode="play", mouth_open=True)

    # small bounce arcs under dog
    d = ImageDraw.Draw(img)
    d.arc([160, 270, 280, 310], start=200, end=340, fill=(140, 170, 120), width=3)
    return img.convert("RGB")


def make_sleep():
    """Dog curled asleep on bed under moon + Zzz — unmistakable sleep."""
    img = make_card((90, 100, 150), (225, 230, 250), (195, 205, 240))
    d = ImageDraw.Draw(img)

    # crescent moon
    d.ellipse([485, 60, 575, 150], fill=(255, 245, 200), outline=(230, 210, 140), width=3)
    d.ellipse([510, 65, 590, 145], fill=(200, 210, 240))
    # stars
    for (sx, sy, sz) in [(110, 85, 5), (170, 125, 4), (400, 95, 5), (370, 155, 3), (545, 175, 4), (250, 80, 3)]:
        d.ellipse([sx - sz, sy - sz, sx + sz, sy + sz], fill=(255, 240, 160))
        d.line([(sx - sz * 2, sy), (sx + sz * 2, sy)], fill=(255, 240, 160), width=2)
        d.line([(sx, sy - sz * 2), (sx, sy + sz * 2)], fill=(255, 240, 160), width=2)

    # soft bed / cushion
    img = paint_ellipse_grad(
        img, [110, 220, 530, 330],
        (200, 170, 225), (155, 125, 190), outline=(120, 90, 150), ow=3,
    )
    # pillow
    img = paint_ellipse_grad(
        img, [140, 200, 280, 270],
        (250, 245, 255), (230, 220, 245), outline=(180, 170, 200), ow=2,
    )

    # curled sleeping dog
    img = draw_side_dog(img, 340, 245, scale=1.2, facing=-1, mode="sleep_curl")

    # BIG Zzz
    d = ImageDraw.Draw(img)
    for (zx, zy, sz) in [(420, 145, 24), (455, 115, 30), (495, 80, 36)]:
        d.line([(zx, zy), (zx + sz, zy)], fill=(110, 120, 175), width=4)
        d.line([(zx + sz, zy), (zx, zy + sz)], fill=(110, 120, 175), width=4)
        d.line([(zx, zy + sz), (zx + sz, zy + sz)], fill=(110, 120, 175), width=4)
    return img.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = {
        "seq_wake.png": make_wake,
        "seq_eat.png": make_eat,
        "seq_walk.png": make_walk,
        "seq_play.png": make_play,
        "seq_sleep.png": make_sleep,
    }
    for name, fn in cards.items():
        im = fn()
        path = OUT / name
        im.save(path, "PNG", optimize=True)
        print(f"wrote {path} {im.size}")


if __name__ == "__main__":
    main()
