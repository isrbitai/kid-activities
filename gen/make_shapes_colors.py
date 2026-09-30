#!/usr/bin/env python3
"""Preschool matching cards: צורות (shapes) + צבעים (colors). Soft pastel cards, thick borders, friendly faces."""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math
import random

OUT = Path("/workspace/animal-match/assets")
W, H = 1280, 720
RX = 72
BORDER = 22
MARGIN = 14


def lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


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
        px[x, y] = (max(0, min(255, c[0] + n)), max(0, min(255, c[1] + n)), max(0, min(255, c[2] + n)))
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
    draw.ellipse([cx - gap // 2 - e + int(3 * scale), cy - e + int(3 * scale),
                  cx - gap // 2 - e + int(3 * scale) + h * 2, cy - e + int(3 * scale) + h * 2], fill=(255, 255, 255))
    draw.ellipse([cx + gap // 2 - e + int(3 * scale), cy - e + int(3 * scale),
                  cx + gap // 2 - e + int(3 * scale) + h * 2, cy - e + int(3 * scale) + h * 2], fill=(255, 255, 255))
    sw = max(3, int(4.5 * scale))
    bbox = [cx - int(20 * scale), cy + int(6 * scale), cx + int(20 * scale), cy + int(36 * scale)]
    draw.arc(bbox, start=20, end=160, fill=color, width=sw)


def paint_ellipse_grad(img, bbox, c_top, c_bot, outline=None, ow=5):
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


def paint_roundrect_grad(img, xy, radius, c_top, c_bot, outline=None, ow=5):
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


def star_points(cx, cy, r_outer, r_inner, n=5, rotation=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        ang = rotation + i * math.pi / n
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def paint_polygon_grad(img, pts, c_top, c_bot, outline=None, ow=5):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    grad = Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1))
    gd = ImageDraw.Draw(grad)
    h = y1 - y0
    for y in range(h + 1):
        gd.line([(0, y), (x1 - x0, y)], fill=lerp(c_top, c_bot, y / max(h, 1)))
    mask = Image.new("L", (x1 - x0 + 1, y1 - y0 + 1), 0)
    local = [(p[0] - x0, p[1] - y0) for p in pts]
    ImageDraw.Draw(mask).polygon(local, fill=255)
    layer.paste(grad, (x0, y0), mask)
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    if outline:
        ImageDraw.Draw(out).polygon(pts, outline=outline)
        # thicken outline by drawing lines
        d = ImageDraw.Draw(out)
        for i in range(len(pts)):
            d.line([pts[i], pts[(i + 1) % len(pts)]], fill=outline, width=ow)
    return out


def outline_only_polygon(img, pts, color, width=18):
    d = ImageDraw.Draw(img)
    for i in range(len(pts)):
        d.line([pts[i], pts[(i + 1) % len(pts)]], fill=color, width=width)
    # round joints with circles
    r = width // 2
    for x, y in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    return img


# ---------- SHAPES: filled ----------

def make_shape_circle():
    img = make_card((90, 168, 210), (232, 246, 255), (210, 234, 250))
    img = soft_ellipse_shadow(img, [390, 560, 890, 620], blur=14, alpha=50)
    # square bbox so circle reads as circle, not oval
    bbox = [390, 120, 890, 620]
    img = paint_ellipse_grad(img, bbox, (120, 210, 255), (40, 140, 220), outline=(20, 90, 160), ow=8)
    # highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([420, 180, 620, 300], fill=(255, 255, 255, 90))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 640, 360, 1.6)
    return img.convert("RGB")


def make_outline_circle():
    img = make_card((140, 150, 168), (250, 250, 252), (232, 234, 240))
    img = soft_ellipse_shadow(img, [390, 560, 890, 620], blur=14, alpha=40)
    d = ImageDraw.Draw(img)
    bbox = [390, 120, 890, 620]
    d.ellipse(bbox, outline=(55, 62, 78), width=22)
    faint = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(faint).ellipse([412, 142, 868, 598], fill=(55, 62, 78, 18))
    img = Image.alpha_composite(img.convert("RGBA"), faint)
    return img.convert("RGB")


def make_shape_square():
    img = make_card((232, 150, 90), (255, 246, 232), (255, 230, 200))
    img = soft_ellipse_shadow(img, [360, 530, 920, 590], blur=14, alpha=50)
    xy = [390, 150, 890, 560]
    img = paint_roundrect_grad(img, xy, 36, (255, 180, 90), (230, 110, 40), outline=(170, 70, 20), ow=8)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).rounded_rectangle([430, 180, 700, 280], radius=20, fill=(255, 255, 255, 85))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 640, 360, 1.55)
    return img.convert("RGB")


def make_outline_square():
    img = make_card((140, 150, 168), (250, 250, 252), (232, 234, 240))
    img = soft_ellipse_shadow(img, [360, 530, 920, 590], blur=14, alpha=40)
    d = ImageDraw.Draw(img)
    xy = [390, 150, 890, 560]
    d.rounded_rectangle(xy, radius=36, outline=(55, 62, 78), width=22)
    faint = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(faint).rounded_rectangle([412, 172, 868, 538], radius=28, fill=(55, 62, 78, 18))
    img = Image.alpha_composite(img.convert("RGBA"), faint)
    return img.convert("RGB")


def make_shape_triangle():
    img = make_card((120, 190, 120), (236, 250, 236), (210, 240, 210))
    img = soft_ellipse_shadow(img, [360, 540, 920, 600], blur=14, alpha=50)
    pts = [(640, 130), (980, 560), (300, 560)]
    img = paint_polygon_grad(img, pts, (140, 230, 140), (50, 170, 80), outline=(30, 120, 50), ow=8)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).polygon([(640, 190), (780, 420), (500, 420)], fill=(255, 255, 255, 70))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 640, 400, 1.4)
    return img.convert("RGB")


