"""Каталог женских сумок Anklavia (200 карточек). Карточка = модель, цвета = варианты (одна Группа).
Спецификации моделей — specs.py (SPEC), данные 1688 — bags.json, медианы WB — wb_med.json."""
import json, re, sys
sys.path.insert(0, '/home/claude/bed')
from pricing_logic import calc_price
from fam import TYPES, MATS, FITS, FIT_S, DEPTH, SCENES, SCENES_EVE
from specs import SPEC

B = json.load(open('/home/claude/bags/bags.json'))
IDS = json.load(open('/home/claude/bags/bids.json'))
MED = json.load(open('/home/claude/bags/wb_med.json'))
PALS_L = ['cream', 'blush', 'sage', 'stone']
PALS_D = ['mocha', 'noir', 'wine', 'navy']
Q = {'baguette': 'сумка багет женская', 'crescent': 'сумка полумесяц женская', 'hobo': 'сумка хобо женская', 'tote': 'сумка тоут женская',
     'shopper': 'сумка шоппер женская', 'bucket': 'сумка мешок женская', 'saddle': 'сумка седло женская', 'cross': 'сумка кросс-боди женская',
     'flap': 'сумка женская через плечо', 'quilted': 'сумка стеганая женская', 'cloud': 'сумка облако экокожа', 'pleated': 'сумка пельмень',
     'bowling': 'сумка саквояж женская', 'box': 'сумка женская с короткой ручкой', 'shell': 'сумка женская с короткой ручкой', 'tophandle': 'сумка женская с короткой ручкой',
     'clutch': 'клатч вечерний', 'evening': 'сумка вечерняя со стразами', 'phone': 'сумка для телефона женская', 'sling': 'сумка кросс-боди женская',
     'waist': 'поясная сумка женская', 'backpack': 'рюкзак женский городской', 'fluffy': 'сумка меховая женская', 'straw': 'сумка плетеная женская',
     'messenger': 'сумка мессенджер женская', 'drawstring': 'сумка мешок женская', 'puffer': 'сумка женская большая'}

def fmt(x): return str(int(x)) if float(x).is_integer() else str(x).replace('.', ',')

def sku_cost(x, cn):
    sim = x.get('sim') or {}
    ps = [float(v[0]) for k, v in sim.items() if cn in k and v[0]]
    if ps: return max(ps)
    pr = [float(p) for p in x['price'] if p]
    return max(pr) if pr else None

def sku_g(x, cn):
    for r in x.get('pk') or []:
        if r.get('g') and (not r.get('sku') or cn in r['sku'] or r['sku'] in cn): return float(r['g'])
    gs = [float(r['g']) for r in x.get('pk') or [] if r.get('g')]
    return max(gs) if gs else None

def pk_dims(x):
    for r in x.get('pk') or []:
        if r.get('l') and r.get('h'): return (float(r['l']), float(r['h']), float(r.get('w') or 0))
    return None

