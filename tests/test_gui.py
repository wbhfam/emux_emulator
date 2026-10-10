"""Тесты окна эмулятора (нужен дисплей, иначе пропускаются)."""

import tkinter as tk

import pytest

from gui import EmulatorApp
from shell import Shell


@pytest.fixture
def app():
    """Окно приложения для теста."""
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("нет дисплея")
    yield EmulatorApp(root, Shell(), "myvfs")
    try:
        root.destroy()
    except tk.TclError:
        pass


def submit(app, line):
    """Вводит строку в окно и нажимает Enter."""
    app.entry.insert(0, line)
    app.on_enter(None)


def test_title_has_vfs_name(app):
    """В заголовке есть имя VFS."""
    assert "myvfs" in app.root.title()


def test_command_output_is_shown(app):
    """Ввод и вывод команды показываются в окне."""
    submit(app, "ls a b")
    text = app.output.get("1.0", "end")
    assert "$ ls a b" in text
    assert "ls a b\n" in text


def test_error_is_shown(app):
    """Ошибка команды показывается в окне."""
    submit(app, "foo")
    assert "foo: command not found" in app.output.get("1.0", "end")


def test_exit_closes_window(app):
    """После exit окно закрывается."""
    submit(app, "exit")
    with pytest.raises(tk.TclError):
        app.root.winfo_exists()
