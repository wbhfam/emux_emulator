"""Тесты параметров командной строки и сборки оболочки."""

import os

from main import (build_shell, format_params, get_vfs_name, parse_args)


def test_defaults():
    """Без параметров все значения не заданы."""
    params = parse_args([])
    assert params.vfs_path is None
    assert params.prompt is None
    assert params.log_file is None
    assert params.script is None


def test_all_params():
    """Все четыре параметра читаются."""
    params = parse_args(["--vfs-path", "v", "--prompt", "> ",
                         "--log-file", "l.xml", "--script", "s.txt"])
    assert params.vfs_path == "v"
    assert params.prompt == "> "
    assert params.log_file == "l.xml"
    assert params.script == "s.txt"


def test_debug_output_has_all_params():
    """В отладочном выводе есть все параметры."""
    text = "\n".join(format_params(parse_args(["--prompt", "> "])))
    for name in ("vfs-path", "prompt", "log-file", "script"):
        assert name in text
    assert "'> '" in text
    assert "(not set)" in text


def test_vfs_name():
    """Имя VFS берется из пути, по умолчанию vfs."""
    assert get_vfs_name(None) == "vfs"
    assert get_vfs_name(os.path.join("a", "myvfs")) == "myvfs"


def test_build_shell_with_prompt_and_log(tmp_path):
    """Оболочка получает приглашение и логгер."""
    log = tmp_path / "log.xml"
    params = parse_args(["--prompt", "> ", "--log-file", str(log)])
    shell, errors = build_shell(params)
    shell.execute("ls")
    assert errors == []
    assert shell.get_prompt() == "> "
    assert log.exists()


def test_bad_log_file_is_reported(tmp_path):
    """Плохой лог-файл дает ошибку, оболочка все равно создается."""
    bad = tmp_path / "bad.xml"
    bad.write_text("not xml", encoding="utf-8")
    shell, errors = build_shell(parse_args(["--log-file", str(bad)]))
    assert len(errors) == 1 and errors[0].startswith("error:")
    assert shell.logger is None
