"""python3 merge_bags.py TAG N SINCE — дописывает переданные записи __bags в bags.json"""
import sys, json
sys.path.insert(0, '/home/claude/lamps')
from xfer import grab
s = grab(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
if s.startswith('{\\"'): s = json.loads('"' + s + '"')
d = json.loads(s); B = json.load(open('/home/claude/bags/bags.json')); n0 = len(B); B.update(d)
json.dump(B, open('/home/claude/bags/bags.json', 'w'), ensure_ascii=False); print(n0, '->', len(B))
