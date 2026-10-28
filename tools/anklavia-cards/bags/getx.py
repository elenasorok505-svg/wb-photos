"""python3 getx.py TAG N SINCE OUTDIR  — манифест MX0 после SINCE + чанки TAG0..N-1 → OUTDIR/{key}.jpg"""
import sys, json
sys.path.insert(0, '/home/claude/lamps')
from xfer import grab
import subprocess
tag, n, since, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
m = grab('MX', 1, since).replace('\\"', '"'); json.dump(json.loads(m), open('/tmp/_man.json', 'w'))
subprocess.run(['python3', '/home/claude/lamps/unpack.py', tag, n, str(since), '/tmp/_man.json', out], cwd='/home/claude/lamps')
