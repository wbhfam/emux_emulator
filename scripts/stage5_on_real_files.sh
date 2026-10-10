#!/bin/sh
# отдельные скрипты для several и deep, потом проверка что диск не изменился
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep; do
    echo "=== VFS: $vfs ==="
    script="startup/stage5_$vfs.txt"
    [ -f "$script" ] || script=startup/stage5.txt
    python3 src/main.py --vfs-path "sample_vfs/$vfs" \
        --prompt "$vfs> " --log-file "logs/stage5_real_$vfs.xml" \
        --script "$script"
done
echo "=== git status of sample_vfs (must be empty) ==="
git status --short sample_vfs
