#!/bin/sh
# mkdir и mv на всех вариантах VFS (общий скрипт)
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    python3 src/main.py --vfs-path "sample_vfs/$vfs" \
        --prompt "$vfs> " --log-file "logs/stage5_$vfs.xml" \
        --script startup/stage5.txt
done
