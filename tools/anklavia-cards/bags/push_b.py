"""Копирует out/{vart} в wb-photos/anklavia/bags и пушит партиями. python3 push.py start end"""
import sys, os, json, shutil, subprocess
P = json.load(open('/home/claude/bags/prods.json'))
V = [(v['vart'], v['key']) for p in P for v in p['variants']]
a, b = int(sys.argv[1]), int(sys.argv[2])
R = '/home/claude/wb-photos'; dst = f'{R}/anklavia/bags'
for va, kk in V[a:b]:
    s = f'/home/claude/bags/out/{kk}'
    if not os.path.isdir(s): print('missing', va); continue
    os.makedirs(f'{dst}/{va}', exist_ok=True)
    for f in sorted(os.listdir(s)):
        if f.endswith('.jpg'): shutil.copy2(f'{s}/{f}', f'{dst}/{va}/{f}')
g = ['git', '-C', R, '-c', 'user.name=Elena', '-c', 'user.email=elenasorok505@gmail.com']
subprocess.run(g + ['add', 'anklavia/bags'], check=True)
msg = f'Anklavia: фото женских сумок, варианты {a + 1}–{min(b, len(V))}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01UcnrgCfSc5bVN7EHHWiver'
subprocess.run(g + ['commit', '-q', '-m', msg], check=True)
for i in range(3):
    r = subprocess.run(['git', '-C', R, 'push', '-q', 'origin', 'main'], capture_output=True, text=True)
    if r.returncode == 0: print('pushed', a, b); break
    print('push err', r.stderr[-300:])
