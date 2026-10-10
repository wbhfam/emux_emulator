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


def test_start_runs_script(app, tmp_path):
    """Стартовый скрипт выполняется в окне."""
    path = tmp_path / "s.txt"
    path.write_text("# c\nls x\nfoo\n", encoding="utf-8")
    app.start(["[debug] test"], str(path))
    text = app.output.get("1.0", "end")
    assert "[debug] test" in text
    assert "$ ls x" in text
    assert "script error: line 3: foo" in text


def test_exit_in_script_closes_window(app, tmp_path):
    """exit в скрипте закрывает окно."""
    path = tmp_path / "s.txt"
    path.write_text("exit\n", encoding="utf-8")
    app.start([], str(path))
    with pytest.raises(tk.TclError):
        app.root.winfo_exists()
