"""
Animasyonlu hayvan cizimleri - yuruyus dongusu ile 8 frame.
Her hayvan icin 8 animasyon karesi uretilir.
"""
import math
import numpy as np
from PIL import Image, ImageDraw


def _circle(draw, cx, cy, r, fill, outline=None, ow=0):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=ow)


def _draw_dog_frame(size: int, t: float) -> Image.Image:
    """t: 0..1 animasyon zamani"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    bob = int(math.sin(t * math.pi * 2) * s * 0.025)

    # Govde
    d.ellipse([int(s*.20), int(s*.42+bob), int(s*.82), int(s*.72+bob)],
              fill=(200, 150, 90, 255))

    # Bacaklar (4 adet, sallanan)
    for i, bx in enumerate([s*.28, s*.40, s*.60, s*.72]):
        phase = (t + i * 0.25) % 1.0
        leg_off = int(math.sin(phase * math.pi * 2) * s * 0.06)
        d.rectangle([int(bx-s*.04), int(s*.68+bob), int(bx+s*.04), int(s*.85+bob+leg_off)],
                    fill=(170, 120, 60, 255))

    # Kuyruk (sallanan)
    tail_ang = math.sin(t * math.pi * 4) * 0.5
    tx = int(s*.80 + math.cos(tail_ang) * s*.14)
    ty = int(s*.48 + bob + math.sin(tail_ang) * s*.14)
    d.line([(int(s*.80), int(s*.48+bob)), (tx, ty)],
           fill=(170, 120, 60, 255), width=max(3, int(s*.04)))

    # Kafa
    _circle(d, int(s*.18), int(s*.42+bob), int(s*.15), (200, 150, 90, 255))

    # Kulaklar (sarkan)
    for ex in [s*.10, s*.26]:
        d.ellipse([int(ex-s*.06), int(s*.34+bob), int(ex+s*.06), int(s*.56+bob)],
                  fill=(160, 110, 60, 255))

    # Gozler
    _circle(d, int(s*.20), int(s*.38+bob), int(s*.025), (20, 10, 5, 255))
    _circle(d, int(s*.22), int(s*.37+bob), int(s*.008), (255, 255, 255, 255))

    # Burun
    _circle(d, int(s*.10), int(s*.44+bob), int(s*.03), (30, 10, 0, 255))

    return img


def _draw_cat_frame(size: int, t: float) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    bob = int(math.sin(t * math.pi * 2) * s * 0.025)

    d.ellipse([int(s*.22), int(s*.42+bob), int(s*.82), int(s*.68+bob)],
              fill=(210, 170, 110, 255))

    for i, bx in enumerate([s*.30, s*.42, s*.60, s*.72]):
        phase = (t + i * 0.25) % 1.0
        leg_off = int(math.sin(phase * math.pi * 2) * s * 0.05)
        d.rectangle([int(bx-s*.035), int(s*.65+bob), int(bx+s*.035), int(s*.82+bob+leg_off)],
                    fill=(180, 140, 80, 255))

    # Kuyruk (kıvrık)
    tail_t = math.sin(t * math.pi * 2) * 0.4
    pts = []
    for step in range(8):
        a = step / 7.0
        curve = math.sin(a * math.pi + tail_t) * s * .12
        pts.append((int(s*.82 + a*s*.12 + curve), int(s*.55+bob - a*s*.25)))
    for j in range(len(pts)-1):
        d.line([pts[j], pts[j+1]], fill=(180, 140, 80, 255), width=max(3, int(s*.035)))

    # Kafa
    _circle(d, int(s*.16), int(s*.38+bob), int(s*.14), (210, 170, 110, 255))

    # Kulaklar (ucgen)
    for pts_ear in [
        [(s*.06, s*.28+bob), (s*.12, s*.12+bob), (s*.24, s*.28+bob)],
        [(s*.08, s*.28+bob), (s*.14, s*.14+bob), (s*.22, s*.28+bob)],
    ]:
        pass
    d.polygon([(int(s*.06), int(s*.28+bob)), (int(s*.12), int(s*.10+bob)),
               (int(s*.22), int(s*.28+bob))], fill=(200, 160, 100, 255))
    d.polygon([(int(s*.10), int(s*.28+bob)), (int(s*.14), int(s*.14+bob)),
               (int(s*.20), int(s*.28+bob))], fill=(255, 150, 150, 255))

    _circle(d, int(s*.19), int(s*.34+bob), int(s*.025), (60, 180, 80, 255))
    _circle(d, int(s*.21), int(s*.33+bob), int(s*.008), (255, 255, 255, 255))
    _circle(d, int(s*.10), int(s*.40+bob), int(s*.025), (255, 100, 120, 255))

    return img


def _draw_rabbit_frame(size: int, t: float) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    hop = abs(math.sin(t * math.pi * 2)) * s * 0.06

    d.ellipse([int(s*.28), int(s*.48-hop), int(s*.78), int(s*.76-hop)],
              fill=(230, 200, 220, 255))

    for bx in [s*.36, s*.70]:
        d.rectangle([int(bx-s*.04), int(s*.73-hop), int(bx+s*.04), int(s*.88-hop)],
                    fill=(210, 175, 200, 255))

    for ex in [s*.36, s*.62]:
        d.ellipse([int(ex-s*.06), int(s*.14-hop), int(ex+s*.06), int(s*.50-hop)],
                  fill=(230, 200, 220, 255))
        d.ellipse([int(ex-s*.03), int(s*.17-hop), int(ex+s*.03), int(s*.45-hop)],
                  fill=(255, 150, 170, 255))

    _circle(d, int(s*.50), int(s*.42-hop), int(s*.16), (240, 215, 230, 255))
    _circle(d, int(s*.43), int(s*.38-hop), int(s*.025), (40, 20, 60, 255))
    _circle(d, int(s*.57), int(s*.38-hop), int(s*.025), (40, 20, 60, 255))
    _circle(d, int(s*.50), int(s*.45-hop), int(s*.018), (255, 100, 130, 255))

    return img


def _draw_bird_frame(size: int, t: float) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    bob = int(math.sin(t * math.pi * 2) * s * 0.03)
    wing_angle = math.sin(t * math.pi * 4) * 0.35

    _circle(d, int(s*.50), int(s*.65+bob), int(s*.22), (80, 160, 255, 255))
    _circle(d, int(s*.50), int(s*.36+bob), int(s*.18), (60, 140, 230, 255))

    # Kanatlar
    for sign, wx in [(-1, s*.20), (1, s*.80)]:
        wy = s*.58 + bob + sign * wing_angle * s * .15
        d.ellipse([int(wx-s*.18), int(wy-s*.12), int(wx+s*.18), int(wy+s*.12)],
                  fill=(50, 120, 220, 255))

    _circle(d, int(s*.58), int(s*.31+bob), int(s*.04), (20, 20, 20, 255))
    pts = [(s*.64, s*.36+bob), (s*.80, s*.38+bob), (s*.64, s*.42+bob)]
    d.polygon([(int(x), int(y)) for x, y in pts], fill=(255, 180, 0, 255))

    # Bacaklar
    for bx in [s*.43, s*.57]:
        d.line([(int(bx), int(s*.85+bob)), (int(bx), int(s*.95+bob))],
               fill=(255, 180, 0, 255), width=max(2, int(s*.025)))

    return img


def _draw_fox_frame(size: int, t: float) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    bob = int(math.sin(t * math.pi * 2) * s * 0.025)

    d.ellipse([int(s*.20), int(s*.44+bob), int(s*.80), int(s*.70+bob)],
              fill=(220, 90, 20, 255))

    for i, bx in enumerate([s*.28, s*.40, s*.60, s*.72]):
        phase = (t + i * 0.25) % 1.0
        leg_off = int(math.sin(phase * math.pi * 2) * s * 0.05)
        d.rectangle([int(bx-s*.04), int(s*.67+bob), int(bx+s*.04), int(s*.84+bob+leg_off)],
                    fill=(190, 70, 10, 255))

    tail_a = math.sin(t * math.pi * 2) * 0.4
    tx = int(s*.82 + math.cos(tail_a)*s*.16)
    ty = int(s*.50+bob + math.sin(tail_a)*s*.16)
    d.line([(int(s*.82), int(s*.50+bob)), (tx, ty)],
           fill=(220, 90, 20, 255), width=max(6, int(s*.07)))
    _circle(d, tx, ty, max(5, int(s*.06)), (250, 240, 230, 255))

    _circle(d, int(s*.16), int(s*.40+bob), int(s*.14), (220, 90, 20, 255))
    _circle(d, int(s*.16), int(s*.46+bob), int(s*.09), (250, 220, 200, 255))

    for pts_ear in [
        [(s*.06, s*.28+bob), (s*.10, s*.10+bob), (s*.22, s*.28+bob)],
    ]:
        d.polygon([(int(x), int(y)) for x, y in pts_ear], fill=(220, 90, 20, 255))

    _circle(d, int(s*.20), int(s*.35+bob), int(s*.025), (80, 40, 0, 255))
    _circle(d, int(s*.08), int(s*.43+bob), int(s*.025), (30, 10, 0, 255))

    return img


def _draw_bear_frame(size: int, t: float) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    bob = int(math.sin(t * math.pi * 2) * s * 0.02)

    d.ellipse([int(s*.18), int(s*.42+bob), int(s*.82), int(s*.72+bob)],
              fill=(100, 65, 25, 255))

    for i, bx in enumerate([s*.26, s*.40, s*.60, s*.74]):
        phase = (t + i * 0.25) % 1.0
        leg_off = int(math.sin(phase * math.pi * 2) * s * 0.04)
        d.rectangle([int(bx-s*.05), int(s*.69+bob), int(bx+s*.05), int(s*.86+bob+leg_off)],
                    fill=(80, 50, 15, 255))

    _circle(d, int(s*.18), int(s*.40+bob), int(s*.16), (100, 65, 25, 255))
    for ex in [s*.08, s*.28]:
        _circle(d, int(ex), int(s*.28+bob), int(s*.07), (80, 50, 20, 255))
        _circle(d, int(ex), int(s*.28+bob), int(s*.04), (100, 65, 25, 255))

    _circle(d, int(s*.18), int(s*.46+bob), int(s*.08), (120, 80, 30, 255))
    _circle(d, int(s*.18), int(s*.44+bob), int(s*.03), (20, 10, 5, 255))
    _circle(d, int(s*.24), int(s*.36+bob), int(s*.025), (20, 10, 5, 255))

    return img


FRAME_DRAWERS = {
    "Köpek":   _draw_dog_frame,
    "Kedi":    _draw_cat_frame,
    "Tavşan":  _draw_rabbit_frame,
    "Kuş":     _draw_bird_frame,
    "Tilki":   _draw_fox_frame,
    "Ayı":     _draw_bear_frame,
}

N_FRAMES = 12
_anim_cache: dict = {}


def get_anim_frames(name: str, size: int) -> list:
    key = (name, size)
    if key not in _anim_cache:
        fn = FRAME_DRAWERS.get(name, _draw_dog_frame)
        frames = [fn(size, i / N_FRAMES) for i in range(N_FRAMES)]
        _anim_cache[key] = frames
    return _anim_cache[key]


def overlay_animal_on_frame(frame_bgr: np.ndarray,
                             detections: list,
                             animal_name: str,
                             frame_idx: int) -> np.ndarray:
    from PIL import Image as PILImage

    # RGB olarak tut — RGBA'ya cevirme (siyah delik sorunu olur)
    img = PILImage.fromarray(frame_bgr[:, :, ::-1])
    fw, fh = img.size

    for det in detections:
        x1, y1, x2, y2 = det[:4]

        # Sinir kontrolu
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(fw, x2); y2 = min(fh, y2)
        if x2 <= x1 or y2 <= y1:
            continue

        w, h = x2 - x1, y2 - y1

        # Tespit alani tum ekranin %70'inden buyukse atla (gurultu)
        if w * h > fw * fh * 0.70:
            continue

        # Overlay boyutu — hayvanin bbox'u ile orantili, max 500px
        size = max(min(int(max(w, h) * 1.2), 500), 50)
        frames = get_anim_frames(animal_name, size)
        anim_frame = frames[frame_idx % len(frames)]

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        px = max(0, cx - size // 2)
        py = max(0, cy - size // 2)

        # Kırpma: ekran dışına taşmasın
        crop_x2 = min(size, fw - px)
        crop_y2 = min(size, fh - py)
        if crop_x2 <= 0 or crop_y2 <= 0:
            continue
        anim_cropped = anim_frame.crop((0, 0, crop_x2, crop_y2))

        img.paste(anim_cropped, (px, py), anim_cropped)

    return np.array(img)[:, :, ::-1]