def make_outline_triangle():
    img = make_card((140, 150, 168), (250, 250, 252), (232, 234, 240))
    img = soft_ellipse_shadow(img, [360, 540, 920, 600], blur=14, alpha=40)
    pts = [(640, 130), (980, 560), (300, 560)]
    # faint fill
    faint = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(faint).polygon(pts, fill=(55, 62, 78, 18))
    img = Image.alpha_composite(img.convert("RGBA"), faint)
    outline_only_polygon(img, pts, (55, 62, 78), width=22)
    return img.convert("RGB")


def make_shape_star():
    img = make_card((210, 170, 70), (255, 250, 230), (255, 240, 190))
    img = soft_ellipse_shadow(img, [360, 530, 920, 590], blur=14, alpha=50)
    pts = star_points(640, 360, 250, 105)
    img = paint_polygon_grad(img, pts, (255, 230, 90), (240, 170, 30), outline=(180, 120, 10), ow=7)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([560, 280, 720, 400], fill=(255, 255, 255, 75))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 640, 360, 1.35)
    return img.convert("RGB")


def make_outline_star():
    img = make_card((140, 150, 168), (250, 250, 252), (232, 234, 240))
    img = soft_ellipse_shadow(img, [360, 530, 920, 590], blur=14, alpha=40)
    pts = star_points(640, 360, 250, 105)
    faint = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(faint).polygon(pts, fill=(55, 62, 78, 18))
    img = Image.alpha_composite(img.convert("RGBA"), faint)
    outline_only_polygon(img, pts, (55, 62, 78), width=20)
    return img.convert("RGB")


# ---------- COLORS: object → paint blob ----------

def make_red_ball():
    img = make_card((210, 90, 90), (255, 240, 238), (255, 220, 214))
    img = soft_ellipse_shadow(img, [380, 520, 900, 580], blur=14, alpha=50)
    bbox = [380, 140, 900, 560]
    img = paint_ellipse_grad(img, bbox, (255, 120, 110), (200, 40, 40), outline=(150, 25, 25), ow=8)
    # shiny highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([480, 190, 660, 320], fill=(255, 255, 255, 110))
    ImageDraw.Draw(hi).ellipse([720, 400, 800, 470], fill=(255, 255, 255, 50))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 640, 360, 1.55)
    return img.convert("RGB")


