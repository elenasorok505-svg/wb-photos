"""Убирает белый фон, оставшийся внутри ручек-колец: компоненты почти белых пикселей в верхней части, не доходящие до низа."""
import sys, numpy as np, cv2
from PIL import Image
for k in sys.argv[1:]:
    o = Image.open(f'cut/{k}.png').convert('RGBA'); a = np.asarray(o).copy()
    rgb = a[..., :3].astype(int); h, w = rgb.shape[:2]
    m = ((rgb.min(axis=2) > 236) & (a[..., 3] > 0)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8); c = 0
    for i in range(1, n):
        x, y, ww, hh, ar = st[i]
        if ar > 0.004 * h * w and y + hh < 0.6 * h: a[lab == i, 3] = 0; c += 1
    Image.fromarray(a).save(f'cut/{k}.png'); print(k, c)
