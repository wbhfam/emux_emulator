"""Общие вещи для команд: ошибка и разбор флагов."""


class CommandError(Exception):
    """Ошибка выполнения команды."""

    def __init__(self, message, output=""):
        """Сообщение и вывод, который был до ошибки."""
        super().__init__(message)
        self.output = output


def split_options(args, allowed, name):
    """Делит аргументы на буквенные флаги и операнды."""
    flags = set()
    operands = []
    options_end = False
    for arg in args:
        if options_end or arg == "-" or not arg.startswith("-"):
            operands.append(arg)
        elif arg == "--":
            options_end = True
        else:
            flags.update(check_flags(arg, allowed, name))
    return flags, operands


def check_flags(arg, allowed, name):
    """Проверяет буквы флагов вида -abc, возвращает их."""
    if arg.startswith("--"):
        raise CommandError(f"{name}: unrecognized option '{arg}'")
    for char in arg[1:]:
        if char not in allowed:
            raise CommandError(f"{name}: invalid option -- '{char}'")
    return arg[1:]
