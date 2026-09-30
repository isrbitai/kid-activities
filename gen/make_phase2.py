#!/usr/bin/env python3
"""Phase 2 assets: same/different, visual closure, happy/sad faces.

Closure scenes are illustrated sources in gen/src/phase2/. A large obvious
part (door, head, tail, wheel) is lifted out so the gap and the piece match.
Blue ball and blue star reuse the preschool card drawing from make_shapes_colors.
"""
import importlib.util
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
SRC = Path(__file__).resolve().parent / "src" / "phase2"
W, H = 1280, 720

spec = importlib.util.spec_from_file_location(
    "shapes", Path(__file__).resolve().parent / "make_shapes_colors.py"
)
shapes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shapes)


def save(name, img):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    print(f"wrote {path.name} {img.size}")


def make_blue_ball():
    img = shapes.make_card((70, 120, 190), (232, 244, 255), (210, 230, 250))
    img = shapes.soft_ellipse_shadow(img, [380, 520, 900, 580], blur=14, alpha=50)
    bbox = [380, 140, 900, 560]
    img = shapes.paint_ellipse_grad(
        img, bbox, (120, 190, 255), (40, 110, 210), outline=(20, 70, 150), ow=8
    )
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([480, 190, 660, 320], fill=(255, 255, 255, 110))
    ImageDraw.Draw(hi).ellipse([720, 400, 800, 470], fill=(255, 255, 255, 50))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    shapes.draw_face(ImageDraw.Draw(img), 640, 360, 1.55)
    return img.convert("RGB")


def make_blue_star():
    img = shapes.make_card((70, 120, 190), (232, 244, 255), (210, 230, 250))
    img = shapes.soft_ellipse_shadow(img, [360, 530, 920, 590], blur=14, alpha=50)
    pts = shapes.star_points(640, 360, 250, 105)
    img = shapes.paint_polygon_grad(
        img, pts, (120, 190, 255), (36, 110, 210), outline=(20, 70, 150), ow=7
    )
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).ellipse([560, 280, 720, 400], fill=(255, 255, 255, 75))
    img = Image.alpha_composite(img.convert("RGBA"), hi)
    shapes.draw_face(ImageDraw.Draw(img), 640, 360, 1.35)
    return img.convert("RGB")


def face_card(filename, border, bg, bg2):
    card = shapes.make_card(border, bg, bg2)
    face = Image.open(SRC / filename).convert("RGBA")
    inner = 620
    face.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    mask = Image.new("L", face.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, face.size[0] - 1, face.size[1] - 1], radius=48, fill=255)
    x = (W - face.size[0]) // 2
    y = (H - face.size[1]) // 2 - 4
    card.paste(face, (x, y), mask)
    return card


def flood(im, seed, tol):
    w, h = im.size
    px = im.load()
    sr, sg, sb = [int(v) for v in px[seed]]
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    stack = [seed]
    seen = bytearray(w * h)
    seen[seed[1] * w + seed[0]] = 1
    while stack:
        x, y = stack.pop()
        r, g, b = px[x, y]
        if abs(int(r) - sr) + abs(int(g) - sg) + abs(int(b) - sb) > tol:
            continue
        mp[x, y] = 255
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                seen[ny * w + nx] = 1
                stack.append((nx, ny))
    return mask


def warm_right(im, x_min):
    w, h = im.size
    px = im.load()
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for y in range(h):
        for x in range(x_min, w):
            r, g, b = [int(v) for v in px[x, y]]
            cream = r > 230 and g > 210 and b > 180
            if r > 150 and r > b + 40 and g < 230 and not cream:
                mp[x, y] = 255
    return mask


def circle_mask(size, box):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    return mask


def soften(mask, grow=9):
    m = mask.filter(ImageFilter.MaxFilter(grow))
    return m.filter(ImageFilter.GaussianBlur(0.8)).point(lambda v: 255 if v > 48 else 0)


def dashed_rect(draw, box, color, width=7, dash=16, gap=12):
    x0, y0, x1, y1 = box
    step = dash + gap
    x = x0
    while x < x1:
        draw.line([(x, y0), (min(x + dash, x1), y0)], fill=color, width=width)
        draw.line([(x, y1), (min(x + dash, x1), y1)], fill=color, width=width)
        x += step
    y = y0
    while y < y1:
        draw.line([(x0, y), (x0, min(y + dash, y1))], fill=color, width=width)
        draw.line([(x1, y), (x1, min(y + dash, y1))], fill=color, width=width)
        y += step


