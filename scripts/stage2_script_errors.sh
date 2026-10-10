#!/bin/sh
# все параметры, в стартовом скрипте есть ошибочные строки
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
rm -f logs/stage2_errors.xml
python3 src/main.py --vfs-path sample_vfs/minimal --prompt "err> " \
    --log-file logs/stage2_errors.xml --script startup/stage2_errors.txt
echo "--- log file ---"
cat logs/stage2_errors.xml
