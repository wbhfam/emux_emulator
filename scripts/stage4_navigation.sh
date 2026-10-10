#!/bin/sh
# ls и cd на VFS с несколькими файлами и на глубоком дереве
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    script="startup/stage4_$vfs.txt"
    [ -f "$script" ] || script=startup/stage4.txt
    python3 src/main.py --vfs-path "sample_vfs/$vfs" --prompt "$vfs> " \
        --log-file "logs/stage4_nav_$vfs.xml" --script "$script"
done
