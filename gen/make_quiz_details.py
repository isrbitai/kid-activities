#!/usr/bin/env python3
"""Crop zoomed animal details for visual quiz (חידון ויזואלי)."""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

def detail(src, box, dst, border_rgb, size=512):
    im = Image.open(ASSETS / src).convert("RGBA")
    crop = im.crop(box)
    w, h = crop.size
    side = max(w, h)
    bg = (252, 248, 240, 255)
    canvas = Image.new("RGBA", (side, side), bg)
    canvas.paste(crop, ((side - w) // 2, (side - h) // 2), crop)
    out = canvas.resize((size, size), Image.Resampling.LANCZOS)
    out = ImageEnhance.Sharpness(out).enhance(1.3)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 10, size - 11, size - 11], radius=56, fill=255)
    rounded = Image.new("RGBA", (size, size), bg)
    rounded.paste(out, (0, 0), mask)
    d = ImageDraw.Draw(rounded)
    d.rounded_rectangle([8, 8, size - 9, size - 9], radius=58, outline=border_rgb + (255,), width=12)
    rounded.convert("RGB").save(ASSETS / dst, "PNG", optimize=True)
    print("wrote", dst)

def sil(src, dst, fill, inset=55, border=32):
    im = Image.open(ASSETS / src).convert("RGB")
    w, h = im.size
    pts = [
        (inset, inset), (w - inset - 1, inset), (inset, h - inset - 1), (w - inset - 1, h - inset - 1),
        (w // 2, inset), (inset, h // 2), (w - inset - 1, h // 2), (w // 2, h - inset - 1),
    ]
    samples = [im.getpixel(p) for p in pts]
    pale = [s for s in samples if sum(s) / 3 > 200] or samples
    br = sorted(s[0] for s in pale)[len(pale) // 2]
    bg_g = sorted(s[1] for s in pale)[len(pale) // 2]
    bb = sorted(s[2] for s in pale)[len(pale) // 2]
    px = im.load()
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for y in range(border, h - border):
        for x in range(border, w - border):
            r, g, b = px[x, y]
            dist = abs(r - br) + abs(g - bg_g) + abs(b - bb)
            sat = max(r, g, b) - min(r, g, b)
            if dist > 48 or sat > 28 or (r + g + b) / 3 < 110:
                mp[x, y] = 255
    mask = mask.filter(ImageFilter.MedianFilter(3))
    mask = mask.filter(ImageFilter.MaxFilter(5))
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = mask.filter(ImageFilter.GaussianBlur(1.0))
    canvas = Image.new("RGB", (w, h), (252, 248, 240))
    canvas.paste(Image.new("RGB", (w, h), fill), (0, 0), mask)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([8, 8, w - 9, h - 9], radius=36, outline=(150, 168, 160), width=12)
    canvas.save(ASSETS / dst, "PNG", optimize=True)
    print("wrote", dst)

if __name__ == "__main__":
    detail("cat.png", (215, 5, 355, 145), "quiz_cat_ear.png", (220, 140, 80))
    detail("cat.png", (255, 95, 400, 240), "quiz_cat_nose.png", (220, 140, 80))
    detail("dog.png", (155, 40, 290, 200), "quiz_dog_ear.png", (90, 150, 110))
    detail("dog.png", (270, 130, 400, 270), "quiz_dog_nose.png", (90, 150, 110))
    detail("bird.png", (300, 70, 460, 230), "quiz_bird_beak.png", (90, 140, 190))
    detail("bird.png", (200, 150, 360, 310), "quiz_bird_tail.png", (90, 140, 190))
    detail("fish.png", (140, 90, 320, 270), "quiz_fish_eye.png", (210, 170, 60))
    detail("fish.png", (360, 70, 580, 300), "quiz_fish_tail.png", (210, 170, 60))
    sil("dog.png", "quiz_dog_sil.png", (70, 55, 45))
    sil("bird.png", "quiz_bird_sil.png", (50, 75, 105))
    # cat/fish silhouettes unreliable via threshold — use CSS brightness(0) at runtime
    print("done")
