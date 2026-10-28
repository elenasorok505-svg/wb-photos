"""Графика для карточек ковриков v2: фоны (студия-подиум, тёмный карбон со «свушами», светлая геометрия, гараж),
схема авто сверху, бейджи, плашки. Холст 1800×2400."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import sys
sys.path.insert(0, '/home/claude/mass')
from render_m2 import F, tw, fitf, wrap, icon, W, H

def rgba(c, a=255): return tuple(c[:3]) + (a,)
def mixc(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def vlin(w, h, top, bot, curve=1.0):
    t = (np.linspace(0, 1, h) ** curve)[:, None]
    a = np.array(top, np.float32)[None] * (1 - t) + np.array(bot, np.float32)[None] * t
    return Image.fromarray(np.repeat(a[:, None, :], w, 1).astype('uint8'), 'RGB')

def radial_img(w, h, cx, cy, r, inner, outer, power=1.6):
    yy, xx = np.mgrid[0:h:2, 0:w:2]
    d = np.clip(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r, 0, 1) ** power
    a = np.array(inner, np.float32)[None, None] * (1 - d[..., None]) + np.array(outer, np.float32)[None, None] * d[..., None]
    return Image.fromarray(a.astype('uint8'), 'RGB').resize((w, h), Image.BILINEAR)

def glow(cv, cx, cy, r, col, a=160):
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    g = (a * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / float(r * r) * 1.8)).astype('uint8')
    lay = Image.new('RGBA', (W, H), rgba(col, 0)); lay.putalpha(Image.fromarray(g).resize((W, H), Image.BILINEAR)); cv.alpha_composite(lay)

def noise_over(cv, amt=6, seed=0):
    rng = np.random.default_rng(seed); n = rng.normal(0, amt, (H // 2, W // 2)).astype(np.float32)
    n = Image.fromarray(np.clip(n + 128, 0, 255).astype('uint8')).resize((W, H), Image.BILINEAR)
    base = cv.convert('RGB'); arr = np.asarray(base).astype(np.int16) + (np.asarray(n).astype(np.int16) - 128)[..., None]
    cv.paste(Image.fromarray(np.clip(arr, 0, 255).astype('uint8')).convert('RGBA'), (0, 0))

def poly_grad(cv, pts, c0, c1, a0=255, a1=255, vertical=False, blur=0):
    """полигон с линейной заливкой по x (или y)"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = int(min(xs)), int(max(xs)) + 1, int(min(ys)), int(max(ys)) + 1
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    if vertical: t = np.linspace(0, 1, h)[:, None].repeat(w, 1)
    else: t = np.linspace(0, 1, w)[None, :].repeat(h, 0)
    col = np.array(c0, np.float32)[None, None] * (1 - t[..., None]) + np.array(c1, np.float32)[None, None] * t[..., None]
    al = (a0 * (1 - t) + a1 * t)
    im = Image.fromarray(np.dstack([col, al]).astype('uint8'), 'RGBA')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    if blur: m = m.filter(ImageFilter.GaussianBlur(blur))
    im.putalpha(ImageChops.multiply(im.split()[3], m))
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); lay.paste(im, (x0, y0)); cv.alpha_composite(lay)

def soft_shadow(cv, mask_img, x, y, blur=40, a=0.55, dx=0, dy=40, squash=1.0):
    al = mask_img.split()[3]
    if squash != 1.0: al = al.resize((al.width, max(1, int(al.height * squash))))
    pad = blur * 3; big = Image.new('L', (al.width + 2 * pad, al.height + 2 * pad), 0); big.paste(al.point(lambda v: int(v * a)), (pad, pad))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', big.size, (0, 0, 0, 255)); sh.putalpha(big)
    paste_clip(cv, sh, x - pad + dx, y - pad + dy + (mask_img.height - al.height))

def paste_clip(cv, im, x, y):
    x, y = int(x), int(y)
    x0, y0 = max(0, -x), max(0, -y); x1, y1 = min(im.width, cv.width - x), min(im.height, cv.height - y)
    if x1 <= x0 or y1 <= y0: return
    cv.alpha_composite(im.crop((x0, y0, x1, y1)), (x + x0, y + y0))

