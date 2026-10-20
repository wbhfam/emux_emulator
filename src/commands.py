"""Команды эмулятора."""


class CommandError(Exception):
    """Ошибка выполнения команды."""

    def __init__(self, message, output=""):
        """Сообщение и вывод, который был до ошибки."""
        super().__init__(message)
        self.output = output


def stub_output(name, args):
    """Строка для команд-заглушек: имя команды и аргументы."""
    return " ".join([name] + args)


def cmd_ls(shell, args):
    """Заглушка ls."""
    return stub_output("ls", args)


def cmd_cd(shell, args):
    """Заглушка cd."""
    if len(args) > 1:
        raise CommandError("cd: too many arguments")
    return stub_output("cd", args)


def cmd_vfs_info(shell, args):
    """Служебная команда: сводка по VFS и дерево файлов."""
    if args:
        raise CommandError("vfs-info: too many arguments")
    dirs, files, total = shell.vfs.stats()
    head = [
        f"name: {shell.vfs.name}",
        f"directories: {dirs}",
        f"files: {files}",
        f"bytes: {total}",
    ]
    return "\n".join(head + shell.vfs.tree_lines())


def cmd_exit(shell, args):
    """Завершает работу эмулятора."""
    if args:
        raise CommandError("exit: too many arguments")
    shell.running = False
    return ""


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "vfs-info": cmd_vfs_info,
    "exit": cmd_exit,
}
