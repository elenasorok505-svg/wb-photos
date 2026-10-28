import sys, json, os, time
sys.path.insert(0, '/home/claude/bags')
import br as lr2
P = json.load(open('/home/claude/bags/prods.json'))
out = sys.argv[1]; sel = sys.argv[2]
part, nparts = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)
items = [(p, v) for p in P for v in p['variants']]
if sel != 'all':
    arts = sel.split(','); items = [(p, v) for p, v in items if p['art'] in arts or v['vart'] in arts]
items = items[part::nparts]
t0 = time.time()
for i, (p, v) in enumerate(items):
    od = f"{out}/{v['key']}"
    if os.path.exists(f'{od}/08.jpg') and os.environ.get('FORCE') != '1': continue
    try: lr2.render(p, v, od)
    except Exception as e: print('ERR', v['vart'], repr(e), flush=True)
    if i % 10 == 0: print(i, len(items), round(time.time() - t0), flush=True)
