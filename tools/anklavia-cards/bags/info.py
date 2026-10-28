"""python3 info.py n1 n2 ... — сводка оффера: название, цены, SKU (цвет: цена), упаковка, атрибуты"""
import json, sys
B = json.load(open('/home/claude/bags/bags.json')); I = json.load(open('/home/claude/bags/bids.json'))
for a in sys.argv[1:]:
    n = int(a); x = B.get(I[n])
    if not x: print(n, 'MISSING'); continue
    sp = next((p for p in x.get('sp') or [] if any(v[1] for v in p['v'])), {'v': []})
    sims = x.get('sim') or {}
    cols = [f"{k}:{v[0]}" + (f"[{max([float(s[0]) for kk, s in sims.items() if v[0] in kk and s[0]] or [0])}]" if sims else '') for k, v in enumerate(sp['v'][:10])]
    pk = [(r['l'], r['w'], r['h'], r['g'], r.get('sku', '')) for r in (x.get('pk') or [])[:2]]
    fa = {k: v for k, v in (x.get('fa') or {}).items() if k not in ('颜色', '适用场景', '风格')}
    print(n, x['title'][:44], x['price'][:2], '|', ' '.join(cols), '| pk', pk, '|', fa)
