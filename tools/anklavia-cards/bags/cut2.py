"""как cut.py, но всегда сравнивает isnet и u2net (лучше для белых/светлых сумок)"""
import sys, os, cut
for k in sys.argv[1:]:
    if os.path.exists(f'cut/{k}.png') and os.environ.get('FORCE') != '1': continue
    sp = f'clean/{k}.jpg' if os.path.exists(f'clean/{k}.jpg') else f'src/{k}.jpg'
    try: cut.process(sp, f'cut/{k}.png', True)
    except Exception as e: print('ERR', k, e, flush=True)
