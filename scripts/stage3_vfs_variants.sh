#!/bin/sh
# три варианта VFS: минимальный, несколько файлов, глубокое дерево
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    python3 src/main.py --vfs-path "sample_vfs/$vfs" --prompt "$vfs> " \
        --log-file "logs/stage3_$vfs.xml" --script startup/stage3_vfs.txt
done