def build():
    res = []; skipped = []
    cnt = {'l': 0, 'd': 0}
    for n, s in enumerate(SPEC):
        x = B[IDS[s['n']]]; t = TYPES[s['type']]; m = MATS[s['mat']]
        dims = s.get('dims') or pk_dims(x)
        w, h, d = dims if len(dims) == 3 else (*dims, 8)
        if not d: d = {'mini': 5, 'small': 7, 'medium': 10, 'large': 13, 'xl': 15}[s['size']]
        size = s['size']; kindv = t[1]
        eve = kindv == 'Вечерние'
        dark = s.get('dark', n % 3 == 1)
        pal = (PALS_D if dark else PALS_L)[cnt['d' if dark else 'l'] % 4]; cnt['d' if dark else 'l'] += 1
        name = s.get('name', t[0])
        adj = s.get('adj', '')
        mat_word = {'pu': 'из экокожи', 'pu_matte': 'из матовой экокожи', 'pu_lacquer': 'лаковая', 'suede': 'замшевая', 'nylon': 'нейлоновая',
                    'canvas': 'из канваса', 'fur': 'меховая', 'straw': 'плетёная из соломки', 'knit': 'вязаная', 'satin': 'атласная',
                    'sequin': 'блестящая', 'crystal': 'со стразами', 'velvet': 'бархатная', 'denim': 'джинсовая', 'poly': 'текстильная',
                    'corduroy': 'вельветовая'}[s['mat']]
        base = 'Рюкзак женский' if s['type'] == 'backpack' else f"{name} женская"
        wear_t = {'cross': 'через плечо', 'shoulder': 'на плечо', 'hand': 'с ручками', 'clutch': 'вечерняя', 'waist': 'на пояс', 'back': 'городской'}[t[4][0]]
        if any(r in (adj + ' ' + name).lower() for r in ['экокож', 'замш', 'мех', 'пушист', 'лак', 'нейлон', 'соломк']): mat_word = ''
        title = s.get('title') or re.sub(r'\s+', ' ', f"{base} {adj} {wear_t} {mat_word} {fmt(w)} см").strip()
        title = title[0].upper() + title[1:]
        cover = s.get('cover') or [name if s['type'] != 'backpack' else 'Рюкзак', f"{m[2].lower()}, {fmt(w)}×{fmt(h)} см"]
        q = s.get('q') or Q[s['type']]; med = MED.get(q, [None])[0]
        strap = s.get('strap')
        closure = s.get('closure', 'Молния')
        vs = []
        for k, color in s['v']:
            cn = (x.get('sp') or [{}])[0]['v'][k][0] if x.get('sp') else ''
            cost = s.get('cost') or sku_cost(x, cn)
            g = s.get('g') or sku_g(x, cn) or {'mini': 250, 'small': 380, 'medium': 520, 'large': 650, 'xl': 800}[size]
            g = max(150, min(g, 1500))
            pk = sorted([int(w + 4), int(h + 4), int(max(d, 4) + 3)], reverse=True)
            r = calc_price(cost, g, med, pk)
            if r['status'] == 'skip': skipped.append((n, s['n'], color, cost, r.get('floor_rub'), r.get('market_rub'))); continue
            vs.append(dict(key=f"B{s['n']}_{k}", color=color, cn=cn, cost=cost, g=g, pkg=pk, price=r['price_rub'], calc=r, med=med))
        if not vs: continue
        g = max(v['g'] for v in vs)
        feats = s.get('feats') or default_feats(s, t, m, closure, strap)
        specs = [('Тип', name), ('Материал', m[0][0].upper() + m[0][1:]), ('Размер', f"{fmt(w)}×{fmt(h)}×{fmt(d)} см"),
                 ('Застёжка', closure), ('Отделения', str(s.get('comp', 1)))]
        if strap: specs.append(('Ремень', f"до {fmt(strap)} см" + (', регулируется' if s.get('adjust', True) else '')))
        specs.append(('Подкладка', s.get('lining', 'Полиэстер')))
        p = dict(n=n, src=s['n'], id=IDS[s['n']], type=s['type'], line=s['mat'], title=title[:120], cover=cover, dims=dict(w=w, h=h, d=d),
                 size=size, strap=strap, closure=closure, mat=m[0], mat_attr=s.get('mat_attr', m[1]), mat_label=m[2],
                 mac_t=m[3], mac_s=m[4], mac_items=m[5], kind=kindv, cut_style=t[2], strap_purpose=t[3], wear=t[4],
                 wear_icon={'cross': 'vector-line', 'shoulder': 'account-outline', 'hand': 'hand-back-right', 'clutch': 'hand-heart',
                            'waist': 'human-female', 'back': 'bag-personal'}[t[4][0]],
                 wear_label={'cross': 'Через плечо', 'shoulder': 'На плечо', 'hand': 'В руке', 'clutch': 'Клатч', 'waist': 'На поясе', 'back': 'На спине'}[t[4][0]],
                 badge=(f"{fmt(w)} см", 'ширина'), depth_note=DEPTH[size],
                 strap_txt=s.get('strap_txt') or (f"Съёмный регулируемый ремень до {fmt(strap)} см — носите на плече или через плечо" if strap else 'Удобные ручки — носите в руке или на плече'),
                 fits=FITS[size], fit_s=FIT_S[size], scene_t=(SCENES_EVE if eve else SCENES)[n % (3 if eve else 8)],
                 feats=feats, wear_s='Несколько способов носить — под любой образ', specs=specs, pal=pal, dark=dark,
                 cover_i=s.get('cover_i', (n * 3 + n // 4) % 4), comp=s.get('comp', 1), pockets=s.get('pockets', 'Внутренние'),
                 lining=s.get('lining', 'Полиэстер'), texture=s.get('texture', 'Гладкая'), decor=s.get('decor', 'Без декора'),
                 pattern=s.get('pattern', 'Однотонный'), features=s.get('features', ''), q=q, g=g, approx=s.get('approx', False), variants=vs)
        res.append(p)
    for k, p in enumerate(res):
        p['art'] = f'ANK-BAG-{k + 1:03d}'
        for i, v in enumerate(p['variants']): v['vart'] = f"{p['art']}-{i + 1:02d}"
    return res, skipped

def default_feats(s, t, m, closure, strap):
    f = []
    f.append({'Молния': ('lock-outline', 'Застёжка-молния', 'Вещи надёжно защищены'), 'Магнит': ('magnet', 'Магнитная кнопка', 'Открывается одной рукой'),
              'Пряжка': ('lock-outline', 'Металлическая пряжка', 'Стильная и надёжная'), 'Шнурок': ('vector-curve', 'Затяжка на шнурке', 'Мягкий силуэт мешка'),
              'Кнопка': ('magnet', 'Кнопка', 'Быстро открывается'),
              'Без застёжки': ('gesture-tap', 'Открытый верх', 'Быстрый доступ к вещам'), 'Завязки': ('ribbon', 'Завязки-бант', 'Нежный акцент и мягкий силуэт'),
              'Замок-рамка': ('lock-outline', 'Замок-рамка', 'Ретро-застёжка, щёлкает надёжно')}.get(closure, ('lock-outline', closure, 'Надёжная застёжка')))
    f.append(m[5][0][:1] + (m[5][0][1], {'pu': 'Не боится дождя и снега', 'suede': 'Тренд сезона'}.get(s['mat'], 'Практичный материал')))
    if strap: f.append(('vector-line', 'Регулируемый ремень', f'До {fmt(strap)} см — на плечо и через плечо'))
    else: f.append(('hand-back-right', 'Удобные ручки', 'Комфортно в руке и на плече'))
    f.append(('format-list-bulleted', f"{s.get('comp', 1)} {'отделение' if s.get('comp', 1) == 1 else 'отделения'}", 'Внутренний карман для мелочей'))
    return [(a, b, c) for a, b, c in f]

if __name__ == '__main__':
    res, sk = build()
    json.dump(res, open('/home/claude/bags/prods.json', 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print('products', len(res), 'variants', sum(len(p['variants']) for p in res), Counter(p['type'] for p in res))
    for s in sk: print('SKIP', s)
