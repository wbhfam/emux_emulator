#!/bin/sh
# команды этапа 4 на всех вариантах VFS
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    python3 src/main.py --vfs-path "sample_vfs/$vfs" \
        --log-file "logs/stage4_$vfs.xml" --script startup/stage4.txt
done
