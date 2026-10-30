"""Справочник категорий Anklavia (anklavia-categories-*.xlsx) для конвейера «200 карточек».

  python3 cats.py tree [фильтр]          — дерево разделов/подразделов/категорий со slug
  python3 cats.py leaves "Одежда › Женская"  — листовые категории (slug) внутри раздела/подраздела
  python3 cats.py fields SLUG            — поля категории: тип, обязательность, значения словарей
  python3 cats.py tpl SLUG out.xlsx      — шаблон «Товары» для категории

tpl: если рядом лежит официальный tpl_SLUG.xlsx — копирует его. Иначе собирает шаблон по образцу
tpl_women-tshirts.xlsx: базовые колонки + поля категории; подсказки ряда 2 — из справочника, с кодом
колонки [attr:…]. Коды известны только для полей, встречавшихся в официальных шаблонах (CODES ниже);
для остальных печатает предупреждение и ставит [attr:?] — такой шаблон годится для подготовки
данных, но перед загрузкой в кабинет нужен официальный шаблон категории (положить сюда как tpl_SLUG.xlsx).
"""
import sys, os, re, glob, shutil, warnings
import openpyxl, signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
warnings.filterwarnings('ignore')
D = os.path.dirname(os.path.abspath(__file__))
SRC = sorted(glob.glob(os.path.join(D, 'anklavia-categories-*.xlsx')))[-1]
BASE = os.path.join(D, 'tpl_women-tshirts.xlsx')


def load():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    tree, path, out = list(wb['Дерево категорий'].iter_rows(values_only=True))[1:], [None, None], []
    chart = [None, None]
    for r in tree:
        if r[0]:
            path = [r[0], None]; chart = [r[6], None]
        elif r[1]:
            path[1] = r[1]; chart[1] = r[6]
        lvl = 0 if r[0] else 1 if r[1] else 2
        name = r[0] or r[1] or r[2]
        full = ' › '.join([x for x in path[:lvl] if x] + [name]) if lvl else name
        out.append(dict(level=lvl, name=name, zh=r[3], slug=r[4], active=r[5], chart=r[6] or chart[1] or chart[0], path=full))
    F = {}
    for r in list(wb['Характеристики по категориям'].iter_rows(values_only=True))[1:]:
        F.setdefault(r[1], []).append(dict(field=r[2], zh=r[3], type=r[4], req=r[5] == 'да', filt=r[6], axis=r[7], vals=r[8], path=r[0]))
    V = {}
    for r in list(wb['Словари значений'].iter_rows(values_only=True))[1:]:
        V.setdefault(r[0], []).append(r[3])
    return out, F, V


def vals(f, V, n=None):
    v = f['vals'] or ''
    m = re.match(r'словарь «(.+)»', v)
    lst = V.get(m.group(1), []) if m else [x.strip() for x in v.split(';') if x.strip()]
    return lst[:n] if n else lst


def base_codes():
    C = {}
    for p in glob.glob(os.path.join(D, 'tpl_*.xlsx')):
        ws = openpyxl.load_workbook(p)['Товары']
        for a, b in zip(ws[1], ws[2]):
            m = re.search(r'\[([^\]]+)\]\s*$', b.value or '')
            if a.value and m: C[a.value] = m.group(1)
    return C


def cmd_tree(flt=''):
    T, F, _ = load()
    for t in T:
        if flt.lower() in t['path'].lower():
            print('  ' * t['level'] + f"{t['name']}  [{t['slug']}]" + (f"  полей: {len(F.get(t['slug'], []))}" if t['level'] == 2 else ''))


def cmd_leaves(prefix):
    T, F, _ = load()
    for t in T:
        if t['level'] == 2 and t['path'].startswith(prefix) and t['active'] == 'да':
            print(f"{t['slug']}\t{t['path']}\t{t['zh']}\tполей {len(F.get(t['slug'], []))}")


def cmd_fields(slug):
    _, F, V = load()
    for f in F.get(slug, []):
        v = vals(f, V)
        print(f"{'*' if f['req'] else ' '} {f['field']} ({f['zh']}) — {f['type']}" + (f": {'; '.join(v[:40])}" + (' …' if len(v) > 40 else '') if v else ''))


def cmd_tpl(slug, out):
    off = os.path.join(D, f'tpl_{slug}.xlsx')
    if os.path.exists(off):
        shutil.copy(off, out); print('официальный шаблон:', off); return
    T, F, V = load()
    cat = next((t for t in T if t['slug'] == slug), None)
    if not cat or slug not in F: sys.exit(f'нет категории {slug}')
    C = base_codes()
    wb = openpyxl.load_workbook(BASE); ws = wb['Товары']
    hdr = [c.value for c in ws[1]]; hint = [c.value for c in ws[2]]
    nbase = hdr.index('Таблица размеров (код)') + 1
    cols = list(zip(hdr[:nbase], hint[:nbase]))
    if not cat['chart']:  # без размерной сетки — нет колонок размера
        cols = [c for c in cols if c[0] not in ('Размер', 'Таблица размеров (код)')]
    cols = [(h, (t or '').replace('[category:women-tshirts]', f'[category:{slug}]')) for h, t in cols]
    unknown = []
    for f in F[slug]:
        v = vals(f, V, 10)
        many = 'несколько' in f['type']
        txt = ('Обязательно к публикации. ' if f['req'] else '') + ('до 3 значений через «;». ' if many else '')
        if v: txt += 'из справочника: ' + '; '.join(v) + ('; …' if len(vals(f, V)) > 10 else '') + ('. или своё значение (уйдёт на проверку)' if 'своё' in f['type'] else '')
        elif f['type'] == 'число': txt += 'Число'
        code = C.get(f['field'])
        if not code: unknown.append(f['field']); code = 'attr:?'
        cols.append((f['field'], f'{txt} [{code}]'.strip()))
    ws.delete_rows(1, ws.max_row); ws.delete_cols(1, ws.max_column)
    for j, (h, t) in enumerate(cols, 1):
        ws.cell(1, j, h); ws.cell(2, j, t)
    wb.save(out)
    print(f'{out}: {len(cols)} колонок, категория {cat["path"]}')
    if unknown:
        print('ВНИМАНИЕ: нет кода колонки для полей:', '; '.join(unknown))
        print('Для загрузки в кабинет нужен официальный шаблон этой категории → положить как', off)


if __name__ == '__main__':
    a = sys.argv[1:] or ['tree']
    {'tree': lambda: cmd_tree(*a[1:]), 'leaves': lambda: cmd_leaves(a[1]), 'fields': lambda: cmd_fields(a[1]),
     'tpl': lambda: cmd_tpl(a[1], a[2])}[a[0]]()
