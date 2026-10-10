"""Тесты виртуальной файловой системы."""

import pytest

from shell import Shell
from vfs import Vfs, VfsError, load_vfs, vfs_name


def sample():
    """Небольшая VFS для тестов."""
    return Vfs.from_dict("t", {
        "a.txt": b"abc",
        "dir": {"b.txt": b"12", "sub": {"c.txt": b""}},
    })


def test_vfs_name():
    """Имя VFS берется из пути, по умолчанию vfs."""
    assert vfs_name(None) == "vfs"
    assert vfs_name("some/where/myvfs") == "myvfs"


def test_resolve_absolute_and_relative():
    """Пути находятся от корня и от текущей папки."""
    vfs = sample()
    folder = vfs.resolve("/dir", vfs.root)
    assert vfs.resolve("sub/c.txt", folder).name == "c.txt"
    assert vfs.resolve("/dir/sub/../b.txt", vfs.root).name == "b.txt"
    assert vfs.resolve("..", vfs.root) is vfs.root


def test_resolve_missing_and_through_file():
    """Нет файла или путь идет через файл - None."""
    vfs = sample()
    assert vfs.resolve("nope", vfs.root) is None
    assert vfs.resolve("a.txt/x", vfs.root) is None
    assert vfs.resolve("a.txt/", vfs.root) is None


def test_path_of():
    """Полный путь строится по родителям."""
    vfs = sample()
    node = vfs.resolve("/dir/sub", vfs.root)
    assert vfs.path_of(node) == "/dir/sub"
    assert vfs.path_of(vfs.root) == "/"


def test_stats_and_tree():
    """Сводка и дерево."""
    vfs = sample()
    assert vfs.stats() == (2, 3, 5)
    assert vfs.tree_lines() == [
        "/",
        "|-- a.txt",
        "`-- dir/",
        "    |-- b.txt",
        "    `-- sub/",
        "        `-- c.txt",
    ]


def test_load_minimal():
    """Минимальная VFS с одним файлом."""
    vfs = load_vfs("sample_vfs/minimal")
    assert vfs.name == "minimal"
    assert list(vfs.root.children) == ["hello.txt"]


def test_load_several_files():
    """VFS с несколькими файлами и папкой."""
    vfs = load_vfs("sample_vfs/several")
    assert set(vfs.root.children) == {
        "a.txt", "b.txt", "notes.txt", ".hidden", "docs"}


def test_load_three_levels():
    """VFS с вложенностью больше трех уровней."""
    vfs = load_vfs("sample_vfs/deep")
    path = "/level1/level2/level3/level4/deepest.txt"
    assert vfs.resolve(path, vfs.root).data == b"the deepest file\n"


def test_load_empty_dir(tmp_path):
    """Пустая папка дает пустую VFS."""
    assert load_vfs(str(tmp_path)).root.children == {}


def test_binary_data_is_kept_as_bytes(tmp_path):
    """Двоичные данные читаются как есть."""
    (tmp_path / "x.bin").write_bytes(bytes(range(256)))
    node = load_vfs(str(tmp_path)).root.children["x.bin"]
    assert node.data == bytes(range(256))


def test_load_does_not_change_disk(tmp_path):
    """Загрузка и работа в памяти не меняют папку на диске."""
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    vfs = load_vfs(str(tmp_path))
    vfs.root.children["f.txt"].detach()
    assert [p.name for p in tmp_path.iterdir()] == ["f.txt"]


def test_load_missing_path():
    """Нет такой папки - ошибка."""
    with pytest.raises(VfsError, match="not found"):
        load_vfs("no_such_dir")


def test_load_file_is_wrong_format():
    """Файл вместо папки - ошибка формата."""
    with pytest.raises(VfsError, match="wrong format"):
        load_vfs("sample_vfs/minimal/hello.txt")


def test_vfs_info_command():
    """Служебная команда vfs-info показывает сводку и дерево."""
    shell = Shell(sample())
    out = shell.execute("vfs-info").output.splitlines()
    assert out[:4] == ["name: t", "directories: 2", "files: 3", "bytes: 5"]
    assert "|-- a.txt" in out


def test_vfs_info_with_args_is_error():
    """vfs-info с аргументами это ошибка."""
    assert not Shell(sample()).execute("vfs-info x").ok
