"""Вырезка товара: rembg isnet (+ u2net для стекла/тиффани/ткани — берём маску с большим покрытием), чистка мелких компонентов → cut/{k}.png"""
import sys, os
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
S = {}
def sess(m):
    if m not in S: S[m] = new_session(m)
    return S[m]
DUAL = ()
def clean_alpha(a):
    m = (a > 40).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1: return a
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); ab = st[big, cv2.CC_STAT_AREA]
    keep = np.zeros_like(m)
    for i in range(1, n):
        if i == big or st[i, cv2.CC_STAT_AREA] > 0.08 * ab: keep[lab == i] = 1
    keep = cv2.dilate(keep, np.ones((5, 5), np.uint8))
    return (a * keep).astype(np.uint8)
def process(src, dst, dual):
    im = Image.open(src).convert('RGB')
    o = remove(im, session=sess('isnet-general-use'), post_process_mask=True)
    if dual:
        o2 = remove(im, session=sess('u2net'), post_process_mask=True)
        c1 = (np.asarray(o.split()[3]) > 128).sum(); c2 = (np.asarray(o2.split()[3]) > 128).sum()
        if c2 > c1 * 1.08: o = o2
    a = clean_alpha(np.asarray(o.split()[3])); o.putalpha(Image.fromarray(a))
    bb = o.getbbox()
    if bb: o = o.crop(bb)
    o.save(dst)
if __name__ == '__main__':
    os.makedirs('cut', exist_ok=True)
    for k in sys.argv[1:]:
        if os.path.exists(f'cut/{k}.png') and os.environ.get('FORCE') != '1': continue
        sp = f'clean/{k}.jpg' if os.path.exists(f'clean/{k}.jpg') else f'src/{k}.jpg'
        try: process(sp, f'cut/{k}.png', k.split('_')[0] in DUAL)
        except Exception as e: print('ERR', k, e, flush=True)
