"""оценка «предметного» фото: однородный светлый/серый фон по краям кадра"""
import numpy as np
from PIL import Image
def score(path):
    a = np.asarray(Image.open(path).convert('RGB').resize((100, 100))).astype(float)
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    med = np.median(border, 0); dev = np.abs(border - med).sum(1)
    uni = (dev < 30).mean()                     # доля однородных пикселей рамки
    return round(float(uni), 2), tuple(int(x) for x in med)
if __name__ == '__main__':
    import sys, glob, re
    for f in sorted(glob.glob(sys.argv[1])): print(f.split('/')[-1][:-4], *score(f))
