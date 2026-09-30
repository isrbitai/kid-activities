#!/usr/bin/env python3
"""Bake recognizable animal silhouettes for the צלליות quiz.

Choice cards are full-color illustrations on a cream rounded card. A color
threshold that treats the whole card as foreground saves a solid rectangle,
which is impossible to match. This script keeps only the animal shape
(frame, page margin, and soft ground shadow removed) and paints a solid
near-black silhouette on white.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ASSETS = Path(__file__).resolve().parent.parent / "assets"
OUT_SIZE = 1024
FILL = (18, 16, 14)
# Drop specks (card-corner crumbs). Feet and other real parts stay.
MIN_COMPONENT = 700

# Duck sits on a brown perch. Orange beak and feet stay; the plank does not.
WOOD_ANIMALS = {"quiz_duck.png"}


def is_margin(c):
    return c[0] > 248 and c[1] > 248 and c[2] > 246


def creamish(c):
    r, g, b = c
    lum = (r + g + b) / 3
    sat = max(c) - min(c)
    return lum > 228 and 14 <= sat <= 58


def is_soft_shadow(r, g, b):
    """Pale gray cast shadow on the cream card, not the animal body."""
    lum = (r + g + b) / 3
    sat = max(r, g, b) - min(r, g, b)
    return sat < 16 and lum > 196


def is_wood(r, g, b):
    """Brown plank. Bright orange beak/feet are not wood."""
    lum = (r + g + b) / 3
    if b > 90:
        return False
    if r > 200 and (r - b) > 120:
        return False
    return lum < 175 and r > 60 and g < r * 0.9 and b < g + 8


def interior_box(im):
    """Crop inside the colored card frame so the frame is not part of the shape."""
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if not is_margin(px[x, y]):
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)

    def walk(start, end, step, get):
        run = 0
        i = start
        while (i - end) * step < 0:
            if creamish(get(i)):
                run += 1
                if run >= 8:
                    return i - step * 7
            else:
                run = 0
            i += step
        return start

    ymid = (miny + maxy) // 2
    xmid = (minx + maxx) // 2
    left = walk(minx, maxx, 1, lambda i: px[i, ymid])
    right = walk(maxx, minx, -1, lambda i: px[i, ymid])
    top = walk(miny, maxy, 1, lambda i: px[xmid, i])
    bottom = walk(maxy, miny, -1, lambda i: px[xmid, i])
    return (left + 6, top + 6, right - 6, bottom - 6)


def background_color(px, w, h):
    samples = []
    for cx, cy in ((12, 12), (w - 36, 12), (12, h - 36), (w - 36, h - 36)):
        for dy in range(18):
            for dx in range(18):
                samples.append(px[cx + dx, cy + dy])
    samples.sort(key=lambda c: c[0] + c[1] + c[2])
    return samples[len(samples) // 2]


def connected_components(mask):
    w, h = mask.size
    mp = mask.load()
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            if mp[x, y] < 128 or seen[y][x]:
                continue
            stack = [(x, y)]
            seen[y][x] = True
            pts = []
            minx = maxx = x
            miny = maxy = y
            while stack:
                cx, cy = stack.pop()
                pts.append((cx, cy))
                if cx < minx:
                    minx = cx
                if cx > maxx:
                    maxx = cx
                if cy < miny:
                    miny = cy
                if cy > maxy:
                    maxy = cy
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and mp[nx, ny] >= 128:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            comps.append((pts, (minx, miny, maxx, maxy)))
    comps.sort(key=lambda c: len(c[0]), reverse=True)
    return comps


def animal_mask(src_name, thr=32, close=5):
    im = Image.open(ASSETS / src_name).convert("RGB")
    box = interior_box(im)
    crop = im.crop(box)
    w, h = crop.size
    px = crop.load()
    bg = background_color(px, w, h)
    drop_wood = src_name in WOOD_ANIMALS

    ink = Image.new("L", (w, h), 0)
    ip = ink.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if is_soft_shadow(r, g, b):
                continue
            if drop_wood and is_wood(r, g, b):
                continue
            dist = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if dist > thr:
                ip[x, y] = 255

    k = close if close % 2 else close + 1
    closed = ink.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(max(3, k - 2)))
    ff = closed.copy()
    draw = ImageDraw.Draw(ff)
    draw.rectangle([0, 0, w - 1, 2], fill=0)
    draw.rectangle([0, h - 3, w - 1, h - 1], fill=0)
    draw.rectangle([0, 0, 2, h - 1], fill=0)
    draw.rectangle([w - 3, 0, w - 1, h - 1], fill=0)
    ImageDraw.floodfill(ff, (1, 1), 128)

    sil = Image.new("L", (w, h), 0)
    sp = sil.load()
    fp = ff.load()
    for y in range(h):
        for x in range(w):
            if fp[x, y] != 128:
                sp[x, y] = 255

    comps = connected_components(sil)
    if not comps:
        raise SystemExit(f"{src_name}: no animal pixels found")
    largest = len(comps[0][0])
    keep = Image.new("L", (w, h), 0)
    kp = keep.load()
    kept_area = 0
    for pts, _bbox in comps:
        area = len(pts)
        if area < MIN_COMPONENT and area < largest * 0.008:
            continue
        kept_area += area
        for x, y in pts:
            kp[x, y] = 255

    # Smooth jaggies without eating ears, beak, or ossicones.
    keep = keep.filter(ImageFilter.GaussianBlur(1.15))
    keep = keep.point(lambda p: 255 if p > 128 else 0)
    return keep, kept_area, bg


def render_square(mask):
    bbox = mask.getbbox()
    if not bbox:
        raise SystemExit("empty silhouette")
    cropped = mask.crop(bbox)
    bw, bh = cropped.size
    pad = int(max(bw, bh) * 0.12)
    side = max(bw, bh) + pad * 2
    square = Image.new("L", (side, side), 0)
    square.paste(cropped, ((side - bw) // 2, (side - bh) // 2))
    margin = int(OUT_SIZE * 0.06)
    fitted = square.resize((OUT_SIZE - margin * 2, OUT_SIZE - margin * 2), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (OUT_SIZE, OUT_SIZE), (255, 255, 255))
    dark = Image.new("RGB", fitted.size, FILL)
    canvas.paste(dark, (margin, margin), fitted)
    return canvas


def assert_recognizable(mask, src_name):
    """A filled card is almost a solid rectangle. An animal is not."""
    bbox = mask.getbbox()
    if not bbox:
        raise SystemExit(f"{src_name}: empty mask")
    w, h = mask.size
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    area = 0
    px = mask.load()
    for y in range(bbox[1], bbox[3], 2):
        for x in range(bbox[0], bbox[2], 2):
            if px[x, y] > 128:
                area += 1
    area *= 4
    solidity = area / float(bw * bh)
    covers = (bw * bh) / float(w * h)
    if covers > 0.82 and solidity > 0.9:
        raise SystemExit(
            f"{src_name}: silhouette looks like a filled rectangle "
            f"(covers={covers:.2f} solidity={solidity:.2f})"
        )
    if solidity < 0.18:
        raise SystemExit(f"{src_name}: silhouette too sparse (solidity={solidity:.2f})")
    print(f"  {src_name}: solidity={solidity:.2f} covers={covers:.2f} bbox={bw}x{bh}")


def write_silhouette(src_name, dst_name, **kwargs):
    mask, _area, bg = animal_mask(src_name, **kwargs)
    assert_recognizable(mask, src_name)
    out = render_square(mask)
    path = ASSETS / dst_name
    out.save(path, "PNG", optimize=True)
    print(f"wrote {dst_name} from {src_name} bg={bg}")


def main():
    # close=5 seals thin outline gaps (white rabbit) without merging the ground.
    jobs = [
        ("quiz_elephant.png", "quiz_elephant_sil.png", {}),
        ("quiz_rabbit.png", "quiz_rabbit_sil.png", {"close": 7}),
        ("quiz_giraffe.png", "quiz_giraffe_sil.png", {}),
        ("quiz_duck.png", "quiz_duck_sil.png", {}),
        ("quiz_turtle.png", "quiz_turtle_sil.png", {}),
    ]
    for src, dst, kwargs in jobs:
        write_silhouette(src, dst, **kwargs)
    print("done")


if __name__ == "__main__":
    main()