def fit(im, bw, bh, up_sharp=True):
    s = min(bw / im.width, bh / im.height)
    r = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    if s > 1.15 and up_sharp: r = r.filter(ImageFilter.UnsharpMask(2.0, 70, 2))
    return r

def place_prod(cv, cut, box, shadow='floor', anchor='c', contact=True):
    x0, y0, x1, y1 = [int(v) for v in box]
    p = fit(cut, x1 - x0, y1 - y0)
    a = p.split()[3].point(lambda v: 0 if v < 40 else v); p.putalpha(a)
    x = x0 + (x1 - x0 - p.width) // 2
    y = y0 + (y1 - y0 - p.height) // 2 if anchor == 'c' else (y1 - p.height)
    if shadow:
        soft_shadow(cv, p, x, y, blur=46, a=0.6, dx=10, dy=48)
        if contact: soft_shadow(cv, p, x, y, blur=12, a=0.45, dx=4, dy=14)
    cv.alpha_composite(p, (x, y))
    return x, y, p

def cover_crop(im, w, h, fx=0.5, fy=0.5):
    s = max(w / im.width, h / im.height); r = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    x = int((r.width - w) * fx); y = int((r.height - h) * fy); r = r.crop((x, y, x + w, y + h))
    return r.filter(ImageFilter.UnsharpMask(1.8, 60, 2)) if s > 1.2 else r

# ---------------- фоны ----------------
def bg_studio(seed=0, warm=True):
    """светлая студия: стена + пол + подиум из двух блоков"""
    wall_t, wall_b = ((244, 242, 238), (220, 216, 210)) if warm else ((240, 242, 245), (212, 216, 222))
    cv = vlin(W, H, wall_t, wall_b).convert('RGBA')
    fy = int(H * 0.62)
    floor = vlin(W, H - fy, mixc(wall_b, (190, 184, 176) if warm else (182, 188, 196), 0.5), (200, 194, 186) if warm else (196, 200, 208)).convert('RGBA')
    cv.alpha_composite(floor, (0, fy))
    # мягкий горизонт
    hz = Image.new('RGBA', (W, 160), (255, 255, 255, 0)); d = ImageDraw.Draw(hz); d.rectangle((0, 70, W, 90), fill=(255, 255, 255, 110))
    cv.alpha_composite(hz.filter(ImageFilter.GaussianBlur(30)), (0, fy - 80))
    glow(cv, W * 0.62, H * 0.32, 900, (255, 255, 255), 150)
    # окно-свет (диагональные лучи)
    for k in range(3):
        x = 1050 + k * 230
        poly_grad(cv, [(x, 0), (x + 120, 0), (x - 380, fy), (x - 520, fy)], (255, 255, 255), (255, 255, 255), 40, 0, vertical=True, blur=30)
    return cv, fy

def podium(cv, cx, top_y, w, h, warm=True, two=True):
    """блоки-подиум: верхняя грань светлее, фронт темнее, тень на полу"""
    base = (226, 221, 214) if warm else (222, 225, 230)
    def block(x0, y0, bw, bh, depth=60):
        sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 - 30, y0 + bh - 20, x0 + bw + 60, y0 + bh + 60), 40, fill=(0, 0, 0, 120))
        cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
        poly_grad(cv, [(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh), (x0, y0 + bh)], mixc(base, (0, 0, 0), 0.06), mixc(base, (0, 0, 0), 0.16), vertical=True)
        poly_grad(cv, [(x0 + depth, y0 - depth * 0.6), (x0 + bw + depth, y0 - depth * 0.6), (x0 + bw, y0), (x0, y0)], mixc(base, (255, 255, 255), 0.5), base, vertical=True)
        poly_grad(cv, [(x0 + bw, y0), (x0 + bw + depth, y0 - depth * 0.6), (x0 + bw + depth, y0 + bh - depth * 0.6), (x0 + bw, y0 + bh)], mixc(base, (0, 0, 0), 0.22), mixc(base, (0, 0, 0), 0.3))
    if two:
        block(cx - w * 0.62, top_y + h * 0.42, w * 0.7, h * 0.58)
        block(cx - w * 0.1, top_y, w * 0.62, h)
    else:
        block(cx - w / 2, top_y, w, h)