def dashed_ellipse(draw, box, color, width=7, on=10, off=7):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    steps = 200
    pts = []
    for i in range(steps):
        a = -math.pi / 2 + 2 * math.pi * i / steps
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    drawing = True
    run = 0
    limit = on
    for i in range(steps):
        if drawing:
            draw.line([pts[i], pts[(i + 1) % steps]], fill=color, width=width)
        run += 1
        if run >= limit:
            drawing = not drawing
            run = 0
            limit = on if drawing else off


def piece_card(im, mask, border, bg, bg2):
    bb = mask.getbbox()
    crop = im.crop(bb).convert("RGBA")
    cm = mask.crop(bb)
    cut = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    cut.paste(crop, mask=cm)
    card = shapes.make_card(border, bg, bg2)
    inner_w, inner_h = 1040, 560
    cut.thumbnail((inner_w, inner_h), Image.Resampling.LANCZOS)
    x = (W - cut.size[0]) // 2
    y = (H - cut.size[1]) // 2
    card.paste(cut, (x, y), cut)
    return card


def closure(name, im, mask, fill, border, bg, bg2, outline="rect"):
    im = im.convert("RGB")
    mask = soften(mask)
    scene = im.copy()
    scene.paste(Image.new("RGB", im.size, fill), mask=mask)
    draw = ImageDraw.Draw(scene)
    bb = mask.getbbox()
    pad = 10
    box = [bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad]
    if outline == "ellipse":
        dashed_ellipse(draw, box, (46, 130, 86), width=8)
    else:
        dashed_rect(draw, box, (46, 130, 86), width=8)
    save(f"close_{name}.png", im)
    save(f"close_{name}_gap.png", scene)
    save(f"close_{name}_piece.png", piece_card(im, mask, border, bg, bg2))
    print(
        f"  gap {name}: left {box[0]/W:.3f} top {box[1]/H:.3f} "
        f"w {(box[2]-box[0])/W:.3f} h {(box[3]-box[1])/H:.3f}"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    save("sd_ball_blue.png", make_blue_ball())
    save("sd_star_blue.png", make_blue_star())
    save("sd_apple_green.png", Image.open(SRC / "phase2_apple_green.jpg"))
    save("sd_duck.png", Image.open(SRC / "phase2_duck.jpg"))
    save("sd_duck_bow.png", Image.open(SRC / "phase2_duck_bow.jpg"))
    save("emo_happy.png", face_card("phase2_face_happy.jpg", (210, 150, 70), (255, 248, 230), (255, 236, 200)))
    save("emo_sad.png", face_card("phase2_face_sad.jpg", (90, 130, 180), (232, 242, 255), (214, 228, 248)))

    house = Image.open(SRC / "phase2_house.jpg").convert("RGB")
    closure(
        "house",
        house,
        flood(house, (693, 500), 80),
        (255, 236, 214),
        (180, 70, 60),
        (255, 244, 238),
        (255, 228, 220),
    )

    cat = Image.open(SRC / "phase2_cat_full.jpg").convert("RGB")
    closure(
        "cat",
        cat,
        flood(cat, (680, 180), 110),
        (255, 248, 236),
        (210, 140, 60),
        (255, 246, 232),
        (255, 232, 206),
    )

    bird = Image.open(SRC / "phase2_bird_tail.jpg").convert("RGB")
    closure(
        "bird",
        bird,
        warm_right(bird, 740),
        (255, 245, 220),
        (190, 90, 50),
        (255, 246, 236),
        (255, 230, 210),
    )

    car = Image.open(SRC / "phase2_car.jpg").convert("RGB")
    # Front (left) wheel: dark tire bbox measured from the illustration.
    closure(
        "car",
        car,
        circle_mask(car.size, [351, 367, 562, 578]),
        (250, 232, 205),
        (70, 70, 80),
        (244, 244, 246),
        (228, 228, 232),
        outline="ellipse",
    )
    print("done")


if __name__ == "__main__":
    main()
