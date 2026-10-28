"""Электромассажёры v2: инфографика в стиле топ-карточек WB.
Рисуем в 1800×2400 и уменьшаем до 900×1200 (сглаживание текста и линий).
Товар крупно по центру, свечение, крупные цифры-бейджи, выноски, эффект, детали крупно, иконки. Без деления кадра на две половины."""
import os, sys, math, colorsys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
sys.path.insert(0, '/home/claude/mass')
from tdef import TD
from meta import M

W, H = 1800, 2400
FD = '/home/claude/fonts2/ttf'
ICON = json.load(open('/home/claude/mass/icons/mdi.json'))
_fc = {}
def F(n, s):
    k = (n, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype('/home/claude/mass/icons/mdi.ttf' if n == 'mdi' else f'{FD}/{n}.ttf', s)
    return _fc[k]
def tw(d, t, f): b = d.textbbox((0, 0), t, font=f); return b[2] - b[0]
def th(d, t, f): b = d.textbbox((0, 0), t, font=f); return b[3] - b[1]
def fitf(d, t, n, s, mw, mn=20):
    while s > mn and tw(d, t, F(n, s)) > mw: s -= 2
    return F(n, s)
def wrap(d, text, f, mw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if tw(d, t, f) <= mw: cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
def tint(c, k): return tuple(int(v + (255 - v) * k) for v in c) if k > 0 else tuple(int(v * (1 + k)) for v in c)
def mix(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
def hls(h, l, s): r, g, b = colorsys.hls_to_rgb(h % 1, l, s); return (int(r * 255), int(g * 255), int(b * 255))
def plural(n, a, b, c):
    n = abs(int(n)) % 100
    if 11 <= n <= 19: return c
    n %= 10
    return a if n == 1 else (b if 2 <= n <= 4 else c)

def icon(d, xy, name, size, col, anchor='mm'):
    ch = chr(int(ICON.get(name, ICON['check-circle']), 16))
    d.text(xy, ch, font=F('mdi', size), fill=col, anchor=anchor)

# ---------- палитры (как у топовых карточек WB) ----------
PAL = [
 dict(n='navy',   top=(18, 20, 48),  bot=(52, 38, 110), acc=(150, 110, 255), ink=(255, 255, 255), sub=(205, 200, 235), dark=True,  card=(255, 255, 255, 26)),
 dict(n='red',    top=(196, 32, 38), bot=(120, 12, 20), acc=(255, 255, 255), ink=(255, 255, 255), sub=(255, 220, 220), dark=True,  card=(255, 255, 255, 34)),
 dict(n='graph',  top=(34, 34, 38),  bot=(12, 12, 14),  acc=(232, 40, 46),  ink=(255, 255, 255), sub=(200, 200, 205), dark=True,  card=(255, 255, 255, 22)),
 dict(n='terra',  top=(186, 92, 70), bot=(140, 60, 48), acc=(255, 236, 220), ink=(255, 255, 255), sub=(255, 228, 214), dark=True,  card=(255, 255, 255, 36)),
 dict(n='cream',  top=(250, 244, 236), bot=(232, 220, 204), acc=(150, 96, 60), ink=(44, 32, 26), sub=(110, 90, 76), dark=False, card=(255, 255, 255, 220)),
 dict(n='pink',   top=(255, 150, 196), bot=(232, 70, 140), acc=(255, 255, 255), ink=(255, 255, 255), sub=(255, 236, 244), dark=True, card=(255, 255, 255, 40)),
 dict(n='emer',   top=(14, 70, 60),  bot=(6, 34, 30),   acc=(214, 182, 110), ink=(255, 255, 255), sub=(200, 226, 214), dark=True,  card=(255, 255, 255, 24)),
 dict(n='ice',    top=(236, 242, 250), bot=(196, 214, 238), acc=(40, 92, 210), ink=(18, 30, 60), sub=(80, 96, 130), dark=False, card=(255, 255, 255, 225)),
 dict(n='brown',  top=(92, 52, 34),  bot=(46, 24, 16),  acc=(232, 186, 120), ink=(255, 248, 238), sub=(232, 210, 190), dark=True, card=(255, 255, 255, 26)),
 dict(n='teal',   top=(0, 128, 140), bot=(0, 70, 86),   acc=(255, 214, 90), ink=(255, 255, 255), sub=(200, 240, 240), dark=True,  card=(255, 255, 255, 30)),
 dict(n='lilac',  top=(244, 238, 255), bot=(214, 200, 246), acc=(112, 70, 220), ink=(36, 22, 70), sub=(96, 80, 130), dark=False, card=(255, 255, 255, 225)),
 dict(n='orange', top=(255, 140, 40), bot=(226, 80, 20), acc=(255, 255, 255), ink=(255, 255, 255), sub=(255, 236, 214), dark=True, card=(255, 255, 255, 40)),
]
FONTS = [('unbounded-800', 'montserrat-600', 'montserrat-800', True), ('oswald-700', 'rubik-500', 'rubik-800', True),
         ('russo-one-400', 'exo-2-600', 'exo-2-800', True), ('manrope-800', 'manrope-500', 'manrope-800', False),
         ('rubik-800', 'rubik-500', 'rubik-800', False), ('montserrat-800', 'montserrat-600', 'montserrat-800', True),
         ('exo-2-800', 'manrope-500', 'manrope-800', True), ('playfair-display-900', 'manrope-500', 'manrope-800', False),
         ('jost-700', 'jost-500', 'jost-700', True), ('nunito-900', 'nunito-600', 'nunito-900', False)]

def lin(top, bot, w=W, h=H):
    t = np.linspace(0, 1, h)[:, None]; a = np.array(top)[None] * (1 - t) + np.array(bot)[None] * t
    return Image.fromarray(np.repeat(a[:, None, :], w, 1).astype('uint8'), 'RGB').convert('RGBA')

def glow(cv, cx, cy, r, col, a=200, squash=1.0):
    g = Image.new('L', (W, H), 0); d = ImageDraw.Draw(g)
    d.ellipse((cx - r, cy - r * squash, cx + r, cy + r * squash), fill=a)
    g = g.filter(ImageFilter.GaussianBlur(r * 0.45))
    layer = Image.new('RGBA', (W, H), col + (0,)); layer.putalpha(g); cv.alpha_composite(layer)

def rays(cv, cx, cy, col, n=18, a=26):
    g = Image.new('L', (W, H), 0); d = ImageDraw.Draw(g)
    for i in range(n):
        t = 2 * math.pi * i / n; t2 = t + math.pi / n * 0.6
        d.polygon([(cx, cy), (cx + 2600 * math.cos(t), cy + 2600 * math.sin(t)), (cx + 2600 * math.cos(t2), cy + 2600 * math.sin(t2))], fill=a)
    g = g.filter(ImageFilter.GaussianBlur(6))
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((cx - 1100, cy - 1100, cx + 1100, cy + 1100), fill=255); m = m.filter(ImageFilter.GaussianBlur(300))
    g = ImageChops.multiply(g, m)
    layer = Image.new('RGBA', (W, H), col + (0,)); layer.putalpha(g); cv.alpha_composite(layer)

def fitim(im, bw, bh):
    s = min(bw / im.width, bh / im.height)
    r = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return r.filter(ImageFilter.UnsharpMask(radius=2.2, percent=60, threshold=2)) if s > 1.2 else r

def place(cv, im, box, shadow=True, floor=True, anchor='c'):
    x0, y0, x1, y1 = box; p = fitim(im, x1 - x0, y1 - y0)
    x = x0 + (x1 - x0 - p.width) // 2; y = y0 + (y1 - y0 - p.height) // 2 if anchor == 'c' else y1 - p.height
    if floor:
        fl = Image.new('L', (W, H), 0); ImageDraw.Draw(fl).ellipse((x + p.width * 0.12, y + p.height - 30, x + p.width * 0.88, y + p.height + 50), fill=150)
        fl = fl.filter(ImageFilter.GaussianBlur(36)); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.putalpha(fl); cv.alpha_composite(lay)
    if shadow:
        a = p.split()[3]; sh = Image.new('RGBA', p.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * 0.45)))
        pad = 120; big = Image.new('RGBA', (p.width + 2 * pad, p.height + 2 * pad), (0, 0, 0, 0)); big.paste(sh, (pad, pad), sh)
        cv.alpha_composite(big.filter(ImageFilter.GaussianBlur(40)), (x - pad + 10, y - pad + 40))
    cv.alpha_composite(p, (x, y))
    return (x, y, p), p

def rr(cv, box, r, fill):
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(box, radius=r, fill=fill); cv.alpha_composite(lay)

def prod_hls(im):
    a = np.asarray(im.convert('RGBA').resize((90, 90))); px = a[a[..., 3] > 200][:, :3]
    if len(px) == 0: return (0, 0.5, 0)
    q = Image.fromarray(px.reshape(-1, 1, 3).astype('uint8')).quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette(); best, bs = (0, 0.5, 0), -1
    for n, i in q.getcolors():
        r, g, b = pal[i * 3:i * 3 + 3]; h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        sc = s * (n ** 0.5) * (1 - abs(l - 0.5))
        if sc > bs: bs, best = sc, (h, l, s)
    return best

# ---------- тексты эффектов / шагов ----------
EFF = {
 'gun': [('arm-flex', 'Снимает напряжение мышц', 'после тренировок и сидячей работы'), ('run', 'Ускоряет восстановление', 'мышцы быстрее приходят в тонус'),
         ('heart-pulse', 'Разгоняет кровообращение', 'глубокая перкуссия до 10 мм'), ('human-handsup', 'Убирает скованность', 'спина, плечи, ноги')],
 'neck': [('human-handsup', 'Снимает напряжение шеи', 'зажимы после работы за компьютером'), ('fire', 'Согревает мышцы', 'тепло усиливает расслабление'),
          ('heart-pulse', 'Улучшает кровообращение', 'в зоне шеи и плеч'), ('meditation', 'Помогает расслабиться', 'антистресс после трудного дня')],
 'back': [('seat-recline-normal', 'Расслабляет спину', 'после долгого рабочего дня'), ('fire', 'Прогревает поясницу', 'тепло для уставших мышц'),
          ('heart-pulse', 'Улучшает кровообращение', 'разминание глубоких мышц'), ('sleep', 'Помогает отдохнуть', 'как массаж в салоне, но дома')],
 'eye': [('eye', 'Снимает усталость глаз', 'после экрана и чтения'), ('fire', 'Тёплый компресс', 'расслабляет мышцы вокруг глаз'),
         ('sleep', 'Помогает уснуть', 'спокойный ритуал перед сном'), ('meditation', 'Антистресс', 'пауза для себя за 10–15 минут')],
 'eyecare': [('face-woman-shimmer', 'Тонизирует кожу', 'вокруг глаз'), ('water', 'Помогает крему впитаться', 'вибрация и тепло'),
             ('brightness-5', 'Световой уход', 'несколько режимов подсветки'), ('star-four-points', 'Свежий взгляд', 'ежедневный домашний уход')],
 'head': [('head-outline', 'Расслабляет кожу головы', 'как массаж в спа'), ('meditation', 'Снимает стресс', 'приятные «мурашки»'),
          ('heart-pulse', 'Улучшает кровообращение', 'кожи головы'), ('sleep', 'Помогает уснуть', 'ритуал перед сном')],
 'comb': [('head-outline', 'Массаж кожи головы', 'при каждом расчёсывании'), ('water', 'Равномерно наносит средство', 'сыворотку, масло, тоник'),
          ('heart-pulse', 'Стимулирует кровообращение', 'кожи головы'), ('hair-dryer', 'Бережный уход', 'мягкие зубцы не царапают')],
 'legs': [('foot-print', 'Снимает тяжесть в ногах', 'после дня на ногах'), ('water-minus', 'Меньше отёчности к вечеру', 'компрессия от стопы вверх'),
          ('run', 'Восстановление', 'после спорта и прогулок'), ('heart-pulse', 'Улучшает кровообращение', 'мягкое ритмичное сжатие')],
 'hand': [('hand-back-right', 'Снимает усталость рук', 'после работы за компьютером'), ('fire', 'Согревает', 'холодные руки и пальцы'),
          ('heart-pulse', 'Улучшает кровообращение', 'ладони и пальцев'), ('meditation', 'Расслабляет', 'приятный массаж-перерыв')],
 'ems': [('lightning-bolt', 'Импульсный массаж', 'мягкие микротоки расслабляют мышцы'), ('human-handsup', 'Снимает напряжение', 'шея, плечи, спина'),
         ('heart-pulse', 'Улучшает кровообращение', 'в зоне воздействия'), ('meditation', 'Помогает расслабиться', 'в любом месте')],
}
EFFT = dict(gun_mini='gun', gun_hook='gun', gun_full='gun', dolphin='gun', neck_ems='ems', neck_band='neck', pillow='back', pillow_u='neck',
            back_cushion='back', seat='back', shawl='neck', trapez='neck', eye='eye', eye_steam='eye', eye_ems='eyecare', head='head',
            head_wrap='head', comb='comb', foot_machine='legs', leg_boots='legs', leg_calf='legs', hand='hand')
EFF_H = ['Эффект от массажа', 'Что вы почувствуете', 'Результат после сеанса', 'Почему это работает']

USE_ICON = [('компьют', 'laptop'), ('офис', 'briefcase'), ('стол', 'laptop'), ('работ', 'briefcase'), ('дорог', 'airplane'), ('самол', 'airplane'),
            ('перелёт', 'airplane'), ('машин', 'car'), ('автомоб', 'car'), ('сном', 'sleep'), ('сна', 'sleep'), ('трен', 'dumbbell'), ('бег', 'run'),
            ('спорт', 'dumbbell'), ('прогул', 'walk'), ('диван', 'sofa'), ('кресл', 'seat-recline-normal'), ('дома', 'home'), ('телевиз', 'television'),
            ('шея', 'account'), ('плеч', 'human-handsup'), ('спин', 'human'), ('поясн', 'human'), ('ног', 'foot-print'), ('икр', 'foot-print'),
            ('бёдр', 'foot-print'), ('стоп', 'foot-print'), ('рук', 'hand-back-right'), ('голов', 'head-outline'), ('питом', 'paw'), ('крем', 'lotion'),
            ('уход', 'face-woman-shimmer'), ('сыворот', 'water'), ('мыть', 'shower'), ('расчёс', 'hair-dryer'), ('лопат', 'human'), ('обед', 'coffee'),
            ('холод', 'snowflake'), ('рукодел', 'hand-back-right'), ('вечер', 'weather-night'), ('утрен', 'weather-sunny'), ('линз', 'eye'), ('поезд', 'bag-suitcase')]
def use_icon(t):
    tl = t.lower()
    for k, v in USE_ICON:
        if k in tl: return v
    return 'check-circle'

FEAT_ICON = [('подогр', 'fire'), ('прогрев', 'fire'), ('тепл', 'fire'), ('ик-', 'fire'), ('аккум', 'battery-charging'), ('беспровод', 'battery-charging'),
             ('usb', 'usb-port'), ('зарядк', 'battery-charging'), ('bluetooth', 'bluetooth'), ('музык', 'music'), ('дисплей', 'monitor'),
             ('пульт', 'remote'), ('ems', 'lightning-bolt'), ('микроток', 'lightning-bolt'), ('импульс', 'lightning-bolt'), ('свет', 'brightness-5'),
             ('распыл', 'spray'), ('резервуар', 'water'), ('компресс', 'weather-windy'), ('пар', 'weather-fog'), ('насад', 'puzzle'),
             ('голов', 'shape-circle-plus'), ('ролик', 'rotate-3d-variant'), ('пальц', 'hand-back-right'), ('рук', 'hand-back-right'),
             ('вибрац', 'vibrate'), ('режим', 'tune-vertical'), ('уров', 'tune-vertical'), ('скорост', 'speedometer'), ('ручк', 'ruler'),
             ('карман', 'cellphone'), ('мини', 'cellphone'), ('мягк', 'feather'), ('магнит', 'magnet'), ('душ', 'shower'), ('водонепрон', 'water'),
             ('самоочист', 'broom'), ('антистат', 'flash-off'), ('подставк', 'stand'), ('чехол', 'tshirt-crew'), ('пара', 'numeric-2-circle'),
             ('охлажд', 'snowflake'), ('камер', 'weather-windy'), ('петл', 'hand-back-right'), ('стоп', 'foot-print'), ('3 в 1', 'numeric-3-circle'),
             ('2 в 1', 'numeric-2-circle'), ('электрод', 'lightning-bolt'), ('программ', 'tune-vertical'), ('ударн', 'hammer'), ('шиацу', 'rotate-3d-variant')]
def feat_icon(t):
    tl = t.lower()
    for k, v in FEAT_ICON:
        if k in tl: return v
    return 'check-decagram'

TYPEOF = {}

class Card:
    def __init__(self, n, sel, cuts):
        o, ims, color, vk, note = sel
        self.n, self.o, self.color, self.cuts = n, o, color, cuts
        self.ty = TYPEOF[n]; self.td = TD[self.ty]; self.m = M.get(o, {})
        h, l, s = prod_hls(cuts[0]); self.ph = (h, l, s)
        self.p = dict(PAL[(n * 7 + n // 5) % len(PAL)])
        # если товар почти сливается с фоном — сдвигаем палитру
        bgm = mix(self.p['top'], self.p['bot'], 0.5)
        prod_l = l * 255
        if abs(prod_l - lum(bgm)) < 45 and s < 0.25: self.p = dict(PAL[(n * 7 + n // 5 + 3) % len(PAL)])
        f = FONTS[(n * 3 + n // 7) % len(FONTS)]
        self.tf, self.bf, self.bb, self.caps = f
        self.lay = dict(cover=(n + n // 9) % 4, call=(n * 2 + n // 4) % 2, eff=(n + n // 3) % 2, how=(n * 3) % 2)
        self.name = self.m.get('name') or self.td['name']
        self.title = self.m.get('title') or self.td['name']
        self.feats = self.m.get('feats') or self.td['feats']
        self.ben = self.m.get('ben') or self.td['ben']
        self.use = self.m.get('use') or self.td['use']
        self.ink, self.sub, self.acc, self.dark = self.p['ink'], self.p['sub'], self.p['acc'], self.p['dark']
        self.ta = (30, 24, 20) if lum(self.acc) > 160 else (255, 255, 255)
    def T(self, s): return s.upper() if self.caps else s
    def TF(self, s): return F(self.tf, s)
    def BF(self, s): return F(self.bf, s)
    def BB(self, s): return F(self.bb, s)
    def bg(self): return lin(self.p['top'], self.p['bot'])
    def badges(self):
        out = []; m = self.m
        if m.get('modes'): out.append((str(m['modes']), plural(m['modes'], 'режим', 'режима', 'режимов'), None))
        if m.get('heads'): out.append((str(m['heads']), plural(m['heads'], 'насадка', 'насадки', 'насадок') if 'gun' in self.ty or 'head' in self.ty or self.ty == 'dolphin' else plural(m['heads'], 'массажная головка', 'массажные головки', 'массажных головок'), None))
        for t in self.feats:
            if len(out) >= 3: break
            if any(ch.isdigit() for ch in t) and (m.get('modes') and str(m['modes']) in t or m.get('heads') and str(m['heads']) in t): continue
            out.append((None, t, feat_icon(t)))
        return out[:3]

def title_block(c, d, x, y, mw, text, ms, col, align='l', maxl=3, font=None):
    font = font or c.tf; s = ms; lines = wrap(d, text, F(font, s), mw)
    while (len(lines) > maxl or any(tw(d, l, F(font, s)) > mw for l in lines)) and s > 50:
        s -= 4; lines = wrap(d, text, F(font, s), mw)
    f = F(font, s); lh = int(s * 1.1)
    for ln in lines:
        xx = x if align == 'l' else x + (mw - tw(d, ln, f)) / 2
        d.text((xx, y), ln, font=f, fill=col); y += lh
    return y

def badge(c, cv, x, y, b, w=330, h=170, style=0):
    num, cap, ic = b
    fill = c.p['card'] if style == 0 else c.acc + (255,)
    tc = c.ink if style == 0 and c.dark else ((30, 24, 20) if style == 0 else c.ta)
    if style == 0 and not c.dark: tc = c.ink
    rr(cv, (x, y, x + w, y + h), 40, fill)
    d = ImageDraw.Draw(cv)
    if num:
        fn = F(c.bb, 96); d.text((x + 34, y + h / 2), num, font=fn, fill=c.acc if style == 0 else c.ta, anchor='lm')
        nx = x + 44 + tw(d, num, fn)
    else:
        icon(d, (x + 76, y + h / 2), ic, 76, c.acc if style == 0 else c.ta); nx = x + 136
    ls = wrap(d, cap, F(c.bb, 34), x + w - nx - 20)[:3]
    while len(ls) > 3 or (ls and tw(d, ls[0], F(c.bb, 34)) > x + w - nx - 20): break
    fs = 34 if len(ls) <= 2 else 28; ls = wrap(d, cap, F(c.bb, fs), x + w - nx - 20)[:3]
    yy = y + h / 2 - len(ls) * fs * 1.12 / 2
    for ln in ls: d.text((nx, yy), ln, font=F(c.bb, fs), fill=tc); yy += fs * 1.12
    return h

def color_pill(c, d, x, y, center=False):
    t = f'Цвет: {c.color}'; f = F(c.bf, 40); w = tw(d, t, f) + 80
    if center: x = (W - w) / 2
    d.rounded_rectangle((x, y, x + w, y + 80), radius=40, outline=c.sub, width=3)
    d.text((x + 40, y + 40), t, font=f, fill=c.sub, anchor='lm')

# ---------- 1. обложка ----------
def s_cover(c):
    L = c.lay['cover']; im = c.cuts[0]; head = c.T(c.title); bs = c.badges()
    cv = c.bg(); d = ImageDraw.Draw(cv)
    if L == 0:   # заголовок сверху, товар огромный со свечением, бейджи-плитки снизу
        y = title_block(c, d, 100, 110, W - 200, head, 128, c.ink, align='c', maxl=3)
        glow(cv, W // 2, 1250, 640, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=170)
        place(cv, im, (150, y + 60, W - 150, 1850))
        n = len(bs); bw = (W - 200 - 40 * (n - 1)) // max(n, 1)
        for i, b in enumerate(bs): badge(c, cv, 100 + i * (bw + 40), 1930, b, w=bw, h=190)
        d = ImageDraw.Draw(cv); color_pill(c, d, 0, 2210, center=True)
    elif L == 1:  # товар во весь кадр, бейджи слева столбцом поверх, плашка с названием снизу
        glow(cv, W // 2 + 120, 1050, 760, tint(c.acc, 0.25) if c.dark else (255, 255, 255), a=190)
        rays(cv, W // 2 + 120, 1050, (255, 255, 255), a=22 if c.dark else 40)
        place(cv, im, (260, 160, W - 60, 1760))
        for i, b in enumerate(bs): badge(c, cv, 80, 200 + i * 220, b, w=480, h=190, style=0)
        rr(cv, (0, 1840, W, H), 0, c.acc + (255,)); d = ImageDraw.Draw(cv)
        y = title_block(c, d, 90, 1900, W - 180, head, 104, c.ta, maxl=3)
        d.text((92, min(y + 30, H - 90)), f'Цвет: {c.color}', font=F(c.bf, 44), fill=c.ta)
    elif L == 2:  # подиум, заголовок сверху, свойства строкой снизу
        y = title_block(c, d, 100, 110, W - 200, head, 120, c.ink, align='c', maxl=3)
        pod = tint(c.acc, 0.35) if c.dark else tint(c.acc, 0.55)
        glow(cv, W // 2, 1250, 620, tint(c.acc, 0.4), a=150)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.ellipse((260, 1720, W - 260, 1960), fill=pod + (255,)); dl.ellipse((260, 1700, W - 260, 1930), fill=tint(pod, 0.25) + (255,))
        cv.alpha_composite(lay)
        place(cv, im, (220, y + 60, W - 220, 1810), floor=False, anchor='b'); d = ImageDraw.Draw(cv)
        xx = 100; f = F(c.bb, 42); items = c.feats
        tot = sum(tw(d, t, f) + 150 for t in items) - 40
        xx = (W - tot) / 2 if tot < W - 120 else 60
        for t in items:
            w = tw(d, t, f) + 110
            if xx + w > W - 40: break
            rr(cv, (xx, 2030, xx + w, 2130), 50, c.p['card']); d = ImageDraw.Draw(cv)
            icon(d, (xx + 52, 2080), feat_icon(t), 48, c.acc); d.text((xx + 90, 2080), t, font=f, fill=c.ink, anchor='lm'); xx += w + 40
        color_pill(c, d, 0, 2210, center=True)
    else:  # L3: тёмная сцена, заголовок слева сверху, бейджи справа, товар крупно снизу
        glow(cv, W // 2, 1450, 700, tint(c.acc, 0.2) if c.dark else (255, 255, 255), a=180)
        y = title_block(c, d, 100, 120, W - 200, head, 118, c.ink, maxl=3)
        d.rectangle((100, y + 30, 260, y + 42), fill=c.acc)
        place(cv, im, (100, y + 130, W - 100, 2150))
        for i, b in enumerate(bs): badge(c, cv, W - 560, y + 140 + i * 210, b, w=480, h=180, style=1 if i == 0 else 0)
        d = ImageDraw.Draw(cv); color_pill(c, d, 100, 2230)
    return cv

# ---------- 2. выноски «Возможности» ----------
def edge_points(p, ox, oy, fr):
    a = np.asarray(p.split()[3]) > 60; pts = []
    for f in fr:
        y = int(p.height * f); row = np.where(a[y])[0]
        if len(row) == 0: row = np.array([p.width // 2])
        pts.append(((ox + row[0], oy + y), (ox + row[-1], oy + y)))
    return pts

def s_call(c):
    im = c.cuts[0]; cv = c.bg(); d = ImageDraw.Draw(cv); ben = c.ben[:4]
    head = c.T(['Возможности', 'Что умеет', 'Функции', 'Преимущества'][c.n % 4])
    title_block(c, d, 100, 100, W - 200, head, 120, c.ink, align='c', maxl=1)
    glow(cv, W // 2, 1300, 560, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=170)
    (ox, oy, p), _ = place(cv, im, (560, 420, W - 560, 2150))
    d = ImageDraw.Draw(cv)
    pts = edge_points(p, ox, oy, [0.3, 0.7])
    slots = [('l', 520, pts[0][0]), ('r', 520, pts[0][1]), ('l', 1500, pts[1][0]), ('r', 1500, pts[1][1])]
    for (side, y, pt), (t, s) in zip(slots, ben):
        x0 = 70 if side == 'l' else W - 70 - 470
        rr(cv, (x0, y - 40, x0 + 470, y + 360), 36, c.p['card']); d = ImageDraw.Draw(cv)
        d.ellipse((x0 + 30, y - 10, x0 + 150, y + 110), fill=c.acc)
        icon(d, (x0 + 90, y + 50), feat_icon(t + ' ' + s), 70, c.ta)
        yy = y + 140
        for ln in wrap(d, t, F(c.bb, 44), 410)[:3]: d.text((x0 + 30, yy), ln, font=F(c.bb, 44), fill=c.ink); yy += 52
        for ln in wrap(d, s, F(c.bf, 34), 410)[:3]: d.text((x0 + 30, yy + 8), ln, font=F(c.bf, 34), fill=c.sub); yy += 42
        sx = x0 + 470 if side == 'l' else x0; sy = y + 50
        d.line((sx, sy, pt[0], pt[1]), fill=c.acc, width=5)
        d.ellipse((pt[0] - 16, pt[1] - 16, pt[0] + 16, pt[1] + 16), fill=c.acc, outline=(255, 255, 255), width=5)
    return cv

# ---------- 3. эффект ----------
def s_eff(c):
    L = c.lay['eff']; im = c.cuts[-1]; cv = c.bg(); d = ImageDraw.Draw(cv)
    eff = EFF[EFFT.get(c.ty, 'neck')]
    head = c.T(EFF_H[c.n % len(EFF_H)])
    if L == 0:
        title_block(c, d, 100, 100, W - 200, head, 112, c.ink, align='c', maxl=2)
        glow(cv, W // 2, 820, 520, (255, 150, 60) if any('fire' == e[0] for e in eff) else tint(c.acc, 0.3), a=170)
        place(cv, im, (330, 330, W - 330, 1250))
        cw = (W - 200 - 40) // 2; ch = 470
        for i, (ic, t, s) in enumerate(eff):
            x = 100 + (i % 2) * (cw + 40); y = 1330 + (i // 2) * (ch + 40)
            rr(cv, (x, y, x + cw, y + ch), 44, c.p['card']); d = ImageDraw.Draw(cv)
            icon(d, (x + 100, y + 110), ic, 110, c.acc)
            yy = y + 210
            for ln in wrap(d, t, F(c.bb, 52), cw - 80)[:2]: d.text((x + 44, yy), ln, font=F(c.bb, 52), fill=c.ink); yy += 60
            for ln in wrap(d, s, F(c.bf, 38), cw - 80)[:2]: d.text((x + 44, yy + 12), ln, font=F(c.bf, 38), fill=c.sub); yy += 46
    else:
        glow(cv, W // 2, 1650, 700, (255, 140, 60) if any('fire' == e[0] for e in eff) else tint(c.acc, 0.3), a=150)
        title_block(c, d, 100, 100, W - 200, head, 112, c.ink, maxl=2)
        y = 400
        for ic, t, s in eff:
            d.ellipse((100, y, 240, y + 140), fill=c.acc); icon(d, (170, y + 70), ic, 80, c.ta)
            d.text((290, y + 6), t, font=fitf(d, t, c.bb, 56, W - 400), fill=c.ink)
            d.text((290, y + 80), s, font=fitf(d, s, c.bf, 40, W - 400), fill=c.sub)
            y += 210
        place(cv, im, (300, 1250, W - 300, 2280))
    return cv

# ---------- 4. детали крупно ----------
def detail_regions(p, k=3):
    a = np.asarray(p.split()[3]) > 200; g = np.asarray(p.convert('L')).astype(float)
    s = int(min(p.width, p.height) * 0.34); best = []
    for y in range(0, p.height - s, max(8, s // 6)):
        for x in range(0, p.width - s, max(8, s // 6)):
            cov = a[y:y + s, x:x + s].mean()
            if cov < 0.8: continue
            gg = g[y:y + s, x:x + s]; sc = np.abs(np.diff(gg, axis=0)).mean() + np.abs(np.diff(gg, axis=1)).mean()
            best.append((sc, x, y))
    best.sort(reverse=True); out = []
    for sc, x, y in best:
        if all(abs(x - ox) > s * 0.8 or abs(y - oy) > s * 0.8 for _, ox, oy in out): out.append((sc, x, y))
        if len(out) == k: break
    if len(out) < k:
        out = [(0, int(p.width * fx - s / 2), int(p.height * fy - s / 2)) for fx, fy in [(0.5, 0.3), (0.35, 0.65), (0.65, 0.65)]][:k]
    return s, [(max(0, x), max(0, y)) for _, x, y in out]

def s_det(c):
    im = c.cuts[0]; cv = c.bg(); d = ImageDraw.Draw(cv)
    head = c.T(['Детали крупно', 'Продумано в деталях', 'Качество в деталях'][c.n % 3])
    title_block(c, d, 100, 100, W - 200, head, 112, c.ink, align='c', maxl=1)
    glow(cv, W // 2, 900, 480, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=150)
    (ox, oy, p), _ = place(cv, im, (380, 300, W - 380, 1420))
    s, regs = detail_regions(p)
    R = 250; cx = [W // 2 - 560, W // 2, W // 2 + 560]; cy = 1830
    d = ImageDraw.Draw(cv)
    src = c.cuts[0]; sx = src.width / p.width
    for i, (x, y) in enumerate(regs):
        crop = src.crop((int(x * sx), int(y * sx), int((x + s) * sx), int((y + s) * sx))).resize((2 * R, 2 * R), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
        circ = Image.new('RGBA', (2 * R, 2 * R), (255, 255, 255, 255) if not c.dark else tint(c.p['top'], 0.15) + (255,)); circ.alpha_composite(crop)
        m = Image.new('L', (2 * R, 2 * R), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
        px, py = ox + x + s // 2, oy + y + s // 2
        d.line((px, py, cx[i], cy - R), fill=c.acc, width=5)
        d.ellipse((px - s // 2, py - s // 2, px + s // 2, py + s // 2), outline=c.acc, width=5)
        cv.paste(circ, (cx[i] - R, cy - R), m); d = ImageDraw.Draw(cv)
        d.ellipse((cx[i] - R - 6, cy - R - 6, cx[i] + R + 6, cy + R + 6), outline=c.acc, width=10)
    line = ' • '.join(c.feats)
    d.text((W / 2, 2250), line, font=fitf(d, line, c.bb, 46, W - 200), fill=c.sub, anchor='mm')
    return cv

# ---------- 5. характеристики с крупными цифрами ----------
SH = dict(gun_mini='Перкуссионный массажер', gun_hook='Перкуссионный массажер', gun_full='Массажный пистолет', neck_ems='Импульсный массажер',
          neck_band='Массажер для шеи', pillow='Массажная подушка', pillow_u='Массажная подушка', back_cushion='Массажная подушка', seat='Массажная накидка',
          shawl='Массажер для шеи и плеч', trapez='Разминающий массажер', eye='Массажер для глаз', eye_steam='Массажер для глаз', eye_ems='Массажер для глаз',
          head='Массажер для головы', head_wrap='Массажер для головы', comb='Массажная расческа', foot_machine='Массажер для стоп',
          leg_boots='Компрессионный массажер', leg_calf='Массажер для икр', hand='Массажер для рук', dolphin='Ручной массажер')

def s_spec(c, g):
    im = c.cuts[0]; cv = c.bg(); d = ImageDraw.Draw(cv); m = c.m
    head = c.T(['Характеристики', 'Параметры', 'Коротко о модели'][c.n % 3])
    title_block(c, d, 100, 100, W - 200, head, 112, c.ink, align='c', maxl=1)
    glow(cv, W // 2, 760, 440, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=150)
    place(cv, im, (450, 280, W - 450, 1120))
    tiles = []
    if m.get('modes'): tiles.append(('tune-vertical', str(m['modes']), plural(m['modes'], 'режим', 'режима', 'режимов')))
    if m.get('heads'): tiles.append(('puzzle', str(m['heads']), plural(m['heads'], 'насадка', 'насадки', 'насадок')))
    if g: tiles.append(('weight-kilogram', (f'{g/1000:.1f}'.replace('.', ',') if g >= 1000 else str(int(g))), 'кг' if g >= 1000 else 'г'))
    pw = (m.get('power') or c.td['power'])
    tiles.append(('power-plug' if '220' in pw else 'battery-charging', '220 В' if '220' in pw else ('USB' if 'USB' in pw or 'аккум' in pw else 'бат.'), 'сеть' if '220' in pw else ('зарядка' if 'аккум' in pw or 'USB' in pw else 'питание')))
    tiles = tiles[:4]; n = len(tiles); tw_ = (W - 200 - 30 * (n - 1)) // n
    for i, (ic, num, cap) in enumerate(tiles):
        x = 100 + i * (tw_ + 30); y = 1180
        rr(cv, (x, y, x + tw_, y + 330), 40, c.acc + (255,)); d = ImageDraw.Draw(cv)
        icon(d, (x + tw_ / 2, y + 80), ic, 80, c.ta)
        d.text((x + tw_ / 2, y + 200), num, font=fitf(d, num, c.bb, 96, tw_ - 40), fill=c.ta, anchor='mm')
        d.text((x + tw_ / 2, y + 285), cap, font=F(c.bf, 38), fill=c.ta, anchor='mm')
    rows = [('Тип', m.get('short') or SH.get(c.ty, c.name)), ('Питание', pw), ('Зоны', (m.get('zones') or c.td['zones']).replace('; ', ', ')), ('Цвет', c.color)]
    y = 1570; rh = 150
    rr(cv, (100, y, W - 100, y + rh * len(rows)), 40, c.p['card']); d = ImageDraw.Draw(cv)
    for i, (a, b) in enumerate(rows):
        yy = y + i * rh
        if i: d.line((150, yy, W - 150, yy), fill=c.sub + (90,) if False else tint(c.sub, -0.2) if not c.dark else (120, 120, 130), width=2)
        d.text((150, yy + rh / 2), a, font=F(c.bf, 44), fill=c.sub, anchor='lm')
        fb = fitf(d, b, c.bb, 46, W - 760); d.text((W - 150, yy + rh / 2), b, font=fb, fill=c.ink, anchor='rm')
    return cv

# ---------- 6. где и как пользоваться ----------
def s_use(c):
    L = c.lay['how']; im = c.cuts[0]; cv = c.bg(); d = ImageDraw.Draw(cv); use = c.use[:4]
    if L == 0:
        head = c.T(['Где пригодится', 'Для каких зон', 'Используйте везде'][c.n % 3])
        title_block(c, d, 100, 100, W - 200, head, 112, c.ink, align='c', maxl=1)
        glow(cv, W // 2, 760, 460, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=150)
        place(cv, im, (420, 280, W - 420, 1150))
        cw = (W - 200 - 40) // 2; ch = 480
        for i, t in enumerate(use):
            x = 100 + (i % 2) * (cw + 40); y = 1240 + (i // 2) * (ch + 40)
            rr(cv, (x, y, x + cw, y + ch), 44, c.p['card']); d = ImageDraw.Draw(cv)
            d.ellipse((x + cw / 2 - 110, y + 50, x + cw / 2 + 110, y + 270), fill=c.acc)
            icon(d, (x + cw / 2, y + 160), use_icon(t), 120, c.ta)
            ls = wrap(d, t, F(c.bb, 50), cw - 80)[:2]; yy = y + 320
            for ln in ls: d.text((x + cw / 2, yy), ln, font=F(c.bb, 50), fill=c.ink, anchor='mt'); yy += 60
    else:
        head = c.T(['Как пользоваться', 'Всё просто', '3 шага к расслаблению'][c.n % 3])
        title_block(c, d, 100, 100, W - 200, head, 112, c.ink, maxl=2)
        pw = c.m.get('power') or c.td['power']
        st = [('Зарядите' if '220' not in pw else 'Подключите к сети', 'полный заряд — на несколько сеансов' if '220' not in pw else 'адаптер в комплекте'),
              ('Выберите режим', 'и комфортную интенсивность'), ('Расслабьтесь', '10–15 минут — и мышцы отдохнули')]
        y = 420
        for i, (t, s) in enumerate(st):
            d.text((100, y), f'0{i + 1}', font=F(c.bb, 150), fill=c.acc)
            d.text((380, y + 22), t, font=fitf(d, t, c.bb, 60, W - 480), fill=c.ink)
            d.text((380, y + 104), s, font=fitf(d, s, c.bf, 42, W - 480), fill=c.sub)
            y += 250
        glow(cv, W // 2, 1820, 560, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=150)
        place(cv, im, (300, 1200, W - 300, 2280))
    return cv

# ---------- 7. комплектация ----------
def kit_items(c):
    k = c.m.get('kit') or c.td['kit']
    k = k.replace('{heads}', str(c.m.get('heads') or 4)).replace('{pcs}', str(c.m.get('pcs') or 1))
    return [x.strip() for x in k.split(';') if x.strip()]
KIT_IC = [('кабель', 'usb'), ('адаптер', 'power-plug'), ('зарядн', 'power-plug'), ('инструк', 'book-open-variant'), ('пульт', 'remote'),
          ('насадк', 'puzzle'), ('кейс', 'briefcase'), ('электрод', 'lightning-bolt'), ('провод', 'cable-data'), ('подложк', 'layers'), ('автомоб', 'car')]
def s_kit(c):
    im = c.cuts[0]; cv = c.bg(); d = ImageDraw.Draw(cv); items = kit_items(c)
    head = c.T(['Комплектация', 'Что в коробке', 'В комплекте'][c.n % 3])
    title_block(c, d, 100, 100, W - 200, head, 112, c.ink, align='c', maxl=1)
    glow(cv, W // 2, 900, 520, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=160)
    place(cv, im, (330, 300, W - 330, 1450))
    n = len(items); y = 1560; rh = min(160, (2280 - y) // n)
    for it in items:
        name, _, q = it.partition('×')
        ic = next((v for k, v in KIT_IC if k in name.lower()), None) or ('package-variant' if it is not items[0] else 'star-four-points')
        rr(cv, (100, y, W - 100, y + rh - 24), (rh - 24) // 2, c.p['card']); d = ImageDraw.Draw(cv)
        icon(d, (190, y + (rh - 24) / 2), ic, 64, c.acc)
        d.text((270, y + (rh - 24) / 2), name, font=fitf(d, name, c.bb, 50, W - 640), fill=c.ink, anchor='lm')
        d.text((W - 170, y + (rh - 24) / 2), f'{q or 1} шт', font=F(c.bb, 50), fill=c.acc if c.dark else c.ink, anchor='rm')
        y += rh
    return cv

# ---------- 8. второй ракурс ----------
def s_view(c):
    im = c.cuts[1]; cv = c.bg(); d = ImageDraw.Draw(cv)
    glow(cv, W // 2, 1200, 760, tint(c.acc, 0.3) if c.dark else (255, 255, 255), a=180)
    rays(cv, W // 2, 1200, (255, 255, 255), a=20 if c.dark else 36)
    place(cv, im, (120, 330, W - 120, 2100))
    head = c.T(['Стильный дизайн', 'Со всех сторон', 'Вид сбоку'][c.n % 3])
    title_block(c, d, 100, 100, W - 200, head, 112, c.ink, align='c', maxl=1)
    color_pill(c, d, 0, 2210, center=True)
    return cv

def save(cv, p):
    cv.convert('RGB').resize((900, 1200), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1, 40, 2)).save(p, quality=90, subsampling=0)

def render(c, out, g):
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    slides = [('1_oblozhka', s_cover(c)), ('2_vozmozhnosti', s_call(c)), ('3_effekt', s_eff(c)), ('4_detali', s_det(c)),
              ('5_harakteristiki', s_spec(c, g)), ('6_primenenie', s_use(c)), ('7_komplekt', s_kit(c))]
    if len(c.cuts) > 1: slides.append(('8_rakurs', s_view(c)))
    paths = []
    for name, im in slides:
        p = f'{out}/{name}.jpg'; save(im, p); paths.append(p)
    return paths
