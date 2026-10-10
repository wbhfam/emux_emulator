"""Ядро эмулятора: разбор строки и выполнение команд."""

from commands import COMMANDS, CommandError

DEFAULT_PROMPT = "$ "


def parse_line(line):
    """Делит строку на команду и аргументы по пробелам."""
    parts = line.split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


class Result:
    """Результат выполнения одной строки."""

    def __init__(self, output, ok):
        """Запоминает вывод и признак успеха."""
        self.output = output
        self.ok = ok


class Shell:
    """Состояние оболочки и выполнение команд."""

    def __init__(self):
        """Оболочка работает, пока running равно True."""
        self.running = True

    def get_prompt(self):
        """Приглашение к вводу."""
        return DEFAULT_PROMPT

    def execute(self, line):
        """Выполняет строку и возвращает Result."""
        name, args = parse_line(line)
        if name is None:
            return Result("", True)
        func = COMMANDS.get(name)
        if func is None:
            return Result(f"{name}: command not found", False)
        try:
            return Result(func(self, args), True)
        except CommandError as err:
            text = "\n".join(filter(None, [err.output, str(err)]))
            return Result(text, False)
