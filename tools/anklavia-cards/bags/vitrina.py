"""Превью витрины: обложки первых вариантов, цена, название — как в каталоге маркетплейса. python3 vitrina.py outdir"""
import sys, json, os
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/mass')
from render_m2 import F, wrap
P = json.load(open('/home/claude/bags/prods.json'))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
from PIL import ImageFont
RUB = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf', 32)
cols, per = 5, 40; cw, ch = 360, 480; pad = 24; th = 150
for s in range(0, len(P), per):
    chunk = P[s:s + per]; rows = (len(chunk) + cols - 1) // cols
    im = Image.new('RGB', (pad + cols * (cw + pad), 110 + rows * (ch + th + pad)), (246, 244, 242)); d = ImageDraw.Draw(im)
    d.text((pad, 34), f'Anklavia · Сумки женские · {s + 1}–{s + len(chunk)} из {len(P)}', font=F('manrope-800', 40), fill=(40, 34, 30))
    for i, p in enumerate(chunk):
        v = p['variants'][0]; x = pad + (i % cols) * (cw + pad); y = 110 + (i // cols) * (ch + th + pad)
        f = f"/home/claude/bags/out/{v['key']}/01.jpg"
        if os.path.exists(f): im.paste(Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS), (x, y))
        d.rectangle((x, y + ch, x + cw, y + ch + th), fill=(255, 255, 255))
        d.text((x + 12, y + ch + 10), f"{v['price']:,} ₽".replace(',', ' '), font=RUB, fill=(160, 40, 120))
        if len(p['variants']) > 1: d.text((x + cw - 12, y + ch + 16), f"{len(p['variants'])} цв.", font=F('manrope-600', 22), fill=(120, 110, 100), anchor='ra')
        for j, ln in enumerate(wrap(d, p['title'], F('manrope-500', 21), cw - 24)[:3]): d.text((x + 12, y + ch + 56 + j * 28), ln, font=F('manrope-500', 21), fill=(60, 54, 50))
    im.save(f'{out}/vitrina_{s // per + 1}.jpg', quality=88)
print('ok')
