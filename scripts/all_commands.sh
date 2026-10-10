#!/bin/sh
# все команды, все варианты VFS, все параметры командной строки
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    python3 src/main.py --vfs-path "sample_vfs/$vfs" \
        --prompt "$vfs> " --log-file "logs/all_$vfs.xml" \
        --script startup/all_commands.txt
done
