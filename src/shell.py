"""Ядро эмулятора: разбор строки и выполнение команд."""

from datetime import datetime

from commands import COMMANDS, CommandError
from vfs import Vfs


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

    def __init__(self, vfs=None, prompt=None, logger=None):
        """Оболочка работает, пока running равно True."""
        self.vfs = Vfs() if vfs is None else vfs
        self.cwd = self.vfs.root
        self.running = True
        self.start_time = datetime.now()
        self.prompt = prompt
        self.logger = logger

    def get_prompt(self):
        """Приглашение: свое или по умолчанию имя VFS и папка."""
        if self.prompt is not None:
            return self.prompt
        path = self.vfs.path_of(self.cwd)
        return f"{self.vfs.name}:{path}$ "

    def execute(self, line):
        """Выполняет строку, пишет в лог и возвращает Result."""
        name, args = parse_line(line)
        if name is None:
            return Result("", True)
        result = self.run_command(name, args)
        if self.logger is not None:
            self.logger.log(name, args, result.ok)
        return result

    def run_command(self, name, args):
        """Запускает команду по имени."""
        func = COMMANDS.get(name)
        if func is None:
            return Result(f"{name}: command not found", False)
        try:
            return Result(func(self, args), True)
        except CommandError as err:
            text = "\n".join(filter(None, [err.output, str(err)]))
            return Result(text, False)
