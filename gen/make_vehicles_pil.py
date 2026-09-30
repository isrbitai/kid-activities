#!/usr/bin/env python3
"""High-quality preschool vehicle cards via Pillow — soft pastel, thick borders, friendly faces."""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pathlib import Path
import math

OUT = Path("/workspace/animal-match/assets")
W, H = 656, 376
RX = 48
BORDER = 14
MARGIN = 8


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=255)
    return m


def make_card(border_rgb, bg_rgb, bg2_rgb=None):
    """White canvas + soft card shadow + thick border + pastel fill with subtle grain."""
    bg2 = bg2_rgb or bg_rgb
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # soft drop shadow under card
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([MARGIN+2, MARGIN+5, W-MARGIN-1, H-MARGIN+2], radius=RX, fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # outer border
    draw.rounded_rectangle([MARGIN, MARGIN, W-MARGIN-1, H-MARGIN-1], radius=RX, fill=border_rgb)

    # inner pastel with vertical soft gradient
    inner = [
        MARGIN + BORDER,
        MARGIN + BORDER,
        W - MARGIN - BORDER - 1,
        H - MARGIN - BORDER - 1,
    ]
    ir = RX - 10
    # paint gradient into a temp then mask
    grad = Image.new("RGB", (W, H), bg_rgb)
    gd = ImageDraw.Draw(grad)
    ih = inner[3] - inner[1]
    for y in range(inner[1], inner[3] + 1):
        t = (y - inner[1]) / max(ih, 1)
        r = int(bg_rgb[0] * (1 - t) + bg2[0] * t)
        g = int(bg_rgb[1] * (1 - t) + bg2[1] * t)
        b = int(bg_rgb[2] * (1 - t) + bg2[2] * t)
        gd.line([(inner[0], y), (inner[2], y)], fill=(r, g, b))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(inner, radius=ir, fill=255)
    img.paste(grad, (0, 0), mask)

    # subtle film grain
    import random
    rng = random.Random(42)
    px = img.load()
    for _ in range(8000):
        x = rng.randint(inner[0]+2, inner[2]-2)
        y = rng.randint(inner[1]+2, inner[3]-2)
        # only if inside roughly
        c = px[x, y]
        n = rng.randint(-6, 6)
        px[x, y] = (max(0, min(255, c[0]+n)), max(0, min(255, c[1]+n)), max(0, min(255, c[2]+n)))

    return img


def soft_ellipse_shadow(img, bbox, blur=8, alpha=50):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(bbox, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def draw_face(draw, cx, cy, scale=1.0):
    e = int(9 * scale)
    gap = int(22 * scale)
    # eyes
    draw.ellipse([cx - gap//2 - e, cy - e, cx - gap//2 + e, cy + e], fill=(26, 26, 26))
    draw.ellipse([cx + gap//2 - e, cy - e, cx + gap//2 + e, cy + e], fill=(26, 26, 26))
    # highlights
    h = max(2, int(3 * scale))
    draw.ellipse([cx - gap//2 - e + int(2*scale), cy - e + int(2*scale),
                  cx - gap//2 - e + int(2*scale) + h*2, cy - e + int(2*scale) + h*2], fill=(255, 255, 255))
    draw.ellipse([cx + gap//2 - e + int(2*scale), cy - e + int(2*scale),
                  cx + gap//2 - e + int(2*scale) + h*2, cy - e + int(2*scale) + h*2], fill=(255, 255, 255))
    # smile
    sw = int(2.8 * scale)
    bbox = [cx - int(12*scale), cy + int(4*scale), cx + int(12*scale), cy + int(22*scale)]
    draw.arc(bbox, start=20, end=160, fill=(26, 26, 26), width=sw)


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def lerp(a, b, t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))


def paint_vertical_roundrect(img, xy, radius, c_top, c_bot, outline=None, ow=3):
    """Fill rounded rect with vertical gradient."""
    x0, y0, x1, y1 = xy
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    # full gradient rect then mask
    grad = Image.new("RGB", (x1-x0+1, y1-y0+1))
    gd = ImageDraw.Draw(grad)
    h = y1 - y0
    for y in range(h+1):
        t = y / max(h, 1)
        gd.line([(0, y), (x1-x0, y)], fill=lerp(c_top, c_bot, t))
    mask = Image.new("L", (x1-x0+1, y1-y0+1), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, x1-x0, y1-y0], radius=radius, fill=255)
    layer.paste(grad, (x0, y0), mask)
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    if outline:
        d = ImageDraw.Draw(out)
        d.rounded_rectangle(xy, radius=radius, outline=outline, width=ow)
    return out


def paint_ellipse_grad(img, bbox, c_top, c_bot, outline=None, ow=3):
    x0, y0, x1, y1 = bbox
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    grad = Image.new("RGB", (x1-x0+1, y1-y0+1))
    gd = ImageDraw.Draw(grad)
    h = y1 - y0
    for y in range(h+1):
        t = y / max(h, 1)
        gd.line([(0, y), (x1-x0, y)], fill=lerp(c_top, c_bot, t))
    mask = Image.new("L", (x1-x0+1, y1-y0+1), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, x1-x0, y1-y0], fill=255)
    layer.paste(grad, (x0, y0), mask)
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    if outline:
        d = ImageDraw.Draw(out)
        d.ellipse(bbox, outline=outline, width=ow)
    return out


# ---------- Individual cards ----------

def make_car():
    img = make_card((224, 122, 95), (255, 246, 238), (255, 232, 214))
    img = soft_ellipse_shadow(img, [168, 292, 488, 318], blur=6, alpha=45)
    # cabin
    img = paint_vertical_roundrect(img, [210, 128, 430, 200], 22,
                                   (255, 138, 122), (232, 69, 60), outline=(184, 50, 42), ow=4)
    d = ImageDraw.Draw(img)
    # windows
    for wx in (230, 320):
        img = paint_vertical_roundrect(img, [wx, 142, wx+70, 186], 10,
                                       (214, 240, 255), (126, 200, 232), outline=(91, 163, 196), ow=2)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([wx+6, 148, wx+22, 176], radius=5, fill=(255, 255, 255, ))
        # paste white highlight with opacity via layer
    # highlight overlays
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.rounded_rectangle([236, 148, 252, 176], radius=5, fill=(255, 255, 255, 140))
    hd.rounded_rectangle([326, 148, 342, 176], radius=5, fill=(255, 255, 255, 140))
    img = Image.alpha_composite(img.convert("RGBA"), hi)

    # body
    img = paint_vertical_roundrect(img, [145, 190, 515, 288], 38,
                                   (255, 107, 90), (201, 42, 42), outline=(166, 30, 30), ow=4)
    # body highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.arc([170, 198, 490, 240], start=200, end=340, fill=(255, 255, 255, 80), width=10)
    img = Image.alpha_composite(img, hi)

    d = ImageDraw.Draw(img)
    # headlights
    for hx in (155, 500):
        d.ellipse([hx-16, 218, hx+16, 254], fill=(255, 229, 102), outline=(224, 184, 0), width=3)
        d.ellipse([hx-8, 224, hx, 236], fill=(255, 255, 255))
    # wheels
    for wx in (230, 430):
        d.ellipse([wx-32, 258, wx+32, 322], fill=(45, 45, 50), outline=(26, 26, 30), width=3)
        d.ellipse([wx-16, 274, wx+16, 306], fill=(138, 138, 150))
        d.ellipse([wx-7, 283, wx+7, 297], fill=(200, 200, 208))
    draw_face(d, 328, 235, 1.05)
    return img.convert("RGB")


def make_garage():
    img = make_card((196, 164, 132), (255, 248, 240), (245, 230, 211))
    img = soft_ellipse_shadow(img, [178, 300, 478, 324], blur=6, alpha=40)
    d = ImageDraw.Draw(img)
    # roof triangle with fill via polygon + overlay shade
    roof = [(160, 155), (328, 90), (496, 155)]
    d.polygon(roof, fill=(232, 93, 76), outline=(155, 44, 31))
    # thicker roof outline
    d.line(roof + [roof[0]], fill=(155, 44, 31), width=4)
    # roof highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.line([(210, 145), (328, 105), (380, 125)], fill=(255, 255, 255, 90), width=6)
    img = Image.alpha_composite(img.convert("RGBA"), hi)

    img = paint_vertical_roundrect(img, [180, 148, 476, 305], 8,
                                   (255, 245, 230), (232, 213, 184), outline=(196, 164, 132), ow=3)
    img = paint_vertical_roundrect(img, [230, 185, 426, 305], 6,
                                   (107, 140, 174), (61, 90, 122), outline=(44, 62, 80), ow=3)
    d = ImageDraw.Draw(img)
    # door panels
    d.line([(328, 190), (328, 300)], fill=(44, 62, 80), width=2)
    d.line([(235, 225), (421, 225)], fill=(44, 62, 80), width=2)
    d.line([(235, 260), (421, 260)], fill=(44, 62, 80), width=2)
    d.ellipse([393, 238, 407, 252], fill=(244, 211, 94), outline=(201, 162, 39), width=2)
    # foundation
    d.rounded_rectangle([165, 300, 491, 318], radius=4, fill=(184, 184, 192), outline=(138, 138, 150), width=2)
    # little window
    d.rounded_rectangle([300, 158, 356, 176], radius=4, fill=(168, 216, 234), outline=(91, 163, 196), width=2)
    return img.convert("RGB")


def make_boat():
    img = make_card((74, 144, 164), (240, 250, 252), (214, 240, 245))
    # waves
    wave = Image.new("RGBA", img.size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave)
    # layered wave shapes
    pts = []
    for x in range(70, 590, 4):
        y = 300 + int(12 * math.sin((x - 70) / 40.0))
        pts.append((x, y))
    pts += [(580, 340), (70, 340)]
    wd.polygon(pts, fill=(78, 168, 200, 150))
    pts2 = []
    for x in range(80, 580, 4):
        y = 318 + int(10 * math.sin((x - 80) / 35.0 + 1))
        pts2.append((x, y))
    pts2 += [(570, 345), (80, 345)]
    wd.polygon(pts2, fill=(74, 155, 196, 120))
    img = Image.alpha_composite(img.convert("RGBA"), wave)

    d = ImageDraw.Draw(img)
    # mast
    d.rounded_rectangle([318, 85, 328, 255], radius=4, fill=(166, 124, 82), outline=(122, 86, 53), width=2)
    # sail
    sail = [(328, 95), (328, 230), (460, 230)]
    d.polygon(sail, fill=(255, 229, 102), outline=(212, 160, 23))
    d.line(sail + [sail[0]], fill=(212, 160, 23), width=3)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.polygon([(335, 115), (335, 215), (420, 215)], fill=(255, 255, 255, 90))
    img = Image.alpha_composite(img, hi)

    # cabin
    img = paint_vertical_roundrect(img, [250, 198, 320, 250], 10,
                                   (255, 248, 240), (240, 220, 200), outline=(196, 164, 132), ow=3)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([262, 210, 308, 238], radius=6, fill=(168, 216, 234), outline=(91, 163, 196), width=2)

    # hull as polygon with gradient approx
    hull = Image.new("RGBA", img.size, (0, 0, 0, 0))
    # draw hull on temp then color
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    hull_pts = [(145, 250), (200, 250), (230, 310), (440, 310), (500, 250), (455, 250)]
    md.polygon(hull_pts, fill=255)
    # gradient fill for hull
    grad = Image.new("RGB", img.size)
    gd = ImageDraw.Draw(grad)
    for y in range(250, 311):
        t = (y - 250) / 60
        gd.line([(0, y), (W, y)], fill=lerp((91, 184, 212), (46, 122, 154), t))
    hull.paste(grad, (0, 0), mask)
    img = Image.alpha_composite(img.convert("RGBA"), hull)
    d = ImageDraw.Draw(img)
    d.line(hull_pts + [hull_pts[0]], fill=(30, 90, 114), width=4)
    # highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.line([(200, 262), (450, 262)], fill=(255, 255, 255, 70), width=8)
    img = Image.alpha_composite(img, hi)
    d = ImageDraw.Draw(img)
    draw_face(d, 320, 275, 0.95)
    return img.convert("RGB")


def make_water():
    img = make_card((61, 139, 156), (232, 247, 250), (200, 235, 242))
    img = soft_ellipse_shadow(img, [120, 280, 536, 320], blur=8, alpha=35)
    # pond
    img = paint_ellipse_grad(img, [118, 90, 538, 310], (126, 214, 232), (42, 122, 148),
                             outline=(30, 90, 114), ow=5)
    # shine
    shine = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    sd.ellipse([160, 110, 360, 200], fill=(255, 255, 255, 70))
    shine = shine.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img.convert("RGBA"), shine)
    # wave lines
    d = ImageDraw.Draw(img)
    for amp, y0, op in [(14, 185, 100), (10, 220, 70)]:
        pts = []
        for x in range(170, 500, 3):
            y = y0 + int(amp * math.sin((x - 170) / 45.0))
            pts.append((x, y))
        # draw as thick polyline segments
        hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hi)
        hd.line(pts, fill=(255, 255, 255, op), width=5, joint="curve")
        img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    # sparkles
    for cx, cy, r in [(240, 155, 6), (420, 160, 4), (360, 240, 5)]:
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255))
    # droplets
    d.ellipse([157, 104, 193, 156], fill=(91, 184, 212), outline=(46, 122, 154), width=2)
    d.ellipse([466, 105, 494, 145], fill=(126, 214, 232), outline=(46, 122, 154), width=2)
    d.ellipse([165, 112, 175, 126], fill=(255, 255, 255))
    return img.convert("RGB")


def make_plane():
    img = make_card((91, 141, 239), (242, 247, 255), (220, 233, 255))
    img = soft_ellipse_shadow(img, [170, 290, 510, 318], blur=6, alpha=40)
    # fuselage
    img = paint_ellipse_grad(img, [135, 145, 525, 255], (168, 212, 255), (61, 127, 212),
                             outline=(42, 90, 154), ow=4)
    # highlight
    shine = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    sd.ellipse([180, 155, 420, 195], fill=(255, 255, 255, 80))
    shine = shine.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), shine)

    d = ImageDraw.Draw(img)
    # nose
    d.ellipse([490, 168, 546, 232], fill=(200, 223, 245), outline=(42, 90, 154), width=3)
    d.ellipse([512, 180, 528, 200], fill=(255, 255, 255))
    # windows
    for wx in (250, 290, 330, 370, 410):
        d.ellipse([wx-12, 174, wx+12, 206], fill=(214, 240, 255), outline=(61, 127, 212), width=2)
    # wing
    wing = [(240, 215), (340, 198), (440, 215), (400, 258), (280, 258)]
    d.polygon(wing, fill=(74, 111, 191), outline=(30, 53, 96))
    d.line(wing + [wing[0]], fill=(30, 53, 96), width=3)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.line([(300, 218), (380, 218)], fill=(255, 255, 255, 55), width=5)
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    # tail
    d.polygon([(145, 150), (175, 200), (145, 210)], fill=(232, 93, 76), outline=(155, 44, 31))
    d.polygon([(145, 200), (175, 200), (160, 230)], fill=(232, 93, 76), outline=(155, 44, 31))
    d.line([(145, 150), (175, 200), (145, 210), (145, 150)], fill=(155, 44, 31), width=3)
    draw_face(d, 475, 200, 0.85)
    return img.convert("RGB")


def make_cloud():
    img = make_card((126, 182, 232), (245, 250, 255), (224, 240, 255))
    # stacked ellipses with soft white→blue gradient feel
    puffs = [
        (250, 210, 70, 55),
        (320, 175, 85, 70),
        (400, 205, 75, 58),
        (340, 230, 100, 55),
        (280, 225, 60, 45),
    ]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for cx, cy, rx, ry in puffs:
        # soft shadow under each
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([cx-rx+4, cy-ry+10, cx+rx+4, cy+ry+10], fill=(0, 0, 0, 25))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        layer = Image.alpha_composite(layer, sh)
        puff = Image.new("RGBA", img.size, (0, 0, 0, 0))
        # gradient ellipse
        bbox = [cx-rx, cy-ry, cx+rx, cy+ry]
        grad = Image.new("RGB", (rx*2+1, ry*2+1))
        gd = ImageDraw.Draw(grad)
        for y in range(ry*2+1):
            t = y / max(ry*2, 1)
            gd.line([(0, y), (rx*2, y)], fill=lerp((255, 255, 255), (212, 232, 250), t))
        mask = Image.new("L", (rx*2+1, ry*2+1), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, rx*2, ry*2], fill=255)
        puff.paste(grad, (cx-rx, cy-ry), mask)
        # outline
        ImageDraw.Draw(puff).ellipse(bbox, outline=(168, 200, 224), width=3)
        layer = Image.alpha_composite(layer, puff)
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    # highlights
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.ellipse([260, 145, 340, 185], fill=(255, 255, 255, 160))
    hd.ellipse([355, 170, 410, 200], fill=(255, 255, 255, 100))
    hi = hi.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, hi)
    d = ImageDraw.Draw(img)
    d.ellipse([195, 135, 205, 145], fill=(255, 229, 102))
    d.ellipse([466, 146, 474, 154], fill=(255, 229, 102))
    return img.convert("RGB")


