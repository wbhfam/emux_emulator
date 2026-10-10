"""Точка входа эмулятора."""

import tkinter as tk

from gui import EmulatorApp
from shell import Shell

DEFAULT_VFS_NAME = "vfs"


def main():
    """Создает окно и запускает эмулятор."""
    root = tk.Tk()
    app = EmulatorApp(root, Shell(), DEFAULT_VFS_NAME)
    app.run()


if __name__ == "__main__":
    main()