def make_red_blob():
    img = make_card((210, 90, 90), (255, 244, 242), (255, 228, 222))
    img = soft_ellipse_shadow(img, [340, 530, 940, 600], blur=14, alpha=45)
    # irregular paint blob via overlapping ellipses + drip
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # main blob
    blobs = [
        (420, 200, 860, 520, (230, 50, 50)),
        (380, 280, 560, 480, (210, 40, 40)),
        (740, 240, 920, 460, (240, 70, 60)),
        (560, 160, 760, 300, (255, 90, 80)),
        # drips
        (500, 480, 560, 600, (200, 35, 35)),
        (680, 470, 750, 610, (220, 45, 40)),
        (600, 500, 650, 580, (210, 40, 40)),
    ]
    for x0, y0, x1, y1, c in blobs:
        ld.ellipse([x0, y0, x1, y1], fill=c + (255,))
    # soft edge
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    # re-sharpen core a bit
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for x0, y0, x1, y1, c in blobs[:4]:
        cd.ellipse([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=c + (230,))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    img = Image.alpha_composite(img, core)
    # highlight sheen
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([500, 220, 680, 340], fill=(255, 255, 255, 80))
    img = Image.alpha_composite(img, hi)
    # tiny face on blob optional — skip for pure color target clarity
    return img.convert("RGB")


def make_blue_fish():
    img = make_card((70, 130, 190), (232, 244, 255), (210, 230, 250))
    img = soft_ellipse_shadow(img, [360, 520, 920, 580], blur=14, alpha=50)
    # body
    body = [300, 220, 860, 500]
    img = paint_ellipse_grad(img, body, (120, 190, 255), (40, 110, 210), outline=(20, 70, 150), ow=7)
    d = ImageDraw.Draw(img)
    # tail
    tail = [(860, 360), (1040, 220), (1000, 360), (1040, 500)]
    d.polygon(tail, fill=(50, 120, 220), outline=(20, 70, 150))
    for i in range(len(tail)):
        d.line([tail[i], tail[(i + 1) % len(tail)]], fill=(20, 70, 150), width=5)
    # fins
    d.polygon([(560, 220), (640, 140), (700, 230)], fill=(80, 150, 235), outline=(20, 70, 150))
    d.polygon([(560, 500), (640, 580), (700, 490)], fill=(80, 150, 235), outline=(20, 70, 150))
    # eye
    d.ellipse([400, 300, 480, 380], fill=(255, 255, 255), outline=(20, 70, 150), width=4)
    d.ellipse([420, 320, 460, 360], fill=(26, 26, 40))
    d.ellipse([428, 326, 442, 340], fill=(255, 255, 255))
    # smile
    d.arc([340, 360, 460, 440], start=20, end=160, fill=(20, 70, 150), width=5)
    # scales hint
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    for sx in range(520, 800, 40):
        for sy in range(280, 440, 36):
            hd.arc([sx, sy, sx + 36, sy + 28], start=200, end=340, fill=(255, 255, 255, 55), width=3)
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    return img.convert("RGB")


def make_blue_blob():
    img = make_card((70, 130, 190), (236, 246, 255), (214, 232, 252))
    img = soft_ellipse_shadow(img, [340, 530, 940, 600], blur=14, alpha=45)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    blobs = [
        (420, 200, 860, 520, (50, 120, 230)),
        (380, 280, 560, 480, (40, 100, 210)),
        (740, 240, 920, 460, (70, 150, 245)),
        (560, 160, 760, 300, (90, 170, 255)),
        (500, 480, 560, 600, (35, 95, 200)),
        (680, 470, 750, 610, (45, 115, 220)),
        (600, 500, 650, 580, (40, 105, 210)),
    ]
    for x0, y0, x1, y1, c in blobs:
        ld.ellipse([x0, y0, x1, y1], fill=c + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for x0, y0, x1, y1, c in blobs[:4]:
        cd.ellipse([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=c + (230,))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    img = Image.alpha_composite(img, core)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([500, 220, 680, 340], fill=(255, 255, 255, 80))
    img = Image.alpha_composite(img, hi)
    return img.convert("RGB")


def make_yellow_sun():
    img = make_card((220, 180, 60), (255, 252, 230), (255, 244, 190))
    # rays
    d = ImageDraw.Draw(img)
    cx, cy = 640, 360
    for i in range(12):
        ang = i * math.pi / 6
        x0 = cx + 200 * math.cos(ang)
        y0 = cy + 200 * math.sin(ang)
        x1 = cx + 310 * math.cos(ang)
        y1 = cy + 310 * math.sin(ang)
        # thick ray as rounded line via ellipse at ends
        d.line([(x0, y0), (x1, y1)], fill=(255, 200, 40), width=28)
        d.ellipse([x1 - 16, y1 - 16, x1 + 16, y1 + 16], fill=(255, 190, 30))
    img = soft_ellipse_shadow(img, [400, 520, 880, 580], blur=14, alpha=45)
    bbox = [400, 160, 880, 560]
    img = paint_ellipse_grad(img, bbox, (255, 240, 120), (255, 190, 40), outline=(200, 140, 10), ow=8)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([480, 210, 680, 340], fill=(255, 255, 255, 100))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 640, 370, 1.55)
    return img.convert("RGB")


def make_yellow_blob():
    img = make_card((220, 180, 60), (255, 252, 232), (255, 246, 200))
    img = soft_ellipse_shadow(img, [340, 530, 940, 600], blur=14, alpha=45)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    blobs = [
        (420, 200, 860, 520, (250, 200, 40)),
        (380, 280, 560, 480, (240, 180, 20)),
        (740, 240, 920, 460, (255, 220, 60)),
        (560, 160, 760, 300, (255, 230, 90)),
        (500, 480, 560, 600, (230, 170, 15)),
        (680, 470, 750, 610, (245, 190, 30)),
        (600, 500, 650, 580, (235, 175, 20)),
    ]
    for x0, y0, x1, y1, c in blobs:
        ld.ellipse([x0, y0, x1, y1], fill=c + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for x0, y0, x1, y1, c in blobs[:4]:
        cd.ellipse([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=c + (230,))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    img = Image.alpha_composite(img, core)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([500, 220, 680, 340], fill=(255, 255, 255, 90))
    img = Image.alpha_composite(img, hi)
    return img.convert("RGB")


def make_green_leaf():
    img = make_card((80, 160, 100), (236, 250, 238), (210, 240, 215))
    img = soft_ellipse_shadow(img, [360, 540, 920, 600], blur=14, alpha=50)
    # leaf as rotated ellipse-ish polygon + stem
    # main leaf body: pointed oval via polygon
    cx, cy = 640, 340
    pts = []
    for i in range(36):
        ang = -math.pi / 2 + i * 2 * math.pi / 36
        # pointed tip top/bottom, wider mid — classic leaf
        rx = 160 + 40 * abs(math.sin(ang))
        ry = 240
        # skew for leaf angle
        x = cx + rx * math.cos(ang) * 0.95 + 40 * math.sin(ang)
        y = cy + ry * math.sin(ang)
        pts.append((x, y))
    img = paint_polygon_grad(img, pts, (140, 220, 110), (40, 150, 70), outline=(25, 110, 50), ow=7)
    d = ImageDraw.Draw(img)
    # stem
    d.line([(640, 560), (640, 620)], fill=(100, 70, 40), width=14)
    d.ellipse([628, 610, 652, 640], fill=(100, 70, 40))
    # center vein
    d.line([(640, 140), (640, 560)], fill=(30, 120, 55), width=5)
    # side veins
    for t in (0.25, 0.4, 0.55, 0.7):
        y = 140 + t * 420
        spread = 80 + t * 40
        d.line([(640, y), (640 - spread, y + 40)], fill=(30, 120, 55), width=3)
        d.line([(640, y), (640 + spread, y + 40)], fill=(30, 120, 55), width=3)
    # face
    draw_face(d, 640, 340, 1.35)
    # highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([500, 200, 620, 340], fill=(255, 255, 255, 70))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    return img.convert("RGB")


def make_green_blob():
    img = make_card((80, 160, 100), (238, 250, 240), (214, 242, 218))
    img = soft_ellipse_shadow(img, [340, 530, 940, 600], blur=14, alpha=45)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    blobs = [
        (420, 200, 860, 520, (50, 170, 80)),
        (380, 280, 560, 480, (40, 150, 65)),
        (740, 240, 920, 460, (70, 200, 100)),
        (560, 160, 760, 300, (90, 210, 120)),
        (500, 480, 560, 600, (35, 140, 60)),
        (680, 470, 750, 610, (45, 160, 75)),
        (600, 500, 650, 580, (40, 150, 65)),
    ]
    for x0, y0, x1, y1, c in blobs:
        ld.ellipse([x0, y0, x1, y1], fill=c + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for x0, y0, x1, y1, c in blobs[:4]:
        cd.ellipse([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=c + (230,))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    img = Image.alpha_composite(img, core)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([500, 220, 680, 340], fill=(255, 255, 255, 80))
    img = Image.alpha_composite(img, hi)
    return img.convert("RGB")


def save(name, img):
    path = OUT / name
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path} {img.size}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # shapes
    save("shape_circle.png", make_shape_circle())
    save("outline_circle.png", make_outline_circle())
    save("shape_square.png", make_shape_square())
    save("outline_square.png", make_outline_square())
    save("shape_triangle.png", make_shape_triangle())
    save("outline_triangle.png", make_outline_triangle())
    save("shape_star.png", make_shape_star())
    save("outline_star.png", make_outline_star())
    # colors
    save("color_red_ball.png", make_red_ball())
    save("color_red_blob.png", make_red_blob())
    save("color_blue_fish.png", make_blue_fish())
    save("color_blue_blob.png", make_blue_blob())
    save("color_yellow_sun.png", make_yellow_sun())
    save("color_yellow_blob.png", make_yellow_blob())
    save("color_green_leaf.png", make_green_leaf())
    save("color_green_blob.png", make_green_blob())
    print("done")


if __name__ == "__main__":
    main()