def make_train():
    img = make_card((224, 122, 74), (255, 245, 238), (255, 228, 208))
    img = soft_ellipse_shadow(img, [140, 298, 520, 322], blur=6, alpha=40)
    # tender
    img = paint_vertical_roundrect(img, [120, 195, 215, 280], 14,
                                   (126, 184, 212), (61, 127, 170), outline=(46, 106, 138), ow=3)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([135, 210, 200, 250], radius=8, fill=(168, 216, 234), outline=(61, 127, 160), width=2)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.rounded_rectangle([142, 215, 158, 243], radius=4, fill=(255, 255, 255, 120))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([210, 230, 235, 244], radius=4, fill=(107, 107, 117), outline=(61, 61, 69), width=2)

    # engine body
    img = paint_vertical_roundrect(img, [230, 185, 460, 285], 28,
                                   (255, 107, 74), (192, 57, 43), outline=(139, 30, 20), ow=4)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.arc([250, 192, 440, 230], start=200, end=340, fill=(255, 255, 255, 75), width=9)
    img = Image.alpha_composite(img, hi)

    # cab
    img = paint_vertical_roundrect(img, [380, 128, 470, 195], 12,
                                   (255, 138, 106), (232, 69, 60), outline=(139, 30, 20), ow=3)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([395, 142, 455, 182], radius=8, fill=(168, 216, 234), outline=(61, 127, 160), width=2)
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.rounded_rectangle([402, 148, 416, 174], radius=4, fill=(255, 255, 255, 130))
    img = Image.alpha_composite(img, hi)

    d = ImageDraw.Draw(img)
    # smokestack
    d.rounded_rectangle([265, 115, 297, 190], radius=8, fill=(90, 90, 101), outline=(45, 45, 53), width=3)
    d.ellipse([259, 105, 303, 125], fill=(138, 138, 150), outline=(45, 45, 53), width=2)
    # smoke
    for cx, cy, r, a in [(275, 95, 14, 200), (295, 78, 18, 160), (318, 68, 12, 120)]:
        sm = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sm).ellipse([cx-r, cy-r, cx+r, cy+r], fill=(240, 240, 245, a))
        sm = sm.filter(ImageFilter.GaussianBlur(2))
        img = Image.alpha_composite(img.convert("RGBA"), sm)

    d = ImageDraw.Draw(img)
    # cowcatcher
    d.polygon([(460, 250), (520, 285), (460, 285)], fill=(107, 107, 117), outline=(61, 61, 69))
    d.line([(460, 250), (520, 285), (460, 285), (460, 250)], fill=(61, 61, 69), width=2)
    # wheels
    for wx, wy, r in [(280, 290, 26), (350, 290, 26), (420, 290, 26), (160, 285, 22)]:
        d.ellipse([wx-r, wy-r, wx+r, wy+r], fill=(45, 45, 50), outline=(26, 26, 30), width=3)
        d.ellipse([wx-r//2, wy-r//2, wx+r//2, wy+r//2], fill=(138, 138, 150))
    draw_face(d, 340, 230, 1.0)
    return img.convert("RGB")


def make_tracks():
    img = make_card((139, 115, 85), (255, 248, 240), (240, 230, 216))
    img = soft_ellipse_shadow(img, [100, 285, 556, 318], blur=7, alpha=30)
    d = ImageDraw.Draw(img)
    # ground hint
    ground = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ground).ellipse([98, 260, 558, 320], fill=(232, 213, 184, 110))
    ground = ground.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img.convert("RGBA"), ground)

    # ties
    for y in range(125, 275, 34):
        img = paint_vertical_roundrect(img, [110, y, 546, y+22], 5,
                                       (212, 184, 150), (139, 105, 20), outline=(107, 79, 42), ow=2)
    # rails
    for x in (175, 459):
        img = paint_vertical_roundrect(img, [x, 115, x+22, 300], 6,
                                       (192, 192, 200), (90, 90, 104), outline=(61, 61, 69), ow=2)
        hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hi)
        hd.rounded_rectangle([x+4, 120, x+10, 290], radius=2, fill=(255, 255, 255, 90))
        img = Image.alpha_composite(img.convert("RGBA"), hi)
    d = ImageDraw.Draw(img)
    # bolts
    for y in range(138, 270, 34):
        for cx in (186, 470):
            d.ellipse([cx-4, y-4, cx+4, y+4], fill=(244, 211, 94), outline=(201, 162, 39), width=2)
    return img.convert("RGB")


CARDS = {
    "car": make_car,
    "garage": make_garage,
    "boat": make_boat,
    "water": make_water,
    "plane": make_plane,
    "cloud": make_cloud,
    "train": make_train,
    "tracks": make_tracks,
}


def main():
    for name, fn in CARDS.items():
        print("Making", name, "...")
        im = fn()
        assert im.size == (W, H), im.size
        path = OUT / f"{name}.png"
        im.save(path, "PNG", optimize=True)
        print("  ->", path, path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
