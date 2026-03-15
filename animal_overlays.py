from PIL import Image, ImageDraw
import numpy as np


def _circle(draw, cx, cy, r, fill, outline=None, ow=0):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill,
                 outline=outline, width=ow)


def draw_rabbit(size=200) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # Kulaklar
    for ex in [s*0.32, s*0.68]:
        d.ellipse([ex-s*0.1, s*0.02, ex+s*0.1, s*0.42], fill=(230,200,220,255))
        d.ellipse([ex-s*0.06, s*0.05, ex+s*0.06, s*0.38], fill=(255,150,170,255))
    # Kafa
    _circle(d, s//2, int(s*0.62), int(s*0.32), (240,215,230,255))
    # Gozler
    for ex in [s*0.38, s*0.62]:
        _circle(d, int(ex), int(s*0.55), int(s*0.06), (40,20,60,255))
        _circle(d, int(ex)+int(s*0.02), int(s*0.53), int(s*0.02), (255,255,255,255))
    # Burun
    _circle(d, s//2, int(s*0.67), int(s*0.04), (255,100,130,255))
    # Agiz
    d.arc([int(s*0.44), int(s*0.67), int(s*0.50), int(s*0.74)], 0, 180, fill=(180,80,100,255), width=2)
    d.arc([int(s*0.50), int(s*0.67), int(s*0.56), int(s*0.74)], 0, 180, fill=(180,80,100,255), width=2)
    # Bıyıklar
    for sign in [-1, 1]:
        d.line([(s//2 + sign*int(s*0.06), int(s*0.67)),
                (s//2 + sign*int(s*0.28), int(s*0.64))], fill=(150,100,120,255), width=2)
        d.line([(s//2 + sign*int(s*0.06), int(s*0.69)),
                (s//2 + sign*int(s*0.28), int(s*0.70))], fill=(150,100,120,255), width=2)
    return img


def draw_cat(size=200) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # Kulaklar (ucgen)
    for ex, pts in [
        (s*0.28, [(s*0.18,s*0.28),(s*0.28,s*0.08),(s*0.40,s*0.28)]),
        (s*0.72, [(s*0.60,s*0.28),(s*0.72,s*0.08),(s*0.82,s*0.28)]),
    ]:
        d.polygon([(int(x),int(y)) for x,y in pts], fill=(200,160,100,255))
        inner = [(int(x+s*0.02*(1 if x<s*0.5 else -1)), int(y+s*0.04)) for x,y in pts]
        d.polygon(inner, fill=(255,150,150,255))
    # Kafa
    _circle(d, s//2, int(s*0.58), int(s*0.32), (210,170,110,255))
    # Gozler
    for ex in [s*0.37, s*0.63]:
        _circle(d, int(ex), int(s*0.52), int(s*0.07), (60,180,80,255))
        _circle(d, int(ex), int(s*0.52), int(s*0.04), (20,20,20,255))
        _circle(d, int(ex)+int(s*0.02), int(s*0.50), int(s*0.015), (255,255,255,255))
    # Burun
    pts = [(s*0.50,s*0.62),(s*0.45,s*0.67),(s*0.55,s*0.67)]
    d.polygon([(int(x),int(y)) for x,y in pts], fill=(255,100,120,255))
    # Bıyıklar
    for sign in [-1, 1]:
        for dy in [0, s*0.04]:
            d.line([(s//2+sign*int(s*0.04), int(s*0.65+dy)),
                    (s//2+sign*int(s*0.30), int(s*0.63+dy))],
                   fill=(80,60,40,255), width=2)
    return img


def draw_dog(size=200) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # Kulaklar (sarkan)
    for ex in [s*0.22, s*0.78]:
        d.ellipse([int(ex-s*0.14), int(s*0.22), int(ex+s*0.14), int(s*0.62)],
                  fill=(160,110,60,255))
    # Kafa
    _circle(d, s//2, int(s*0.52), int(s*0.32), (200,150,90,255))
    # Burun bolumu
    d.ellipse([int(s*0.36), int(s*0.58), int(s*0.64), int(s*0.78)],
              fill=(220,170,110,255))
    # Gozler
    for ex in [s*0.37, s*0.63]:
        _circle(d, int(ex), int(s*0.45), int(s*0.07), (60,40,20,255))
        _circle(d, int(ex)+int(s*0.02), int(s*0.43), int(s*0.02), (255,255,255,255))
    # Burun
    _circle(d, s//2, int(s*0.62), int(s*0.07), (40,20,10,255))
    # Agiz
    d.arc([int(s*0.42), int(s*0.64), int(s*0.58), int(s*0.76)], 0, 180,
          fill=(80,40,20,255), width=3)
    return img


def draw_bird(size=200) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # Govde
    _circle(d, s//2, int(s*0.62), int(s*0.28), (80,160,255,255))
    # Kafa
    _circle(d, s//2, int(s*0.35), int(s*0.22), (60,140,230,255))
    # Kanatlar
    d.ellipse([int(s*0.10), int(s*0.45), int(s*0.42), int(s*0.75)],
              fill=(50,120,220,255))
    d.ellipse([int(s*0.58), int(s*0.45), int(s*0.90), int(s*0.75)],
              fill=(50,120,220,255))
    # Goz
    _circle(d, int(s*0.57), int(s*0.30), int(s*0.05), (20,20,20,255))
    _circle(d, int(s*0.585), int(s*0.285), int(s*0.015), (255,255,255,255))
    # Gaga
    pts = [(s*0.62,s*0.36),(s*0.80,s*0.38),(s*0.62,s*0.42)]
    d.polygon([(int(x),int(y)) for x,y in pts], fill=(255,180,0,255))
    # Tepe tuyler
    for i, (tx,ty) in enumerate([(s*0.44,s*0.14),(s*0.50,s*0.10),(s*0.56,s*0.14)]):
        d.ellipse([int(tx-s*0.03), int(ty-s*0.06), int(tx+s*0.03), int(ty+s*0.02)],
                  fill=(255,80,80,255))
    return img


def draw_fox(size=200) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # Kulaklar
    for ex, pts in [
        (s*0.28, [(s*0.16,s*0.30),(s*0.26,s*0.06),(s*0.40,s*0.30)]),
        (s*0.72, [(s*0.60,s*0.30),(s*0.74,s*0.06),(s*0.84,s*0.30)]),
    ]:
        d.polygon([(int(x),int(y)) for x,y in pts], fill=(220,90,20,255))
        inner = [(int(x+s*0.02*(1 if x<s*0.5 else -1)), int(y+s*0.04)) for x,y in pts]
        d.polygon(inner, fill=(255,200,180,255))
    # Kafa
    _circle(d, s//2, int(s*0.58), int(s*0.30), (220,90,20,255))
    # Beyaz yuz
    _circle(d, s//2, int(s*0.62), int(s*0.18), (250,230,210,255))
    # Gozler
    for ex in [s*0.37, s*0.63]:
        _circle(d, int(ex), int(s*0.52), int(s*0.07), (80,40,0,255))
        _circle(d, int(ex)+int(s*0.02), int(s*0.50), int(s*0.02), (255,255,255,255))
    # Burun
    _circle(d, s//2, int(s*0.66), int(s*0.05), (30,10,0,255))
    return img


def draw_bear(size=200) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    # Kulaklar
    for ex in [s*0.28, s*0.72]:
        _circle(d, int(ex), int(s*0.22), int(s*0.12), (80,50,20,255))
        _circle(d, int(ex), int(s*0.22), int(s*0.07), (120,70,30,255))
    # Kafa
    _circle(d, s//2, int(s*0.58), int(s*0.33), (100,65,25,255))
    # Burun bolumu
    _circle(d, s//2, int(s*0.67), int(s*0.14), (130,85,35,255))
    # Gozler
    for ex in [s*0.38, s*0.62]:
        _circle(d, int(ex), int(s*0.50), int(s*0.06), (20,10,5,255))
        _circle(d, int(ex)+int(s*0.02), int(s*0.48), int(s*0.02), (255,255,255,255))
    # Burun
    _circle(d, s//2, int(s*0.64), int(s*0.06), (20,10,5,255))
    return img


ANIMAL_DRAWERS = {
    "Tavşan":  draw_rabbit,
    "Kedi":    draw_cat,
    "Köpek":   draw_dog,
    "Kuş":     draw_bird,
    "Tilki":   draw_fox,
    "Ayı":     draw_bear,
}

_cache: dict = {}

def get_overlay(name: str, size: int) -> Image.Image:
    key = (name, size)
    if key not in _cache:
        fn = ANIMAL_DRAWERS.get(name, draw_rabbit)
        _cache[key] = fn(size)
    return _cache[key]


def overlay_on_frame(frame_bgr: np.ndarray, boxes: list, animal_name: str) -> np.ndarray:
    from PIL import Image as PILImage
    img = PILImage.fromarray(frame_bgr[:, :, ::-1]).convert("RGBA")
    for (x1, y1, x2, y2) in boxes:
        w, h = x2 - x1, y2 - y1
        size = max(int(max(w, h) * 1.1), 40)
        overlay = get_overlay(animal_name, size)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        px = cx - size // 2
        py = cy - size // 2
        img.paste(overlay, (px, py), overlay)
    result = np.array(img.convert("RGB"))
    return result[:, :, ::-1]
