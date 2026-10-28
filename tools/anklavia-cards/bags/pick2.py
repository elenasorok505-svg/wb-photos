"""фильтр результатов API поиска 1688 → cand2.json (новые id, без реплик, 12–90¥, по продажам)"""
import json, sys
from pick import BL
R = json.load(open(sys.argv[1])); old = set(json.load(open('/home/claude/bags/bids.json')))
seen = set(); out = []
for tag, L in R.items():
    for x in L:
        if x.get('ad') or x['id'] in seen or x['id'] in old: continue
        if BL.search(x['t']) or BL.search(x.get('b', '')): continue
        if not x['p'] or not (12 <= x['p'] <= 90): continue
        seen.add(x['id']); out.append(dict(id=x['id'], tag=tag, p=x['p'], s=x['s'], s90=x.get('s90', 0), cc=x.get('cc', 0), t=x['t'][:60], b=x.get('b', ''), img=x['img']))
out.sort(key=lambda x: -(x['s90'] * 3 + x['s']))
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0); print(len(out))
