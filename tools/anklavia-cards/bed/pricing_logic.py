"""
Логика ценообразования для бота маркетплейса.
Все параметры собраны в PARAMS: меняйте их, логика остаётся той же.
"""
import math

PARAMS = {
    "rate_cny_rub": 12.5764,     # курс ЦБ ¥→₽ (обновлять ежедневно)
    "commission": 0.10,          # комиссия маркетплейса с цены продажи
    "withdrawal": 0.01,          # комиссия за вывод денег
    "min_profit_rub": 150,       # минимальная прибыль с одной продажи, ₽
    "wb_discount": 0.15,         # насколько дешевле медианы WB ставим цену
    "k_a": 8.34,                 # множитель K = k_a * закупка^(-k_b)
    "k_b": 0.222,
    "k_min": 1.6,                # нижняя граница множителя (дорогие товары)
    "k_max": 6.0,                # верхняя граница множителя (дешёвые товары)
    # логистика, тариф «Стандарт» из таблицы перевозчика: две пары тарифов, берём дешевле
    "log_tariffs": [(58, 2), (43, 8)],   # (¥ за кг, ¥ за заказ)
    "pack_light_g": 50,          # упаковка для товара легче 300 г
    "pack_heavy_g": 80,          # упаковка для товара от 300 г
    "max_sum_sides_cm": 200,     # ограничение перевозчика: длина+ширина+высота
    "max_side_cm": 120,          # ограничение перевозчика: одна сторона
}


def multiplier(cost_cny, p=PARAMS):
    """Чем дешевле закупка, тем больше иксов. Плавная кривая без ступеней."""
    k = p["k_a"] * cost_cny ** (-p["k_b"])
    return max(p["k_min"], min(p["k_max"], k))


def logistics_cny(weight_g, p=PARAMS):
    """Вес с упаковкой, округлённый вверх до 100 г, по самому дешёвому тарифу."""
    pack = p["pack_light_g"] if weight_g < 300 else p["pack_heavy_g"]
    kg = math.ceil((weight_g + pack) / 100) / 10
    return kg, min(per_kg * kg + per_order for per_kg, per_order in p["log_tariffs"])


def pretty_round(price):
    """Округление вниз: до …9 для цен до 1000 ₽, до …90 от 1000 ₽."""
    p = int(price)
    if p < 1000:
        return (p + 1) // 10 * 10 - 1
    return (p + 10) // 100 * 100 - 10


def calc_price(cost_cny, weight_g, wb_median_rub=None, dims_cm=None, p=PARAMS):
    """
    cost_cny       — закупка на 1688 за 1 шт., ¥
    weight_g       — вес товара без упаковки, г
    wb_median_rub  — медиана цен топ-30 аналогов на WB, ₽ (None, если аналогов нет)
    dims_cm        — (длина, ширина, высота) упаковки, для проверки лимитов перевозчика
    """
    keep = (1 - p["commission"]) * (1 - p["withdrawal"])   # 0.891: доля, которая остаётся вам
    rate = p["rate_cny_rub"]

    if dims_cm and (sum(dims_cm) > p["max_sum_sides_cm"] or max(dims_cm) > p["max_side_cm"]):
        return {"status": "skip", "reason": "не проходит по габаритам перевозчика"}

    kg, log = logistics_cny(weight_g, p)
    cost_rub = (cost_cny + log) * rate                       # себестоимость
    k = multiplier(cost_cny, p)
    ceiling = (cost_cny * k + log) / keep * rate             # потолок: множитель, логистика без наценки
    floor = cost_rub / keep + p["min_profit_rub"]            # пол: минимальная прибыль
    market = wb_median_rub * (1 - p["wb_discount"]) if wb_median_rub else None

    if market is not None and market < floor:
        return {"status": "skip", "reason": "на WB дешевле, чем мы можем продать с прибылью",
                "floor_rub": round(floor), "market_rub": round(market)}

    raw = ceiling if market is None else min(ceiling, market)
    basis = "потолок (множитель)" if market is None or ceiling <= market else "рынок (WB −15%)"
    price = pretty_round(raw)
    if price < floor:                                        # округление не должно уводить ниже пола
        price = math.ceil(floor / 10) * 10 - 1 if floor < 1000 else math.ceil(floor / 100) * 100 - 10
        if price < floor: price += 10 if price < 1000 else 100   # 1099 → 1090 < пол: поднимаем на шаг

    profit = price * keep - cost_rub
    return {
        "status": "ok",
        "price_rub": price,
        "basis": basis,
        "cost_rub": round(cost_rub),
        "logistics_cny": round(log, 2),
        "weight_for_logistics_kg": kg,
        "k": round(k, 2),
        "ceiling_rub": round(ceiling),
        "market_rub": round(market) if market else None,
        "floor_rub": round(floor),
        "you_get_rub": round(price * keep),
        "profit_rub": round(profit),
        "margin": round(profit / price, 3),
        "x_to_cost": round(price / cost_rub, 2),
    }


if __name__ == "__main__":
    tests = [
        ("Сумка-багет", 14.5, 170, 1923),
        ("Сумка-тоут дутая большая", 19.8, 350, 1883),
        ("Сумка-шоппер вязаная", 5.2, 100, 745),
        ("Мини-вентилятор (WB 445 ₽ = медиана для примера)", 5.52, 120, 445),
        ("Проектор, без аналогов на WB", 1880, 1200, None),
    ]
    for name, c, w, wb in tests:
        print(name, calc_price(c, w, wb))
