import json,re,sys,glob,os
def _tooldir():
    # папка, куда Claude сохраняет большие результаты инструментов текущей сессии (самая свежая)
    c = glob.glob('/root/.claude/projects/*/*/tool-results/') + glob.glob('/root/.claude/projects/*/tool-results/')
    return max(c, key=os.path.getmtime) if c else '/tmp/'
D = os.environ.get('XFER_DIR') or _tooldir()
def grab(tag, n, since=0):
    parts={}
    for f in sorted(glob.glob(D+'*.txt'), key=os.path.getmtime)[-200:]:
        m=re.search(r'(\d{13})',os.path.basename(f))
        if m and int(m.group(1))<since: continue
        raw=open(f,errors='ignore').read()
        try: txt=''.join(x.get('text','') for x in json.loads(raw))
        except Exception: txt=raw
        for i in range(n):
            if i in parts: continue
            m=re.search(re.escape(tag)+str(i)+r'\|(.*?)~END\|',txt,re.S)
            if m: parts[i]=json.loads('"'+m.group(1)+'"') if '\\u' in m.group(1)[:50] else m.group(1)
    missing=[i for i in range(n) if i not in parts]
    assert not missing, missing
    return ''.join(parts[i] for i in range(n))
def dec(s):
    out=bytearray(); acc=0; nb=0
    for ch in s:
        acc=(acc<<14)|(ord(ch)-0x4E00); nb+=14
        while nb>=8: nb-=8; out.append((acc>>nb)&0xFF); acc&=(1<<nb)-1
    return bytes(out)
