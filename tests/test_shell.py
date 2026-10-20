"""Тесты парсера и команд первого этапа."""

from shell import Shell, parse_line


def test_parse_splits_by_spaces():
    """Команда и аргументы делятся по пробелам."""
    assert parse_line("ls  -l   /tmp") == ("ls", ["-l", "/tmp"])


def test_parse_empty_line():
    """Пустая строка не дает команды."""
    assert parse_line("   ") == (None, [])


def test_empty_line_does_nothing():
    """Пустая строка выполняется без ошибки и вывода."""
    result = Shell().execute("")
    assert result.ok and result.output == ""


def test_unknown_command():
    """Неизвестная команда дает ошибку."""
    result = Shell().execute("foo 1 2")
    assert not result.ok
    assert result.output == "foo: command not found"


def test_ls_stub_prints_name_and_args():
    """ls пока печатает свое имя и аргументы."""
    result = Shell().execute("ls -l dir")
    assert result.ok and result.output == "ls -l dir"


def test_cd_stub_prints_name_and_args():
    """cd пока печатает свое имя и аргументы."""
    result = Shell().execute("cd a")
    assert result.ok and result.output == "cd a"


def test_cd_too_many_arguments():
    """cd с двумя аргументами это ошибка."""
    result = Shell().execute("cd a b")
    assert not result.ok
    assert result.output == "cd: too many arguments"


def test_exit_stops_shell():
    """exit останавливает оболочку."""
    shell = Shell()
    assert shell.execute("exit").ok
    assert not shell.running


def test_exit_with_arguments_is_error():
    """exit с аргументами это ошибка, оболочка продолжает работу."""
    shell = Shell()
    result = shell.execute("exit now")
    assert not result.ok
    assert shell.running


class FakeLogger:
    """Логгер, который просто запоминает вызовы."""

    def __init__(self):
        """Пустой список событий."""
        self.events = []

    def log(self, command, args, ok):
        """Запоминает событие."""
        self.events.append((command, args, ok))


def test_commands_are_logged():
    """В лог попадают и удачные, и неудачные вызовы."""
    logger = FakeLogger()
    shell = Shell(logger=logger)
    shell.execute("ls -l")
    shell.execute("foo")
    shell.execute("")
    assert logger.events == [("ls", ["-l"], True), ("foo", [], False)]


def test_custom_prompt():
    """Можно задать свое приглашение."""
    assert Shell(prompt="emu> ").get_prompt() == "emu> "