def hex_pattern(w, h, r=26, col=(255, 255, 255), a=14, width=2):
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    dx = r * math.sqrt(3); dy = r * 1.5
    for j in range(int(h / dy) + 2):
        for i in range(int(w / dx) + 2):
            cx = i * dx + (dx / 2 if j % 2 else 0); cy = j * dy
            pts = [(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            d.line(pts + [pts[0]], fill=rgba(col, a), width=width)
    return lay

def bg_dark(acc=(226, 32, 40), seed=0, side='both'):
    """тёмный карбон + соты + цветные «свуши» по бокам"""
    cv = radial_img(W, H, W * 0.5, H * 0.45, 1500, (46, 48, 54), (8, 8, 10)).convert('RGBA')
    hp = hex_pattern(W, H, 30, (255, 255, 255), 12)
    m = radial_img(W, H, W * 0.5, H * 0.5, 1300, (40, 40, 40), (255, 255, 255)).convert('L'); hp.putalpha(ImageChops.multiply(hp.split()[3], m))
    cv.alpha_composite(hp)
    # свуши
    if side in ('both', 'l'):
        poly_grad(cv, [(0, 520), (260, 380), (120, 1500), (0, 1700)], acc, mixc(acc, (0, 0, 0), 0.7), 235, 120)
        poly_grad(cv, [(0, 1750), (330, 1400), (200, 2400), (0, 2400)], mixc(acc, (0, 0, 0), 0.2), (10, 10, 12), 220, 80)
        poly_grad(cv, [(300, 380), (340, 360), (170, 1510), (130, 1530)], (255, 255, 255), (255, 255, 255), 120, 0, vertical=True)
    if side in ('both', 'r'):
        poly_grad(cv, [(W, 300), (W, 1250), (W - 160, 1400), (W - 360, 260)], mixc(acc, (0, 0, 0), 0.6), acc, 120, 235)
        poly_grad(cv, [(W, 1500), (W, 2400), (W - 140, 2400), (W - 300, 1650)], (10, 10, 12), mixc(acc, (0, 0, 0), 0.25), 80, 220)
        poly_grad(cv, [(W - 400, 250), (W - 370, 240), (W - 180, 1400), (W - 210, 1420)], (255, 255, 255), (255, 255, 255), 110, 0, vertical=True)
    glow(cv, W * 0.5, H * 0.55, 800, (255, 255, 255), 40)
    return cv

def bg_geo(seed=0, acc=(240, 120, 30)):
    """светло-серый с крупными полупрозрачными «X»-шевронами"""
    cv = vlin(W, H, (238, 239, 241), (214, 216, 220)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for (x, y, s) in ((1300, 900, 900), (200, 1900, 700)):
        d.polygon([(x - s, y - s), (x - s + 220, y - s), (x + s, y + s), (x + s - 220, y + s)], fill=(255, 255, 255, 120))
        d.polygon([(x + s, y - s), (x + s - 220, y - s), (x - s, y + s), (x - s + 220, y + s)], fill=(200, 202, 208, 70))
    cv.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    glow(cv, W * 0.5, H * 0.55, 900, (255, 255, 255), 120)
    return cv

def bg_garage(acc=(60, 140, 255)):
    """тёмно-синий «шоурум»: пол с отражением, световые полосы сверху"""
    cv = vlin(W, H, (18, 24, 36), (6, 8, 12)).convert('RGBA')
    fy = int(H * 0.66)
    poly_grad(cv, [(0, fy), (W, fy), (W, H), (0, H)], (30, 38, 54), (8, 10, 14), 255, 255, vertical=True)
    for k, x in enumerate((300, 900, 1500)):
        poly_grad(cv, [(x - 160, 0), (x + 160, 0), (x + 60, 40), (x - 60, 40)], (255, 255, 255), (255, 255, 255), 200, 200)
        poly_grad(cv, [(x - 60, 40), (x + 60, 40), (x + 420, fy), (x - 420, fy)], acc, acc, 70, 0, vertical=True, blur=40)
    glow(cv, W * 0.5, fy, 900, acc, 90)
    return cv, fy

# ---------------- схема авто сверху ----------------
def car_top(cv, cx, cy, L=1500, Wd=700, body=(70, 74, 82), hl=None, zones=('fl', 'fr', 'r'), zone_col=(240, 140, 30), mats_rgb=(30, 30, 32), label=True, fnt=None):
    """стилизованный автомобиль вид сверху; подсвеченные зоны ковриков"""
    x0, y0 = cx - Wd / 2, cy - L / 2
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # тень
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0 + 20, y0 + 40, x0 + Wd + 20, y0 + L + 40), radius=Wd * 0.38, fill=(0, 0, 0, 150))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
    # колёса
    for wx, wy in ((x0 - 22, y0 + L * 0.17), (x0 + Wd - 48, y0 + L * 0.17), (x0 - 22, y0 + L * 0.74), (x0 + Wd - 48, y0 + L * 0.74)):
        d.rounded_rectangle((wx, wy, wx + 70, wy + L * 0.12), 22, fill=(16, 16, 18, 255))
    cv.alpha_composite(lay); lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # кузов
    body_box = (x0, y0, x0 + Wd, y0 + L)
    m = Image.new('L', cv.size, 0); ImageDraw.Draw(m).rounded_rectangle(body_box, radius=Wd * 0.38, fill=255)
    grad = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    g = np.linspace(0, 1, int(Wd))[None, :]; prof = 1 - 0.55 * np.abs(g - 0.5) * 2
    col = (np.array(body, np.float32)[None, None] * (0.55 + 0.75 * prof[..., None]))
    gi = Image.fromarray(np.clip(np.repeat(col, int(L), 0), 0, 255).astype('uint8'), 'RGB').convert('RGBA')
    grad.paste(gi, (int(x0), int(y0))); grad.putalpha(m); cv.alpha_composite(grad)
    d = ImageDraw.Draw(cv)
    # стёкла
    glass = (28, 34, 44)
    d.polygon([(x0 + Wd * 0.14, y0 + L * 0.27), (x0 + Wd * 0.86, y0 + L * 0.27), (x0 + Wd * 0.78, y0 + L * 0.34), (x0 + Wd * 0.22, y0 + L * 0.34)], fill=glass)
    d.polygon([(x0 + Wd * 0.2, y0 + L * 0.8), (x0 + Wd * 0.8, y0 + L * 0.8), (x0 + Wd * 0.86, y0 + L * 0.86), (x0 + Wd * 0.14, y0 + L * 0.86)], fill=glass)
    # салон (крыша прозрачная — видно пол)
    ix0, ix1 = x0 + Wd * 0.12, x0 + Wd * 0.88; iy0, iy1 = y0 + L * 0.35, y0 + L * 0.79
    d.rounded_rectangle((ix0, iy0, ix1, iy1), 40, fill=(214, 216, 220))
    # сиденья
    seat = (150, 154, 162)
    for sx in (ix0 + 30, cx + 20):
        d.rounded_rectangle((sx, iy0 + 40, sx + (ix1 - ix0) / 2 - 50, iy0 + 150), 26, fill=seat)
    d.rounded_rectangle((ix0 + 30, iy0 + (iy1 - iy0) * 0.56, ix1 - 30, iy0 + (iy1 - iy0) * 0.56 + 110), 26, fill=seat)
    d.rounded_rectangle((cx - 40, iy0 + 30, cx + 40, iy0 + (iy1 - iy0) * 0.45), 18, fill=(120, 124, 130))
    # зоны ковриков
    zb = {'fl': (ix0 + 30, iy0 + 170, cx - 50, iy0 + (iy1 - iy0) * 0.5),
          'fr': (cx + 50, iy0 + 170, ix1 - 30, iy0 + (iy1 - iy0) * 0.5),
          'r': (ix0 + 30, iy0 + (iy1 - iy0) * 0.56 + 130, ix1 - 30, iy1 - 30),
          't': (x0 + Wd * 0.16, y0 + L * 0.87, x0 + Wd * 0.84, y0 + L * 0.97)}
    if 't' in zones: d.rounded_rectangle(zb['t'], 30, fill=(214, 216, 220))
    for z in zones:
        bx = zb[z]
        d.rounded_rectangle(bx, 26, fill=mats_rgb, outline=zone_col, width=12)
    # фары
    d.rounded_rectangle((x0 + Wd * 0.1, y0 + 22, x0 + Wd * 0.3, y0 + 60), 18, fill=(250, 250, 240))
    d.rounded_rectangle((x0 + Wd * 0.7, y0 + 22, x0 + Wd * 0.9, y0 + 60), 18, fill=(250, 250, 240))
    d.rounded_rectangle((x0 + Wd * 0.08, y0 + L - 50, x0 + Wd * 0.3, y0 + L - 20), 14, fill=(220, 40, 40))
    d.rounded_rectangle((x0 + Wd * 0.7, y0 + L - 50, x0 + Wd * 0.92, y0 + L - 20), 14, fill=(220, 40, 40))
    return zb

# ---------------- бейджи ----------------
def badge_square(cv, x, y, s, big, small, bg, fg, font_big, font_small):
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x + 8, y + 20, x + s + 8, y + s + 20), 40, fill=(0, 0, 0, 110))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(cv); d.rounded_rectangle((x, y, x + s, y + s), 40, fill=bg)
    fb = fitf(d, big, font_big, int(s * 0.5), s * 0.8); d.text((x + s / 2, y + s * 0.4), big, font=fb, fill=fg, anchor='mm')
    ls = wrap(d, small.upper(), F(font_small, int(s * 0.11)), s * 0.84)[:2]; yy = y + s * 0.72
    for ln in ls: d.text((x + s / 2, yy), ln, font=F(font_small, int(s * 0.11)), fill=fg, anchor='mm'); yy += s * 0.13

