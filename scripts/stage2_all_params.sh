#!/bin/sh
# все параметры сразу, обычный скрипт
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
rm -f logs/stage2_all.xml
python3 src/main.py --vfs-path sample_vfs/several --prompt "emu> " \
    --log-file logs/stage2_all.xml --script startup/stage2.txt
echo "--- log file ---"
cat logs/stage2_all.xml
