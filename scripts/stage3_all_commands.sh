#!/bin/sh
# скрипт со всеми командами этапов 1-3 на каждом варианте VFS
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    python3 src/main.py --vfs-path "sample_vfs/$vfs" --prompt "$vfs> " \
        --log-file "logs/stage3_all_$vfs.xml" \
        --script startup/stage3_all.txt
done
