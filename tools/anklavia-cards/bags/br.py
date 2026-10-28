"""Карточки женских сумок Anklavia: подиумы, интерьеры (бутик, кафе, лобби, консоль), тёмные editorial-обложки,
размеры с выносными линиями, «что поместится», цвета модели, макро фактуры, характеристики. 1800×2400 → 900×1200."""
import os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/mats'); sys.path.insert(0, '/home/claude/mass')
from gfx import vlin, glow, poly_grad, fit, cover_crop, rgba, mixc, paste_clip, lum
from render_m2 import F, tw, fitf, wrap, icon, W, H

D = '/home/claude/bags'
BG = {
    'podium': ['b42', 'b43', 'b44', 'b45', 'b46', 'b47', 'b49', 'b50', 'b51', 'b52', 'b53', 'b56', 'b57'],
    'podium_dark': ['b48', 'b58', 'b59'],
    'wall': ['b100', 'b101', 'b102', 'b103', 'b104', 'b106', 'b107', 'b109', 'b110'],
    'marble': ['b21', 'b22', 'b27', 'b29'],
    'dark': ['b30', 'b34', 'b36', 'b37', 'b48', 'b58', 'b59', 'b175', 'b176', 'b177'],
    'boutique': ['b61', 'b62', 'b64', 'b67', 'b68', 'b69', 'b70', 'b73', 'b74', 'b79', 'b80', 'b235', 'b237', 'b238', 'b239', 'b242', 'b243'],
    'cafe': ['b81', 'b82', 'b83', 'b85', 'b86', 'b87', 'b88', 'b93', 'b94', 'b95', 'b96', 'b97', 'b98', 'b99'],
    'home': ['b160', 'b161', 'b162', 'b165', 'b167', 'b175', 'b176', 'b177', 'b178', 'b179'],
    'lobby': ['b180', 'b181', 'b182', 'b183', 'b186', 'b187', 'b192', 'b194', 'b195', 'b196'],
    'street': ['b204', 'b205', 'b206', 'b207', 'b208', 'b209', 'b211'],
    'console': ['b220', 'b221', 'b222', 'b223', 'b224', 'b225', 'b226', 'b227', 'b228', 'b230', 'b231', 'b232'],
}
PAL = {
    'cream': dict(t=(250, 245, 238), b=(234, 224, 210), ink=(44, 34, 28), sub=(120, 102, 88), acc=(156, 106, 70), acc_ink=(255, 255, 255), dark=False),
    'blush': dict(t=(251, 240, 236), b=(238, 216, 208), ink=(72, 40, 40), sub=(140, 100, 96), acc=(178, 98, 96), acc_ink=(255, 255, 255), dark=False),
    'sage': dict(t=(238, 241, 232), b=(212, 220, 204), ink=(34, 46, 36), sub=(90, 106, 90), acc=(86, 112, 84), acc_ink=(255, 255, 255), dark=False),
    'stone': dict(t=(242, 241, 238), b=(220, 217, 212), ink=(36, 36, 38), sub=(106, 104, 102), acc=(36, 36, 38), acc_ink=(244, 240, 234), dark=False),
    'mocha': dict(t=(72, 56, 46), b=(28, 22, 18), ink=(250, 242, 232), sub=(214, 196, 178), acc=(214, 176, 112), acc_ink=(36, 28, 18), dark=True),
    'noir': dict(t=(46, 44, 46), b=(12, 12, 14), ink=(246, 244, 240), sub=(196, 192, 186), acc=(206, 172, 116), acc_ink=(20, 18, 14), dark=True),
    'wine': dict(t=(92, 36, 46), b=(40, 12, 18), ink=(252, 240, 238), sub=(226, 196, 196), acc=(232, 196, 150), acc_ink=(60, 20, 28), dark=True),
    'navy': dict(t=(36, 46, 66), b=(14, 20, 34), ink=(248, 244, 236), sub=(192, 200, 214), acc=(212, 178, 114), acc_ink=(24, 22, 18), dark=True),
}
HEAD = ['playfair-display-700', 'cormorant-garamond-700', 'prata-400', 'unbounded-600', 'montserrat-800', 'lora-700', 'jost-600', 'raleway-700']
BODY, BOLD = 'manrope-500', 'manrope-800'
_bgc = {}