def badge_circle(cv, cx, cy, r, big, small, bg, fg, font_big, font_small, ring=None):
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - r + 8, cy - r + 20, cx + r + 8, cy + r + 20), fill=(0, 0, 0, 120))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(cv); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    if ring: d.ellipse((cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14), outline=ring, width=6)
    fb = fitf(d, big, font_big, int(r * 0.95), r * 1.5); d.text((cx, cy - r * 0.18), big, font=fb, fill=fg, anchor='mm')
    ls = wrap(d, small, F(font_small, int(r * 0.2)), r * 1.5)[:2]; yy = cy + r * 0.38
    for ln in ls: d.text((cx, yy), ln, font=F(font_small, int(r * 0.2)), fill=fg, anchor='mm'); yy += r * 0.23

def tex_circle(cv, im, cx, cy, r, ring=(255, 255, 255), rw=10):
    t = im.resize((2 * r, 2 * r), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 70, 2)).convert('RGBA')
    m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255); t.putalpha(m)
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - r + 6, cy - r + 18, cx + r + 6, cy + r + 18), fill=(0, 0, 0, 120))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    cv.alpha_composite(t, (int(cx - r), int(cy - r)))
    ImageDraw.Draw(cv).ellipse((cx - r, cy - r, cx + r, cy + r), outline=ring, width=rw)

