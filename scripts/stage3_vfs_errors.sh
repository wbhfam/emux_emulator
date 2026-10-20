#!/bin/sh
# ошибки загрузки VFS, между ними все нормальные варианты
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
for vfs in minimal several deep no_such_dir sample_vfs/minimal/hello.txt; do
    echo "=== VFS: $vfs ==="
    case "$vfs" in
        */*) path="$vfs" ;;
        minimal|several|deep) path="sample_vfs/$vfs" ;;
        *) path="$vfs" ;;
    esac
    python3 src/main.py --vfs-path "$path" --prompt "test> " \
        --log-file logs/stage3_errors.xml --script startup/stage3_vfs.txt
done
