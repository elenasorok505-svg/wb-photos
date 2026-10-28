"""python3 thsheet.py A B OUT — контакт-лист миниатюр thm/ для офферов A..B-1 (до 12 картинок в ряд)"""
import sys, os, re
from PIL import Image, ImageDraw
a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
os.chdir('/home/claude/bags'); F = os.listdir('thm'); rows = []
for n in range(a, b):
    ks = sorted([f[:-4] for f in F if re.match(rf'B{n}[_m]\d+\.jpg$', f)], key=lambda k: ('m' in k, int(re.split('[_m]', k[1:])[1])))
    if ks: rows.append((n, ks[:12]))
g = Image.new('RGB', (12 * 120, len(rows) * 132), 'white'); d = ImageDraw.Draw(g)
for r, (n, ks) in enumerate(rows):
    for i, k in enumerate(ks):
        im = Image.open(f'thm/{k}.jpg').convert('RGB'); im.thumbnail((118, 118)); g.paste(im, (i * 120, r * 132))
        if i == 0: d.text((2, r * 132 + 119), str(n), fill=(220, 0, 0))
    d.text((40, r * 132 + 119), ' '.join(k.split('_')[-1] if '_' in k else 'm' for k in ks), fill=(90, 90, 90))
g.save(out, quality=80); print(len(rows))