def hl_text(cv, x, y, text, font, fg, hl, padx=24, pady=6, anchor='l'):
    """текст с цветной «маркерной» подложкой"""
    d = ImageDraw.Draw(cv); b = d.textbbox((0, 0), text, font=font)
    w, h = b[2] - b[0], b[3] - b[1]
    if anchor == 'm': x -= w / 2 + padx
    d.rounded_rectangle((x, y + h * 0.35 - pady + b[1] * 0.0, x + w + 2 * padx, y + b[3] + pady), 14, fill=hl)
    d.text((x + padx - b[0], y), text, font=font, fill=fg)
    return w + 2 * padx, b[3]

def feature_strip(cv, x0, y0, x1, y1, items, ink, sub, acc, fb, fr, dark=False):
    """белая (или тёмная) плашка с 3 иконками и разделителями"""
    sh = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 16, x1, y1 + 16), 44, fill=(0, 0, 0, 90))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)))
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle((x0, y0, x1, y1), 44, fill=(18, 18, 22, 225) if dark else (255, 255, 255, 236)); cv.alpha_composite(lay)
    d = ImageDraw.Draw(cv); n = len(items); cw = (x1 - x0) / n
    for i, (ic, t) in enumerate(items):
        cx = x0 + cw * i
        if i: d.line([(cx, y0 + 40), (cx, y1 - 40)], fill=(220, 220, 224) if not dark else (70, 70, 76), width=3)
        icon(d, (cx + 90, (y0 + y1) / 2), ic, 92, acc)
        ls = wrap(d, t, F(fb, 40), cw - 190)[:3]; yy = (y0 + y1) / 2 - len(ls) * 24
        for ln in ls: d.text((cx + 160, yy), ln, font=F(fb, 40), fill=ink); yy += 48
