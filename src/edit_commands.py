"""Команды, которые меняют VFS (только в памяти): mkdir и mv."""

from common import CommandError, split_options
from vfs import SEPARATOR, Node

MIN_MV_ARGS = 2
NO_ENTRY = "No such file or directory"


def fail_mkdir(path, reason):
    """Ошибка mkdir в формате UNIX."""
    raise CommandError(f"mkdir: cannot create directory '{path}': {reason}")


def find_child(node, part):
    """Ищет в папке элемент по имени (., .. тоже работают)."""
    if part == ".":
        return node
    if part == "..":
        return node.parent or node
    return node.children.get(part)


def enter_or_create(node, part, last, parents, path):
    """Один шаг mkdir: заходит в папку или создает ее."""
    child = find_child(node, part)
    if child is None:
        if not (last or parents):
            fail_mkdir(path, NO_ENTRY)
        return node.add(Node(part, True))
    if not child.is_dir:
        fail_mkdir(path, "File exists" if last else "Not a directory")
    if last and not parents:
        fail_mkdir(path, "File exists")
    return child


def make_dir(shell, path, parents):
    """Создает папку по пути (с -p и промежуточные)."""
    node = shell.vfs.root if path.startswith(SEPARATOR) else shell.cwd
    parts = [part for part in path.split(SEPARATOR) if part]
    if not parts:
        fail_mkdir(path, "File exists")
    for index, part in enumerate(parts):
        last = index == len(parts) - 1
        node = enter_or_create(node, part, last, parents, path)


def cmd_mkdir(shell, args):
    """Создает папки в памяти (флаг -p создает и родителей)."""
    flags, paths = split_options(args, "p", "mkdir")
    if not paths:
        raise CommandError("mkdir: missing operand")
    errors = []
    for path in paths:
        try:
            make_dir(shell, path, "p" in flags)
        except CommandError as err:
            errors.append(str(err))
    if errors:
        raise CommandError("\n".join(errors))
    return ""


def mv_fail(src, dest, reason):
    """Ошибка mv для пары src и dest."""
    raise CommandError(f"mv: cannot move '{src}' to '{dest}': {reason}")


def find_slot(shell, node, src, dest, dest_node):
    """Находит папку и имя, куда надо положить узел."""
    if dest_node is not None and dest_node.is_dir:
        return dest_node, node.name
    if dest.endswith(SEPARATOR):
        plain = shell.vfs.resolve(dest.rstrip(SEPARATOR), shell.cwd)
        reason = NO_ENTRY if plain is None else "Not a directory"
        mv_fail(src, dest, reason)
    head, _, name = dest.rpartition(SEPARATOR)
    start = SEPARATOR if dest.startswith(SEPARATOR) else "."
    folder = shell.vfs.resolve(head or start, shell.cwd)
    if folder is None:
        mv_fail(src, dest, NO_ENTRY)
    if not folder.is_dir:
        mv_fail(src, dest, "Not a directory")
    return folder, name


def is_inside(folder, node):
    """Проверяет, что folder это node или лежит внутри node."""
    while folder is not None:
        if folder is node:
            return True
        folder = folder.parent
    return False


def check_overwrite(node, existing, src, dest):
    """Проверяет, можно ли заменить existing узлом node."""
    if existing is None:
        return
    if existing.is_dir and not node.is_dir:
        raise CommandError(
            f"mv: cannot overwrite directory '{dest}' with non-directory")
    if node.is_dir and not existing.is_dir:
        raise CommandError(
            f"mv: cannot overwrite non-directory '{dest}' "
            f"with directory '{src}'")
    if existing.is_dir and existing.children:
        mv_fail(src, dest, "Directory not empty")


def check_move(node, folder, name, src, dest):
    """Проверяет, что перенос возможен."""
    existing = folder.children.get(name)
    if existing is node:
        raise CommandError(f"mv: '{src}' and '{dest}' are the same file")
    if node.is_dir and is_inside(folder, node):
        raise CommandError(
            f"mv: cannot move '{src}' to a subdirectory of itself, "
            f"'{dest}'")
    check_overwrite(node, existing, src, dest)


def move_one(shell, src, dest, dest_node):
    """Переносит один узел."""
    node = shell.vfs.resolve(src, shell.cwd)
    if node is None:
        raise CommandError(f"mv: cannot stat '{src}': {NO_ENTRY}")
    if node is shell.vfs.root:
        raise CommandError(f"mv: cannot move '{src}': root directory")
    folder, name = find_slot(shell, node, src, dest, dest_node)
    check_move(node, folder, name, src, dest)
    node.detach()
    node.name = name
    folder.add(node)


def cmd_mv(shell, args):
    """Переименовывает или переносит файлы и папки в памяти."""
    _, operands = split_options(args, "", "mv")
    if not operands:
        raise CommandError("mv: missing file operand")
    if len(operands) < MIN_MV_ARGS:
        raise CommandError(
            f"mv: missing destination file operand after '{operands[0]}'")
    sources, dest = operands[:-1], operands[-1]
    dest_node = shell.vfs.resolve(dest, shell.cwd)
    is_dir = dest_node is not None and dest_node.is_dir
    if len(sources) > 1 and not is_dir:
        raise CommandError(f"mv: target '{dest}' is not a directory")
    errors = []
    for src in sources:
        try:
            move_one(shell, src, dest, dest_node)
        except CommandError as err:
            errors.append(str(err))
    if not shell.vfs.contains(shell.cwd):
        shell.cwd = shell.vfs.root
    if errors:
        raise CommandError("\n".join(errors))
    return ""
