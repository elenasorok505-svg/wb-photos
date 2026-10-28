import sys, json, io, os
from xfer import grab, dec
from PIL import Image
tag, n, since, man, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
s = grab(tag, n, since); b = dec(s)
M = json.load(open(man)); p = 0; os.makedirs(outdir, exist_ok=True); bad = []
for k, l in M:
    bb = b[p:p + l]; p += l
    try: Image.open(io.BytesIO(bb)).convert('RGB').save(f'{outdir}/{k}.jpg', quality=93)
    except Exception as e: bad.append(k)
print('ok', len(M) - len(bad), 'bad', bad, 'bytes', len(b), p)
