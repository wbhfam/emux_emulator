"""Тесты команд mkdir и mv."""

import pytest

from shell import Shell
from vfs import Vfs


@pytest.fixture
def shell():
    """Оболочка с небольшой VFS."""
    spec = {
        "a.txt": b"abc",
        "b.txt": b"b",
        "docs": {"x.txt": b"12345", "deep": {"y.txt": b""}},
        "empty": {},
    }
    return Shell(Vfs.from_dict("t", spec))


def out(shell, line):
    """Выполняет строку и возвращает вывод."""
    return shell.execute(line).output


def test_mkdir_creates_directory(shell):
    """mkdir создает папку в текущей папке."""
    assert shell.execute("mkdir new").ok
    assert out(shell, "ls") == "a.txt\nb.txt\ndocs\nempty\nnew"
    assert out(shell, "ls new") == ""


def test_mkdir_relative_and_absolute(shell):
    """mkdir работает с относительным и абсолютным путем."""
    shell.execute("mkdir docs/sub")
    shell.execute("mkdir /top")
    assert "sub" in out(shell, "ls docs")
    assert "top" in out(shell, "ls /")


def test_mkdir_several(shell):
    """Можно создать несколько папок за раз."""
    shell.execute("mkdir one two three")
    assert out(shell, "ls").splitlines()[-3:] == ["one", "three", "two"]


def test_mkdir_parents(shell):
    """-p создает все промежуточные папки."""
    assert shell.execute("mkdir -p x/y/z").ok
    assert out(shell, "ls x/y") == "z"


def test_mkdir_parents_existing_is_ok(shell):
    """С -p существующая папка не ошибка."""
    assert shell.execute("mkdir -p docs/deep").ok
    assert shell.execute("mkdir -p docs/deep/new").ok


def test_mkdir_exists(shell):
    """Без -p существующее имя это ошибка."""
    expect = "mkdir: cannot create directory '{}': File exists"
    assert out(shell, "mkdir docs") == expect.format("docs")
    assert out(shell, "mkdir a.txt") == expect.format("a.txt")
    assert out(shell, "mkdir -p a.txt") == expect.format("a.txt")
    assert out(shell, "mkdir /") == expect.format("/")


def test_mkdir_no_parent(shell):
    """Без -p нужна родительская папка."""
    assert out(shell, "mkdir x/y") == (
        "mkdir: cannot create directory 'x/y': No such file or directory")


def test_mkdir_through_file(shell):
    """Через файл создать папку нельзя."""
    assert out(shell, "mkdir a.txt/sub") == (
        "mkdir: cannot create directory 'a.txt/sub': Not a directory")
    assert not shell.execute("mkdir -p a.txt/sub").ok


def test_mkdir_missing_operand_and_bad_option(shell):
    """Ошибки аргументов mkdir."""
    assert out(shell, "mkdir") == "mkdir: missing operand"
    assert out(shell, "mkdir -z a") == "mkdir: invalid option -- 'z'"


def test_mkdir_partial_errors(shell):
    """Ошибка для одного пути не мешает создать остальные."""
    result = shell.execute("mkdir docs fresh")
    assert not result.ok
    assert "fresh" in out(shell, "ls")


def test_mv_rename_file(shell):
    """mv переименовывает файл."""
    assert shell.execute("mv a.txt c.txt").ok
    assert out(shell, "ls") == "b.txt\nc.txt\ndocs\nempty"
    assert out(shell, "ls -l c.txt") == "-        3 c.txt"


def test_mv_file_into_directory(shell):
    """mv в существующую папку кладет файл внутрь."""
    shell.execute("mv a.txt docs")
    assert "a.txt" in out(shell, "ls docs")
    assert "a.txt" not in out(shell, "ls")


def test_mv_several_into_directory(shell):
    """Несколько источников переносятся в папку."""
    shell.execute("mv a.txt b.txt empty")
    assert out(shell, "ls empty") == "a.txt\nb.txt"


def test_mv_directory(shell):
    """Папка переносится вместе с содержимым."""
    shell.execute("mv docs empty")
    assert out(shell, "ls empty/docs/deep") == "y.txt"
    assert "docs" not in out(shell, "ls").split()


def test_mv_rename_directory(shell):
    """Папку можно переименовать."""
    shell.execute("mv docs papers")
    assert out(shell, "ls papers") == "deep\nx.txt"


