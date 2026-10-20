"""Виртуальная файловая система, которая целиком хранится в памяти."""

import os

DEFAULT_VFS_NAME = "vfs"
SEPARATOR = "/"
SKIP_PARTS = ("", ".")


class VfsError(Exception):
    """Ошибка загрузки VFS."""


class Node:
    """Файл или папка в VFS."""

    def __init__(self, name, is_dir, data=b""):
        """Узел без родителя и без детей."""
        self.name = name
        self.is_dir = is_dir
        self.data = data
        self.parent = None
        self.children = {}

    @property
    def size(self):
        """Размер файла в байтах (у папки 0)."""
        return 0 if self.is_dir else len(self.data)

    def add(self, node):
        """Кладет узел в эту папку и возвращает его."""
        old = self.children.get(node.name)
        if old is not None:
            old.parent = None
        node.parent = self
        self.children[node.name] = node
        return node

    def detach(self):
        """Убирает узел из родительской папки."""
        del self.parent.children[self.name]
        self.parent = None


def fill(folder, spec):
    """Заполняет папку из словаря (dict - папка, bytes - файл)."""
    for name, value in spec.items():
        if isinstance(value, dict):
            fill(folder.add(Node(name, True)), value)
        else:
            folder.add(Node(name, False, value))


class Vfs:
    """Дерево файлов в памяти."""

    def __init__(self, name=DEFAULT_VFS_NAME):
        """Создает пустую VFS с одним корнем."""
        self.name = name
        self.root = Node("", True)

    @classmethod
    def from_dict(cls, name, spec):
        """Собирает VFS из словаря."""
        vfs = cls(name)
        fill(vfs.root, spec)
        return vfs

    def resolve(self, path, cwd):
        """Находит узел по пути, если его нет, возвращает None."""
        node = self.root if path.startswith(SEPARATOR) else cwd
        for part in path.split(SEPARATOR):
            if not node.is_dir:
                return None
            if part in SKIP_PARTS:
                continue
            if part == "..":
                node = node.parent or node
            elif part in node.children:
                node = node.children[part]
            else:
                return None
        return node

    def path_of(self, node):
        """Полный путь до узла."""
        parts = []
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return SEPARATOR + SEPARATOR.join(reversed(parts))

    def contains(self, node):
        """Проверяет, что узел все еще лежит в дереве."""
        while node.parent is not None:
            node = node.parent
        return node is self.root

    def stats(self):
        """Число папок (без корня), файлов и общий размер."""
        dirs = files = total = 0
        stack = list(self.root.children.values())
        while stack:
            node = stack.pop()
            if node.is_dir:
                dirs += 1
                stack.extend(node.children.values())
            else:
                files += 1
                total += node.size
        return dirs, files, total

    def tree_lines(self):
        """Строки с деревом файлов."""
        return [SEPARATOR] + tree_lines(self.root, "")


def tree_lines(folder, prefix):
    """Строки дерева для папки с отступом prefix."""
    lines = []
    names = sorted(folder.children)
    for index, name in enumerate(names):
        node = folder.children[name]
        last = index == len(names) - 1
        mark = "`-- " if last else "|-- "
        lines.append(prefix + mark + name + (SEPARATOR if node.is_dir else ""))
        if node.is_dir:
            extra = "    " if last else "|   "
            lines.extend(tree_lines(node, prefix + extra))
    return lines


def vfs_name(path):
    """Имя VFS по пути (имя папки), по умолчанию vfs."""
    if not path:
        return DEFAULT_VFS_NAME
    return os.path.basename(os.path.abspath(path)) or path


def read_file(path):
    """Читает файл целиком как байты."""
    try:
        with open(path, "rb") as file:
            return file.read()
    except OSError as err:
        raise VfsError(f"cannot read file '{path}': {err.strerror}")


def read_dir(path):
    """Читает папку с диска в словарь, только в память."""
    try:
        with os.scandir(path) as entries:
            items = sorted(entries, key=lambda entry: entry.name)
    except OSError as err:
        raise VfsError(f"cannot read directory '{path}': {err.strerror}")
    spec = {}
    for entry in items:
        if entry.is_dir(follow_symlinks=False):
            spec[entry.name] = read_dir(entry.path)
        elif entry.is_file():
            spec[entry.name] = read_file(entry.path)
    return spec


def load_vfs(path):
    """Загружает VFS из папки на диске в память."""
    if not os.path.exists(path):
        raise VfsError(f"path not found: {path}")
    if not os.path.isdir(path):
        raise VfsError(f"wrong format, not a directory: {path}")
    return Vfs.from_dict(vfs_name(path), read_dir(path))
