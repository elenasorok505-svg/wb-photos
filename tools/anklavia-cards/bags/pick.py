"""фильтр результатов поиска 1688: без реплик брендов, цена 12–90¥, сортировка по продажам"""
import json, re, sys
BL = re.compile(r'老花|CF|小香|香风|香女|铂金|凯莉|凯丽|蔻|驴家|巴黎家|D家|row|龙香|龙骧|Balenc|Rodeo|LeCity|Juliet|tabby|Speedy|city ?33|戴妃|Emblem|GiGi|原厂|芯片|M&LV|LV|谬家|戈雅|25bag|寇家|恶枭|酒神|爱马|Hermes|Gucci|Prada|Dior|Celine|赛琳|YSL|圣罗兰|MK|Coach|稻草人|土著|Toujours|kira|TB女包|pedro|罗意威|Loewe|BV|葆蝶|编织包.*BV|法式龙|miu|缪|奥莱|mini迷你饺子|Lady|lady|chanel|Chanel|LOEWE|cos同款|同款|大牌|名牌|专柜|真皮|头层|牛皮|羊皮|植鞣', re.I)
def sold(s):
    if not s: return 0
    m = re.match(r'([\d.]+)(万)?', s); v = float(m.group(1)) if m else 0
    return int(v * (10000 if m and m.group(2) else 1))
if __name__ == '__main__':
    R = json.load(open(sys.argv[1])); seen = set(); out = []
    for tag, L in R.items():
        for x in L:
            if x.get('ad') or x['id'] in seen: continue
            if BL.search(x['t']): continue
            if not x['p'] or not (12 <= x['p'] <= 90): continue
            seen.add(x['id']); out.append(dict(id=x['id'], tag=tag, p=x['p'], s=sold(x['s']), t=x['t'][:60], img=x['img']))
    out.sort(key=lambda x: -x['s'])
    json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0); print(len(out))
