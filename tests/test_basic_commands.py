"""Тесты команд ls, cd, who и uname."""

import getpass
import platform

import pytest

from shell import Shell
from vfs import Vfs


@pytest.fixture
def shell():
    """Оболочка с небольшой VFS."""
    spec = {
        "a.txt": b"abc",
        ".hid": b"1",
        "docs": {"x.txt": b"12345", "deep": {"y.txt": b""}},
    }
    return Shell(Vfs.from_dict("t", spec))


def out(shell, line):
    """Выполняет строку и возвращает вывод."""
    return shell.execute(line).output


def test_ls_default_hides_hidden(shell):
    """ls без аргументов не показывает скрытые файлы."""
    assert out(shell, "ls") == "a.txt\ndocs"


def test_ls_all(shell):
    """ls -a показывает скрытые файлы, . и .."""
    assert out(shell, "ls -a").splitlines() == [
        ".", "..", ".hid", "a.txt", "docs"]


def test_ls_long(shell):
    """ls -l показывает тип и размер."""
    assert out(shell, "ls -l").splitlines() == [
        "-        3 a.txt", "d        0 docs"]


def test_ls_combined_flags(shell):
    """Флаги можно писать вместе и по отдельности."""
    assert out(shell, "ls -la") == out(shell, "ls -a -l")
    assert ".hid" in out(shell, "ls -la")


def test_ls_path(shell):
    """ls с путем показывает чужую папку."""
    assert out(shell, "ls docs") == "deep\nx.txt"
    assert out(shell, "ls /docs/deep") == "y.txt"


def test_ls_file(shell):
    """ls для файла печатает его имя."""
    assert out(shell, "ls docs/x.txt") == "docs/x.txt"
    assert out(shell, "ls -l a.txt") == "-        3 a.txt"


def test_ls_several_paths(shell):
    """Для нескольких путей печатаются заголовки папок."""
    assert out(shell, "ls docs docs/deep") == (
        "docs:\ndeep\nx.txt\n\ndocs/deep:\ny.txt")


def test_ls_missing_path(shell):
    """Нет такого пути - ошибка, остальное все равно выводится."""
    result = shell.execute("ls docs nope")
    assert not result.ok
    assert result.output.endswith(
        "ls: cannot access 'nope': No such file or directory")
    assert "x.txt" in result.output


def test_ls_bad_option(shell):
    """Неизвестный флаг - ошибка."""
    assert out(shell, "ls -z") == "ls: invalid option -- 'z'"
    assert out(shell, "ls --all") == "ls: unrecognized option '--all'"


def test_cd_and_prompt(shell):
    """cd меняет папку, это видно в приглашении."""
    assert shell.get_prompt() == "t:/$ "
    shell.execute("cd docs/deep")
    assert shell.get_prompt() == "t:/docs/deep$ "
    assert out(shell, "ls") == "y.txt"


def test_cd_dotdot_and_root(shell):
    """cd .. поднимается вверх, cd без аргументов уходит в корень."""
    shell.execute("cd docs/deep")
    shell.execute("cd ..")
    assert shell.get_prompt() == "t:/docs$ "
    shell.execute("cd ../..")
    assert shell.get_prompt() == "t:/$ "
    shell.execute("cd docs")
    shell.execute("cd")
    assert shell.get_prompt() == "t:/$ "


def test_cd_absolute_path(shell):
    """cd работает с абсолютным путем."""
    shell.execute("cd docs")
    shell.execute("cd /")
    assert shell.get_prompt() == "t:/$ "


def test_cd_errors(shell):
    """Ошибки cd: нет папки, файл, много аргументов."""
    assert out(shell, "cd nope") == "cd: nope: No such file or directory"
    assert out(shell, "cd a.txt") == "cd: a.txt: Not a directory"
    assert out(shell, "cd a b") == "cd: too many arguments"
    assert shell.get_prompt() == "t:/$ "


def test_custom_prompt_is_not_changed_by_cd(shell):
    """Свое приглашение не зависит от папки."""
    shell.prompt = "> "
    shell.execute("cd docs")
    assert shell.get_prompt() == "> "


def test_who(shell):
    """who показывает пользователя реальной ОС и время запуска."""
    text = out(shell, "who")
    assert text.startswith(getpass.getuser())
    assert shell.start_time.strftime("%Y-%m-%d %H:%M") in text


def test_who_modes(shell):
    """who -H печатает заголовок, who -q считает пользователей."""
    assert out(shell, "who -H").splitlines()[0].split() == [
        "NAME", "LINE", "TIME"]
    assert out(shell, "who -q").endswith("# users=1")


def test_who_errors(shell):
    """Ошибки who: плохой флаг и лишний операнд."""
    assert out(shell, "who -x") == "who: invalid option -- 'x'"
    assert out(shell, "who abc") == "who: extra operand 'abc'"


def test_uname_default_is_system_name(shell):
    """uname без флагов печатает имя системы."""
    assert out(shell, "uname") == platform.uname().system
    assert out(shell, "uname -s") == platform.uname().system


def test_uname_single_flags(shell):
    """Каждый флаг дает свое поле."""
    info = platform.uname()
    assert out(shell, "uname -n") == info.node
    assert out(shell, "uname -r") == info.release
    assert out(shell, "uname -v") == info.version
    assert out(shell, "uname -m") == info.machine
    assert out(shell, "uname -o")


def test_uname_all(shell):
    """-a печатает все поля, порядок не зависит от флагов."""
    info = platform.uname()
    text = out(shell, "uname -a")
    assert text.startswith(f"{info.system} {info.node} {info.release}")
    assert out(shell, "uname -rs") == f"{info.system} {info.release}"


def test_uname_errors(shell):
    """Ошибки uname: плохой флаг и лишний операнд."""
    assert out(shell, "uname -z") == "uname: invalid option -- 'z'"
    assert out(shell, "uname x") == "uname: extra operand 'x'"
