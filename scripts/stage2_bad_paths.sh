#!/bin/sh
# все параметры, но скрипта нет, а лог-файл испорчен
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
echo "this is not xml" > logs/broken.xml
python3 src/main.py --vfs-path sample_vfs/deep --prompt "bad> " \
    --log-file logs/broken.xml --script startup/no_such_script.txt
echo "--- script not found, log file is broken ---"
