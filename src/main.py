"""Точка входа эмулятора."""

import argparse
import sys
import tkinter as tk

from gui import EmulatorApp
from logger import EventLogger, LogError
from shell import Shell
from vfs import Vfs, VfsError, load_vfs, vfs_name

NOT_SET = "(not set)"


def parse_args(argv=None):
    """Разбирает параметры командной строки."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs-path", help="путь к расположению VFS")
    parser.add_argument("--prompt", help="приглашение к вводу")
    parser.add_argument("--log-file", help="путь к лог-файлу (XML)")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args(argv)


def format_params(params):
    """Строки отладочного вывода всех параметров."""
    lines = ["[debug] parameters:"]
    for name, value in vars(params).items():
        shown = NOT_SET if value is None else repr(value)
        lines.append(f"[debug]   {name.replace('_', '-')} = {shown}")
    return lines


def open_vfs(path, errors):
    """Загружает VFS, при ошибке добавляет текст в errors."""
    if not path:
        return Vfs()
    try:
        return load_vfs(path)
    except VfsError as err:
        errors.append(f"error: {err}")
        return Vfs(vfs_name(path))


def open_logger(path, errors):
    """Открывает лог, при ошибке добавляет текст в errors."""
    if not path:
        return None
    try:
        return EventLogger(path)
    except LogError as err:
        errors.append(f"error: {err}")
        return None


def build_shell(params):
    """Создает оболочку по параметрам, возвращает ее и ошибки."""
    errors = []
    vfs = open_vfs(params.vfs_path, errors)
    logger = open_logger(params.log_file, errors)
    return Shell(vfs, params.prompt, logger), errors


def main(argv=None):
    """Создает окно и запускает эмулятор."""
    params = parse_args(argv)
    shell, errors = build_shell(params)
    debug = format_params(params)
    for line in debug:
        print(line)
    for line in errors:
        print(line, file=sys.stderr)
    root = tk.Tk()
    app = EmulatorApp(root, shell, shell.vfs.name)
    app.run(debug + errors, params.script)


if __name__ == "__main__":
    main()
