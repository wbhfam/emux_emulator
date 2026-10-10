"""Тесты параметров командной строки и сборки оболочки."""

from main import build_shell, format_params, parse_args


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


def test_build_shell_loads_vfs():
    """VFS загружается из папки, имя берется из имени папки."""
    shell, errors = build_shell(parse_args(
        ["--vfs-path", "sample_vfs/several"]))
    assert errors == []
    assert shell.vfs.name == "several"
    assert "a.txt" in shell.vfs.root.children


def test_missing_vfs_is_reported():
    """Если VFS не найдена, есть ошибка и пустая VFS."""
    shell, errors = build_shell(parse_args(["--vfs-path", "no_such_dir"]))
    assert len(errors) == 1 and "not found" in errors[0]
    assert shell.vfs.root.children == {}
    assert shell.vfs.name == "no_such_dir"


def test_file_instead_of_vfs_is_reported():
    """Файл вместо папки это неверный формат VFS."""
    shell, errors = build_shell(parse_args(
        ["--vfs-path", "sample_vfs/minimal/hello.txt"]))
    assert len(errors) == 1 and "wrong format" in errors[0]
