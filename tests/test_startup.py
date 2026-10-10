"""Тесты стартового скрипта."""

from shell import Shell
from startup import run_script, strip_comment


def run(tmp_path, text, shell=None):
    """Выполняет скрипт с текстом и возвращает вывод."""
    path = tmp_path / "script.txt"
    path.write_text(text, encoding="utf-8")
    out = []
    run_script(shell or Shell(), str(path), out.append)
    return out


def test_strip_comment():
    """Комментарии после # убираются."""
    assert strip_comment("ls a # comment") == "ls a"
    assert strip_comment("# only comment") == ""
    assert strip_comment("  cd  ") == "cd"


def test_input_and_output_are_shown(tmp_path):
    """Ввод и вывод показываются как диалог."""
    out = run(tmp_path, "# start\nls -l\n\ncd a\n")
    assert out == ["$ ls -l", "ls -l", "$ cd a", "cd a"]


def test_error_is_reported_and_script_goes_on(tmp_path):
    """Об ошибке сообщается, остальные строки выполняются."""
    out = run(tmp_path, "foo\nls\n")
    assert "foo: command not found" in out
    assert "script error: line 1: foo" in out
    assert "ls" in out


def test_exit_stops_script(tmp_path):
    """После exit остальные строки не выполняются."""
    shell = Shell()
    out = run(tmp_path, "exit\nls\n", shell)
    assert out == ["$ exit"]
    assert not shell.running


def test_missing_script(tmp_path):
    """Если скрипта нет, об этом сообщается."""
    out = []
    ok = run_script(Shell(), str(tmp_path / "no.txt"), out.append)
    assert not ok
    assert out[0].startswith("script error: cannot read script")


def test_custom_prompt_is_used(tmp_path):
    """В скрипте используется заданное приглашение."""
    out = run(tmp_path, "ls\n", Shell(prompt="emu> "))
    assert out[0] == "emu> ls"
