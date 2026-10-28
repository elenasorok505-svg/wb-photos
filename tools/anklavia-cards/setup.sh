#!/bin/bash
# Разворачивает набор в /home/claude/* (скрипты используют эти абсолютные пути).
# Запуск: bash /home/claude/wb-photos/tools/anklavia-cards/setup.sh
set -e; K="$(cd "$(dirname "$0")" && pwd)"
for d in bags mass mats bed lamps fonts2; do mkdir -p /home/claude/$d; cp -rn "$K/$d/." /home/claude/$d/; done
cp -f "$K/lamps/xfer.py" /home/claude/lamps/xfer.py
python3 -c "import rembg" 2>/dev/null || pip install -q --break-system-packages "rembg[cpu]" onnxruntime opencv-python-headless openpyxl
echo "готово: /home/claude/bags"