def test_mv_overwrites_file(shell):
    """Файл на месте файла заменяется."""
    shell.execute("mv a.txt b.txt")
    assert out(shell, "ls -l") == (
        "-        3 b.txt\nd        0 docs\nd        0 empty")


def test_mv_overwrites_empty_directory(shell):
    """Папка заменяет пустую папку с тем же именем."""
    shell.execute("mkdir empty/docs")
    assert shell.execute("mv docs empty").ok
    assert out(shell, "ls empty/docs") == "deep\nx.txt"


def test_mv_with_dots_and_absolute(shell):
    """mv понимает .. и абсолютные пути."""
    shell.execute("cd docs")
    shell.execute("mv x.txt ..")
    shell.execute("mv ../a.txt /empty/z.txt")
    assert "x.txt" in out(shell, "ls ..")
    assert out(shell, "ls /empty") == "z.txt"


def test_mv_moves_current_directory(shell):
    """Если перенести текущую папку, приглашение обновится."""
    shell.execute("cd docs")
    shell.execute("mv /docs /empty")
    assert shell.get_prompt() == "t:/empty/docs$ "


def test_mv_errors_missing_operands(shell):
    """Ошибки аргументов mv."""
    assert out(shell, "mv") == "mv: missing file operand"
    assert out(shell, "mv a.txt") == (
        "mv: missing destination file operand after 'a.txt'")
    assert out(shell, "mv -f a b") == "mv: invalid option -- 'f'"


def test_mv_missing_source(shell):
    """Нет источника - ошибка."""
    assert out(shell, "mv nope docs") == (
        "mv: cannot stat 'nope': No such file or directory")


def test_mv_target_not_directory(shell):
    """Несколько источников требуют папку в конце."""
    assert out(shell, "mv a.txt b.txt c.txt") == (
        "mv: target 'c.txt' is not a directory")
    assert out(shell, "mv a.txt b.txt docs/x.txt") == (
        "mv: target 'docs/x.txt' is not a directory")


def test_mv_missing_destination_folder(shell):
    """Нет папки назначения - ошибка."""
    assert out(shell, "mv a.txt nope/c.txt") == (
        "mv: cannot move 'a.txt' to 'nope/c.txt': "
        "No such file or directory")
    assert not shell.execute("mv a.txt nope/").ok
    assert out(shell, "mv a.txt b.txt/") == (
        "mv: cannot move 'a.txt' to 'b.txt/': Not a directory")
    assert out(shell, "mv a.txt b.txt/c") == (
        "mv: cannot move 'a.txt' to 'b.txt/c': Not a directory")


def test_mv_into_itself(shell):
    """Папку нельзя перенести внутрь себя."""
    text = out(shell, "mv docs docs/deep")
    assert text == (
        "mv: cannot move 'docs' to a subdirectory of itself, 'docs/deep'")
    assert out(shell, "ls docs") == "deep\nx.txt"


def test_mv_same_file(shell):
    """Перенос файла в самого себя - ошибка."""
    assert out(shell, "mv a.txt a.txt") == (
        "mv: 'a.txt' and 'a.txt' are the same file")
    assert out(shell, "mv a.txt .") == "mv: 'a.txt' and '.' are the same file"


def test_mv_overwrite_errors(shell):
    """Нельзя смешивать файлы и папки при замене."""
    assert out(shell, "mv docs a.txt") == (
        "mv: cannot overwrite non-directory 'a.txt' with directory 'docs'")
    shell.execute("mkdir empty/a.txt")
    assert out(shell, "mv a.txt empty") == (
        "mv: cannot overwrite directory 'empty' with non-directory")


def test_mv_overwrite_non_empty_directory(shell):
    """Непустую папку заменить нельзя."""
    shell.execute("mkdir -p empty/docs/inner")
    assert out(shell, "mv docs empty") == (
        "mv: cannot move 'docs' to 'empty': Directory not empty")


def test_mv_root(shell):
    """Корень перенести нельзя."""
    assert not shell.execute("mv / docs").ok


def test_mv_partial_errors(shell):
    """Ошибка для одного источника не мешает остальным."""
    result = shell.execute("mv nope a.txt docs")
    assert not result.ok
    assert "a.txt" in out(shell, "ls docs")


def test_changes_are_only_in_memory(tmp_path):
    """Изменения VFS не трогают папку на диске."""
    from vfs import load_vfs
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    shell = Shell(load_vfs(str(tmp_path)))
    shell.execute("mkdir d")
    shell.execute("mv f.txt d")
    assert [p.name for p in tmp_path.iterdir()] == ["f.txt"]
