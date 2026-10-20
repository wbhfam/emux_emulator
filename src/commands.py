"""Команды эмулятора."""

import getpass
import platform

DEFAULT_USER = "user"
TERMINAL = "console"
UNAME_ORDER = "snrvmo"


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


def format_entry(node, label, long):
    """Одна строка для ls, в длинном формате с типом и размером."""
    if not long:
        return label
    kind = "d" if node.is_dir else "-"
    return f"{kind} {node.size:>8} {label}"


def list_dir(folder, flags):
    """Строки с содержимым папки для ls."""
    entries = []
    if "a" in flags:
        entries.append((".", folder))
        entries.append(("..", folder.parent or folder))
    for name in sorted(folder.children):
        if name.startswith(".") and "a" not in flags:
            continue
        entries.append((name, folder.children[name]))
    return [format_entry(n, label, "l" in flags) for label, n in entries]


def list_target(node, path, flags, header):
    """Текст для одного пути в ls."""
    if not node.is_dir:
        return format_entry(node, path, "l" in flags)
    lines = list_dir(node, flags)
    if header:
        lines.insert(0, f"{path}:")
    return "\n".join(lines)


def cmd_ls(shell, args):
    """Показывает содержимое папок VFS (флаги -a и -l)."""
    flags, paths = split_options(args, "al", "ls")
    targets = paths or ["."]
    blocks = []
    errors = []
    for path in targets:
        node = shell.vfs.resolve(path, shell.cwd)
        if node is None:
            errors.append(
                f"ls: cannot access '{path}': No such file or directory")
            continue
        header = len(targets) > 1
        blocks.append(list_target(node, path, flags, header))
    output = "\n\n".join(blocks)
    if errors:
        raise CommandError("\n".join(errors), output)
    return output


def cmd_cd(shell, args):
    """Меняет текущую папку (без аргументов - корень)."""
    if len(args) > 1:
        raise CommandError("cd: too many arguments")
    target = args[0] if args else "/"
    node = shell.vfs.resolve(target, shell.cwd)
    if node is None:
        raise CommandError(f"cd: {target}: No such file or directory")
    if not node.is_dir:
        raise CommandError(f"cd: {target}: Not a directory")
    shell.cwd = node
    return ""


def get_user_name():
    """Имя пользователя реальной ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return DEFAULT_USER


def cmd_who(shell, args):
    """Показывает пользователя, который работает в эмуляторе."""
    flags, operands = split_options(args, "Hq", "who")
    if operands:
        raise CommandError(f"who: extra operand '{operands[0]}'")
    user = get_user_name()
    if "q" in flags:
        return f"{user}\n# users=1"
    row = f"{user:<8} {TERMINAL:<8} {shell.start_time:%Y-%m-%d %H:%M}"
    if "H" in flags:
        return f"{'NAME':<8} {'LINE':<8} TIME\n{row}"
    return row


def uname_fields():
    """Данные о системе по флагам uname."""
    info = platform.uname()
    os_name = "GNU/Linux" if info.system == "Linux" else info.system
    return {"s": info.system, "n": info.node, "r": info.release,
            "v": info.version, "m": info.machine, "o": os_name}


def cmd_uname(shell, args):
    """Информация о системе: -s -n -r -v -m -o и -a."""
    flags, operands = split_options(args, UNAME_ORDER + "a", "uname")
    if operands:
        raise CommandError(f"uname: extra operand '{operands[0]}'")
    if "a" in flags:
        flags = set(UNAME_ORDER)
    if not flags:
        flags = {"s"}
    fields = uname_fields()
    return " ".join(fields[key] for key in UNAME_ORDER if key in flags)


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
    "who": cmd_who,
    "uname": cmd_uname,
    "vfs-info": cmd_vfs_info,
    "exit": cmd_exit,
}