def save(cv, p): cv.convert('RGB').resize((900, 1200), Image.LANCZOS).save(p, quality=90)

def photo_bg(name, blur=20, dark=0.0, light=0.0, fy=0.5):
    k = (name, blur, round(dark, 2), round(light, 2), fy)
    if k not in _bgc:
        im = Image.open(f'{D}/bg/{name}.jpg').convert('RGB')
        im = cover_crop(im, W // 3, H // 3, 0.5, fy)
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur / 3))
        im = im.resize((W, H), Image.BICUBIC)
        if dark: im = ImageEnhance.Brightness(im).enhance(1 - dark)
        if light: im = Image.blend(im, Image.new('RGB', im.size, (250, 246, 240)), light)
        _bgc[k] = im.convert('RGBA')
        if len(_bgc) > 40: _bgc.pop(next(iter(_bgc)))
    return _bgc[k].copy()

def vgrad(cv, y0, y1, col, a0, a1):
    poly_grad(cv, [(0, y0), (W, y0), (W, y1), (0, y1)], col, col, a0, a1, vertical=True)

def shadow_rr(cv, box, r, col, blur):
    x0, y0, x1, y1 = [int(v) for v in box]; pad = blur * 2; s = 4
    w, h = (x1 - x0 + 2 * pad) // s + 1, (y1 - y0 + 2 * pad) // s + 1
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((pad // s, pad // s, (x1 - x0 + pad) // s, (y1 - y0 + pad) // s), max(1, r // s), fill=col[3] if len(col) > 3 else 120)
    m = m.filter(ImageFilter.GaussianBlur(max(1, blur / s))).resize((w * s, h * s), Image.BILINEAR)
    lay = Image.new('RGBA', m.size, tuple(col[:3]) + (0,)); lay.putalpha(m); paste_clip(cv, lay, x0 - pad, y0 - pad)

def contact_shadow(cv, p, x, y, a=0.55, spread=1.0):
    """мягкая тень под товаром: эллипс у основания + размытая проекция"""
    al = np.asarray(p.split()[3]) > 100; ys = np.where(al.any(1))[0]
    if not len(ys): return
    yb = ys.max(); xs = np.where(al[max(0, yb - 12):yb + 1].any(0))[0]; x0, x1 = xs.min(), xs.max()
    w = int((x1 - x0) * 1.12 * spread); h = max(40, int(w * 0.09))
    m = Image.new('L', (w + 200, h + 200), 0); ImageDraw.Draw(m).ellipse((100, 100, 100 + w, 100 + h), fill=int(255 * a))
    m = m.filter(ImageFilter.GaussianBlur(26)); lay = Image.new('RGBA', m.size, (0, 0, 0, 0)); lay.putalpha(m)
    paste_clip(cv, lay, int(x + (x0 + x1) / 2 - w / 2 - 100), int(y + yb - h / 2 - 100 + 6))
    s = 4; sm = p.split()[3].resize((max(1, p.width // s), max(1, p.height // s)))
    pad = 30; big = Image.new('L', (sm.width + 2 * pad, sm.height + 2 * pad), 0); big.paste(sm.point(lambda v: int(v * a * 0.45)), (pad, pad))
    big = big.filter(ImageFilter.GaussianBlur(12)).resize(((sm.width + 2 * pad) * s, (sm.height + 2 * pad) * s), Image.BILINEAR)
    lay = Image.new('RGBA', big.size, (0, 0, 0, 0)); lay.putalpha(big); paste_clip(cv, lay, x - pad * s + 24, y - pad * s + 34)

def load_cut(k):
    c = Image.open(f'{D}/cut/{k}.png').convert('RGBA')
    if max(c.size) < 1000:
        s = 1000 / max(c.size); c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    return c

def dom_color(cut):
    a = np.asarray(cut.convert('RGBA').resize((120, int(120 * cut.height / cut.width) or 1)))
    m = a[..., 3] > 200; px = a[..., :3][m]
    return tuple(int(v) for v in np.median(px, 0)) if len(px) else (128, 128, 128)

class V:
    def __init__(self, p, v):
        self.p, self.v = p, v; n = p['n']
        self.pal = PAL[p['pal']]; self.head = HEAD[(n * 5 + 1) % len(HEAD)]
        self.cut = load_cut(v['key']); self.col = dom_color(self.cut)
        rnd = random.Random(n * 37 + 11)
        self.bg = {k: rnd.choice(vs) for k, vs in BG.items()}
        self.scene = ['boutique', 'cafe', 'lobby', 'console', 'home', 'street'][(n * 7) % 6]

def brand(cv, x, y, col, anchor='la'):
    ImageDraw.Draw(cv).text((x, y), 'ANKLAVIA', font=F('montserrat-700', 34), fill=col, anchor=anchor)

def fmt(x): return str(int(x)) if float(x).is_integer() else str(x).replace('.', ',')

def size_txt(p):
    d = p['dims']; return f"{fmt(d['w'])}×{fmt(d['h'])}×{fmt(d['d'])} см"

def chips(cv, x, y, items, fill, ink, fs=44, gap=22, center=False):
    d = ImageDraw.Draw(cv); f = F(BOLD, fs); hh = fs + 44
    ws = [tw(d, t, f) + 64 + (fs + 14 if ic else 0) for ic, t in items]
    if center: x = (W - sum(ws) - gap * (len(ws) - 1)) / 2
    for (ic, t), w in zip(items, ws):
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle((x, y, x + w, y + hh), hh // 2, fill=fill); cv.alpha_composite(lay)
        d = ImageDraw.Draw(cv); xx = x + 32
        if ic: icon(d, (xx + fs // 2, y + hh / 2), ic, fs + 6, ink); xx += fs + 14
        d.text((xx, y + hh / 2), t, font=f, fill=ink, anchor='lm'); x += w + gap

def std_chips(v):
    return [('ruler', size_txt(v.p)), ('texture-box', v.p['mat_label']), (v.p['wear_icon'], v.p['wear_label'])]

def title(cv, v, x, y, mw, col, sub_col, size=136, anchor='la'):
    d = ImageDraw.Draw(cv); lines = v.p['cover']
    f = fitf(d, lines[0], v.head, size, mw)
    for ln in wrap(d, lines[0], f, mw)[:2]:
        d.text((x, y), ln, font=f, fill=col, anchor=anchor); y += f.size * 1.1
    y += 12; f2 = fitf(d, lines[1], BODY, 56, mw)
    d.text((x, y), lines[1], font=f2, fill=sub_col, anchor=anchor)
    return y + f2.size * 1.3

def put(cv, v, box, anchor='b', shadow=True, a=0.5, cut=None):
    c = cut or v.cut; x0, y0, x1, y1 = box; p = fit(c, x1 - x0, y1 - y0)
    x = int(x0 + (x1 - x0 - p.width) / 2)
    y = int(y1 - p.height) if anchor == 'b' else int(y0 + (y1 - y0 - p.height) / 2)
    if shadow: contact_shadow(cv, p, x, y, a)
    cv.alpha_composite(p, (x, y)); return x, y, p

def pedestal(cv, cx, top, w, col, dark=False):
    """цилиндрический подиум: верхний эллипс + корпус с вертикальным градиентом"""
    h = 520; eh = int(w * 0.16)
    shadow_rr(cv, (cx - w / 2 + 30, top + eh, cx + w / 2 - 30, top + h + 60), 60, (0, 0, 0, 90), 50)
    c1 = mixc(col, (255, 255, 255), 0.18); c2 = mixc(col, (0, 0, 0), 0.22)
    poly_grad(cv, [(cx - w / 2, top + eh / 2), (cx + w / 2, top + eh / 2), (cx + w / 2, H + 10), (cx - w / 2, H + 10)], c1, c2, vertical=True)
    # боковое затенение
    poly_grad(cv, [(cx + w * 0.18, top + eh / 2), (cx + w / 2, top + eh / 2), (cx + w / 2, H), (cx + w * 0.18, H)], (0, 0, 0), (0, 0, 0), 0, 70)
    poly_grad(cv, [(cx - w / 2, top + eh / 2), (cx - w * 0.3, top + eh / 2), (cx - w * 0.3, H), (cx - w / 2, H)], (255, 255, 255), (255, 255, 255), 40, 0)
    d = ImageDraw.Draw(cv); d.ellipse((cx - w / 2, top, cx + w / 2, top + eh), fill=mixc(col, (255, 255, 255), 0.32))
    d.ellipse((cx - w / 2, top, cx + w / 2, top + eh), outline=mixc(col, (255, 255, 255), 0.5), width=3)
    return top + eh * 0.55

def bag_tone(v):
    """фон в тон сумке, но контрастный по светлоте"""
    c = v.col; L = lum(c)
    if L > 150: return mixc(c, (60, 48, 40), 0.55), mixc(c, (20, 16, 14), 0.75), True
    return mixc(c, (250, 246, 240), 0.82), mixc(c, (236, 228, 218), 0.62), False

# ---------- обложки ----------
def cover_podium(v):
    P = v.pal; cv = photo_bg(v.bg['podium'], 6)
    vgrad(cv, 0, 760, (255, 252, 248), 170, 0)
    top = pedestal(cv, W // 2, 1820, 1240, (226, 214, 198))
    put(cv, v, (230, 640, 1570, top + 10), 'b', a=0.55)
    ink = (44, 34, 28); brand(cv, W // 2, 70, (120, 100, 84), 'ma')
    title(cv, v, W // 2, 130, 1560, ink, (110, 92, 78), 128, anchor='ma')
    chips(cv, 0, 2190, std_chips(v), (255, 255, 255, 235), ink, fs=42, center=True)
    return cv

def cover_noir(v):
    P = v.pal; cv = photo_bg(v.bg['dark'], 30, dark=0.55)
    vgrad(cv, 0, 900, (0, 0, 0), 200, 0); vgrad(cv, 1700, H, (0, 0, 0), 0, 230)
    glow(cv, W / 2, 1280, 900, (255, 226, 180), 70)
    top = pedestal(cv, W // 2, 1900, 1100, (58, 52, 50))
    put(cv, v, (240, 700, 1560, top + 10), 'b', a=0.7)
    gold = (226, 196, 140); brand(cv, 100, 76, gold)
    title(cv, v, 100, 150, 1200, (252, 248, 240), (224, 210, 190), 140)
    d = ImageDraw.Draw(cv); d.line([(100, 120), (330, 120)], fill=gold, width=3)
    r = 150; cx, cy = 1560, 360; d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=gold, width=5)
    big = v.p['badge'][0]; d.text((cx, cy - 26), big, font=fitf(d, big, 'montserrat-800', 76, 230), fill=gold, anchor='mm')
    d.text((cx, cy + 52), v.p['badge'][1], font=fitf(d, v.p['badge'][1], BOLD, 30, 230), fill=(236, 224, 204), anchor='mm')
    chips(cv, 0, 2200, std_chips(v), (255, 255, 255, 40), (252, 246, 236), fs=44, center=True)
    return cv

def cover_scene(v):
    cv = photo_bg(v.bg[v.scene], 9, dark=0.1)
    vgrad(cv, 0, 760, (0, 0, 0), 180, 0)
    # столешница/консоль: светлая плита с кромкой
    top = 1780; d = ImageDraw.Draw(cv)
    shadow_rr(cv, (60, top + 20, W - 60, H + 80), 20, (0, 0, 0, 140), 50)
    poly_grad(cv, [(0, top), (W, top), (W, top + 60), (0, top + 60)], (238, 230, 220), (214, 202, 188), vertical=True)
    poly_grad(cv, [(0, top + 60), (W, top + 60), (W, H), (0, H)], (196, 182, 166), (150, 134, 118), vertical=True)
    put(cv, v, (260, 620, 1540, top + 22), 'b', a=0.6)
    brand(cv, 100, 76, (244, 236, 226)); title(cv, v, 100, 150, 1560, (255, 252, 246), (238, 228, 214), 132)
    vgrad(cv, 2050, H, (0, 0, 0), 0, 150)
    chips(cv, 100, 2230, std_chips(v), (255, 255, 255, 236), (40, 32, 26), fs=42)
    return cv

def cover_arch(v):
    t, b, dk = bag_tone(v); cv = vlin(W, H, t, b).convert('RGBA')
    ink = (250, 244, 236) if dk else (40, 32, 26); sub = (226, 214, 200) if dk else (112, 96, 84)
    ph = photo_bg(v.bg['wall' if not dk else 'podium_dark'], 4, dark=0.15 if dk else 0)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((260, 520, 1540, 2620), 640, fill=255)
    cv.paste(ph, (0, 0), m)
    acc = mixc(v.col, (255, 255, 255) if dk else (0, 0, 0), 0.35)
    ImageDraw.Draw(cv).rounded_rectangle((260, 520, 1540, 2620), 640, outline=acc, width=6)
    put(cv, v, (200, 760, 1600, 2010), 'b', a=0.5)
    brand(cv, W // 2, 66, sub, 'ma')
    title(cv, v, W // 2, 126, 1600, ink, sub, 128, anchor='ma')
    chips(cv, 0, 2170, std_chips(v), rgba(mixc(t, (0, 0, 0), 0.0) if dk else (255, 255, 255), 238), (40, 32, 26), fs=42, center=True)
    return cv

COVERS = [cover_podium, cover_noir, cover_scene, cover_arch]

# ---------- слайды ----------
def studio(v):
    P = v.pal; cv = vlin(W, H, P['t'], P['b']).convert('RGBA')
    glow(cv, W * 0.5, H * 0.45, 1000, (255, 255, 255) if not P['dark'] else (255, 220, 170), 70 if not P['dark'] else 34)
    return cv

def head(cv, v, t, s=None, y=110, col=None, scol=None):
    P = v.pal; d = ImageDraw.Draw(cv)
    f = fitf(d, t, v.head, 112, 1620); d.text((W / 2, y), t, font=f, fill=col or P['ink'], anchor='ma')
    yy = y + f.size * 1.28
    if s:
        for j, ln in enumerate(wrap(d, s, F(BODY, 46), 1520)[:2]): d.text((W / 2, yy + j * 58), ln, font=F(BODY, 46), fill=scol or P['sub'], anchor='ma')

def dim_line(d, a, b, col, w=5, tick=26):
    d.line([a, b], fill=col, width=w)
    if a[1] == b[1]:
        for x in (a[0], b[0]): d.line([(x, a[1] - tick), (x, a[1] + tick)], fill=col, width=w)
    else:
        for y in (a[1], b[1]): d.line([(a[0] - tick, y), (a[0] + tick, y)], fill=col, width=w)

def label(cv, xy, t, P, fs=54):
    d = ImageDraw.Draw(cv); f = F(BOLD, fs); w = tw(d, t, f) + 54; h = fs + 34; x, y = xy
    x = min(max(x, w / 2 + 20), W - w / 2 - 20)
    shadow_rr(cv, (x - w / 2, y - h / 2 + 8, x + w / 2, y + h / 2 + 8), h // 2, (0, 0, 0, 60), 14)
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), h // 2, fill=P['acc']); d.text((x, y), t, font=f, fill=P['acc_ink'], anchor='mm')

def body_box(p):
    """ограничивающий прямоугольник корпуса сумки без тонкого ремня: строки, где ширина ≥ 45% максимума"""
    al = np.asarray(p.split()[3]) > 120; wd = al.sum(1)
    rows = np.where(wd >= 0.45 * wd.max())[0]
    y0, y1 = rows.min(), rows.max(); xs = np.where(al[y0:y1 + 1].any(0))[0]
    return xs.min(), y0, xs.max(), y1

def card(cv, box, P, r=36):
    x0, y0, x1, y1 = box
    shadow_rr(cv, (x0, y0 + 14, x1, y1 + 14), r, (0, 0, 0, 50), 22)
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(box, r, fill=(255, 255, 255, 240) if not P['dark'] else (255, 255, 255, 28)); cv.alpha_composite(lay)

def s_sizes(v):
    P = v.pal; cv = studio(v); head(cv, v, 'Размеры', 'Компактная форма и точные размеры — сверьте с вашими вещами')
    x, y, p = put(cv, v, (330, 560, 1400, 1700), 'b', a=0.35)
    d = ImageDraw.Draw(cv); col = P['ink']; dd = v.p['dims']
    bx0, by0, bx1, by1 = body_box(p)
    yb = y + by1 + 70; dim_line(d, (x + bx0, yb), (x + bx1, yb), col)
    label(cv, ((2 * x + bx0 + bx1) / 2, yb + 84), f"{fmt(dd['w'])} см", P)
    xh = min(x + bx1 + 90, 1650); dim_line(d, (xh, y + by0), (xh, y + by1), col)
    label(cv, (xh + 60, (2 * y + by0 + by1) / 2), f"{fmt(dd['h'])} см", P)
    items = [('arrow-expand-horizontal', 'Глубина', f"{fmt(dd['d'])} см — {v.p['depth_note']}"),
             ('hand-back-right', 'Ремень' if v.p.get('strap') else 'Ручки', v.p['strap_txt'])]
    yy = 2010; cw = 1640 / len(items)
    for i, (ic, a, b) in enumerate(items):
        x0 = 80 + i * cw; card(cv, (x0 + 10, yy, x0 + cw - 10, yy + 276), P)
        d = ImageDraw.Draw(cv); icon(d, (x0 + 100, yy + 120), ic, 96, P['acc'])
        d.text((x0 + 180, yy + 46), a, font=F(BOLD, 42), fill=P['ink'])
        for j, ln in enumerate(wrap(d, b, F(BODY, 35), cw - 220)[:4]): d.text((x0 + 180, yy + 106 + j * 42), ln, font=F(BODY, 35), fill=P['sub'])
    return cv

FIT_IC = {'Смартфон': 'cellphone', 'Кошелёк': 'wallet', 'Ключи': 'key-variant', 'Помада': 'lipstick', 'Очки': 'sunglasses',
          'Планшет': 'tablet', 'Книга': 'book-open-variant', 'Зонт': 'umbrella', 'Бутылка воды': 'cup-water', 'Карты': 'credit-card',
          'Наушники': 'headphones', 'Блокнот': 'notebook', 'Ноутбук 13"': 'laptop', 'Паспорт': 'passport', 'Косметичка': 'face-woman-shimmer',
          'Документы А4': 'file-document-outline', 'Пауэрбанк': 'battery-charging', 'Духи': 'spray', 'Салфетки': 'package-variant'}

def s_fits(v):
    P = v.pal; cv = studio(v); head(cv, v, 'Что поместится', v.p['fit_s'])
    put(cv, v, (520, 470, 1280, 1170), 'b', a=0.35)
    its = v.p['fits'][:8]; cols = 4; cw = 1640 / cols; y0 = 1290
    for i, t in enumerate(its):
        cx = 80 + (i % cols) * cw; cy = y0 + (i // cols) * 470
        card(cv, (cx + 16, cy, cx + cw - 16, cy + 420), P, 44)
        d = ImageDraw.Draw(cv); d.ellipse((cx + cw / 2 - 100, cy + 50, cx + cw / 2 + 100, cy + 250), fill=P['acc'])
        icon(d, (cx + cw / 2, cy + 150), FIT_IC.get(t, 'check'), 110, P['acc_ink'])
        for j, ln in enumerate(wrap(d, t, F(BOLD, 42), cw - 70)[:2]): d.text((cx + cw / 2, cy + 290 + j * 50), ln, font=F(BOLD, 42), fill=P['ink'], anchor='ma')
    return cv

def s_scene(v):
    sc = {'boutique': 'cafe', 'cafe': 'console', 'lobby': 'home', 'console': 'lobby', 'home': 'boutique', 'street': 'cafe'}[v.scene]
    cv = photo_bg(v.bg[sc], 4, dark=0.08)
    top = 1900
    poly_grad(cv, [(0, top), (W, top), (W, top + 50), (0, top + 50)], (90, 66, 48), (70, 50, 36), vertical=True)
    poly_grad(cv, [(0, top + 50), (W, top + 50), (W, H), (0, H)], (58, 40, 28), (34, 24, 16), vertical=True)
    poly_grad(cv, [(0, top - 2), (W, top - 2), (W, top + 8), (0, top + 8)], (170, 136, 104), (170, 136, 104), vertical=True)
    put(cv, v, (420, 900, 1380, top + 18), 'b', a=0.6)
    vgrad(cv, 1980, H, (0, 0, 0), 0, 160)
    d = ImageDraw.Draw(cv); t = v.p['scene_t']
    d.text((W / 2, 2200), t, font=fitf(d, t, v.head, 92, 1600), fill=(255, 250, 242), anchor='mm')
    return cv

def s_callouts(v):
    P = v.pal; cv = studio(v); head(cv, v, v.p.get('call_t', 'Почему её выбирают'))
    put(cv, v, (470, 700, 1330, 1720), 'c', a=0.35)
    pos = [(80, 560), (1190, 560), (80, 1640), (1190, 1640)]
    for (ic, t, s), (cx, cy) in zip(v.p['feats'][:4], pos):
        w, h = 530, 430; card(cv, (cx, cy, cx + w, cy + h), P, 40)
        d = ImageDraw.Draw(cv); d.ellipse((cx + 40, cy + 40, cx + 150, cy + 150), fill=P['acc']); icon(d, (cx + 95, cy + 95), ic, 64, P['acc_ink'])
        d.text((cx + 40, cy + 182), t, font=fitf(d, t, BOLD, 46, w - 80), fill=P['ink'])
        for j, ln in enumerate(wrap(d, s, F(BODY, 34), w - 80)[:4]): d.text((cx + 40, cy + 248 + j * 42), ln, font=F(BODY, 34), fill=P['sub'])
    return cv

def s_macro(v):
    P = v.pal; cv = studio(v); head(cv, v, v.p['mac_t'], v.p['mac_s'])
    a = np.asarray(v.cut.split()[3]); bx0, by0, bx1, by1 = body_box(v.cut)
    cx0, cy0 = int((bx0 + bx1) / 2), int(by0 + (by1 - by0) * 0.55); s = int(min(bx1 - bx0, by1 - by0) * 0.42)
    for k in range(14):
        x0, y0 = cx0 - s // 2, cy0 - s // 2
        if x0 >= 0 and y0 >= 0 and (a[y0:y0 + s, x0:x0 + s] > 250).mean() > 0.97: break
        s = int(s * 0.88)
    tex = v.cut.convert('RGB').crop((max(0, cx0 - s // 2), max(0, cy0 - s // 2), cx0 + s // 2, cy0 + s // 2))
    r = 500; cx, cy = 1170, 1180
    t = tex.resize((2 * r, 2 * r), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 70, 2)).convert('RGBA')
    m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255); t.putalpha(m)
    shadow_rr(cv, (cx - r, cy - r + 30, cx + r, cy + r + 30), r, (0, 0, 0, 90), 30)
    cv.alpha_composite(t, (cx - r, cy - r)); d = ImageDraw.Draw(cv); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255), width=14)
    sm = fit(v.cut, 540, 600); sx, sy = 100, 1400 - sm.height // 2 + 160
    contact_shadow(cv, sm, sx, sy, 0.3); cv.alpha_composite(sm, (sx, sy))
    d.line([(sx + sm.width * 0.6, sy + sm.height * 0.5), (cx - r * 0.7, cy + r * 0.7)], fill=P['acc'], width=5)
    yy = 1840
    for ic, tt in v.p['mac_items'][:3]:
        d.ellipse((120, yy, 220, yy + 100), fill=P['acc']); icon(d, (170, yy + 50), ic, 58, P['acc_ink'])
        d.text((260, yy + 50), tt, font=fitf(d, tt, BOLD, 48, 1420), fill=P['ink'], anchor='lm'); yy += 140
    return cv

WEAR = {'hand': ('hand-back-right', 'В руке'), 'shoulder': ('account-outline', 'На плечо'), 'cross': ('vector-line', 'Через плечо'),
        'back': ('bag-personal', 'На спине'), 'waist': ('human-female', 'На поясе'), 'clutch': ('hand-heart', 'Как клатч')}

def s_colors(v, siblings):
    """цвета модели (другие варианты карточки) + способы носить"""
    P = v.pal; cv = photo_bg(v.bg['wall'], 22, light=0.0 if not P['dark'] else 0, dark=0.55 if P['dark'] else 0)
    if not P['dark']: cv = Image.blend(cv, vlin(W, H, P['t'], P['b']).convert('RGBA'), 0.55)
    ink = P['ink']
    if len(siblings) > 1:
        head(cv, v, 'Цвета модели', f"{len(siblings)} {'цвета' if len(siblings) < 5 else 'цветов'} — выберите свой")
        n = len(siblings); cols = min(n, 3); rows = (n + cols - 1) // cols
        cw = 1640 / cols; ch = min(760, 1300 / rows); y0 = 480
        for i, (key, cname) in enumerate(siblings):
            cx = 80 + (i % cols) * cw; cy = y0 + (i // cols) * ch
            card(cv, (cx + 14, cy, cx + cw - 14, cy + ch - 30), P, 40)
            c = load_cut(key); put(cv, v, (cx + 50, cy + 30, cx + cw - 50, cy + ch - 130), 'b', a=0.25, cut=c)
            d = ImageDraw.Draw(cv); d.text((cx + cw / 2, cy + ch - 84), cname, font=fitf(d, cname, BOLD, 40, cw - 80), fill=ink, anchor='mm')
        ytop = 1830
    else:
        head(cv, v, 'Как носить', v.p['wear_s'])
        put(cv, v, (420, 480, 1380, 1560), 'b', a=0.35); ytop = 1700
    ws = [WEAR[w] for w in v.p['wear']]; cw = 1640 / len(ws)
    for i, (ic, t) in enumerate(ws):
        cx = 80 + cw * i + cw / 2
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle((cx - cw / 2 + 16, ytop + 60, cx + cw / 2 - 16, ytop + 440), 44, fill=rgba(P['acc'], 245)); cv.alpha_composite(lay)
        d = ImageDraw.Draw(cv); icon(d, (cx, ytop + 200), ic, 130, P['acc_ink'])
        d.text((cx, ytop + 340), t, font=fitf(d, t, BOLD, 44, cw - 70), fill=P['acc_ink'], anchor='ma')
    return cv

def s_specs(v):
    P = v.pal; cv = studio(v); head(cv, v, 'Характеристики')
    put(cv, v, (560, 330, 1240, 960), 'b', a=0.3)
    rows = v.p['specs'] + [('Цвет', v.v['color'])]
    d = ImageDraw.Draw(cv); y0 = 1060; rh = min(112, int(1240 / len(rows)))
    card(cv, (100, y0 - 20, 1700, y0 + rh * len(rows) + 20), P, 40); d = ImageDraw.Draw(cv)
    for i, (a, b) in enumerate(rows):
        yy = y0 + i * rh + rh / 2
        if i: d.line([(160, y0 + i * rh), (1640, y0 + i * rh)], fill=(230, 222, 214) if not P['dark'] else (90, 84, 80), width=2)
        d.text((170, yy), a, font=F(BODY, 42), fill=P['sub'], anchor='lm')
        d.text((1630, yy), b, font=fitf(d, b, BOLD, 44, 960), fill=P['ink'], anchor='rm')
    return cv

def render(p, v, outdir):
    os.makedirs(outdir, exist_ok=True); X = V(p, v)
    sib = [(x['key'], x['color']) for x in p['variants']]
    cov = COVERS[p.get('cover_i', p['n'] % 4)](X)
    slides = [cov, s_sizes(X), s_fits(X), s_scene(X), s_callouts(X), s_macro(X), s_colors(X, sib), s_specs(X)]
    for i, s in enumerate(slides): save(s, f'{outdir}/{i + 1:02d}.jpg')
    return len(slides)
