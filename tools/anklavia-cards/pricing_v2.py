"""Новая цена: цена этого же товара на WB (поиск по фото) минус 15%, в юанях,
но не ниже уровня, где с продажи остаётся 150 ₽ прибыли."""
import math, statistics as st

P = dict(rate=12.0677,          # ЦБ РФ на 28.10.2026, ₽ за 1 ¥
         commission=0.10, withdrawal=0.01, min_profit=150, disc=0.15,
         t1k=58, t1o=2, t2k=43, t2o=8, pack_l=50, pack_h=80, top_n=8)
KEEP = (1 - P['commission']) * (1 - P['withdrawal'])


def logistics(w):
    pack = P['pack_l'] if w < 300 else P['pack_h']
    kg = math.ceil((w + pack) / 100) / 10
    return kg, min(P['t1k'] * kg + P['t1o'], P['t2k'] * kg + P['t2o'])


def analog_median(res, n=None):
    n = n or P['top_n']
    pr = [p for p, _ in res if p > 0][:n]
    return st.median(pr) if len(pr) >= 3 else None


def ceiling_rub(cost, log):
    k = max(1.6, min(6.0, 8.34 * cost ** (-0.222)))
    return (cost * k + log) / KEEP * P['rate']


def price(cost, w, wb_rub, use_ceiling=False):
    """use_ceiling — цены «этого товара» нет (взята медиана категории): не выше потолка по множителю."""
    kg, log = logistics(w)
    cost_rub = (cost + log) * P['rate']
    floor_rub = (cost_rub + P['min_profit']) / KEEP     # после комиссий остаётся ровно 150 ₽ сверх себестоимости
    floor_cny = math.ceil(floor_rub / P['rate'])
    market_rub = wb_rub * (1 - P['disc'])
    ceil_rub = ceiling_rub(cost, log)
    if use_ceiling and ceil_rub < market_rub: market_rub = ceil_rub
    market_cny = int(market_rub / P['rate'])
    cny = max(floor_cny, market_cny)
    rub = cny * P['rate']
    return dict(kg=kg, log=round(log, 2), cost_rub=cost_rub, floor_rub=floor_rub, market_rub=market_rub,
                cny=cny, rub=rub, profit=rub * KEEP - cost_rub,
                basis=('мин. прибыль' if market_cny < floor_cny else ('потолок (нет точного аналога)' if use_ceiling and ceil_rub <= wb_rub * (1 - P['disc']) else 'WB −15%')), ceil_rub=ceil_rub,
                over=rub / wb_rub - 1)
