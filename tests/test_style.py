"""Проверка правил оформления кода из задания."""

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_LINE = 80
MAX_FUNC_LINES = 40
MAX_ARGS = 7
MAX_COMPLEXITY = 10
MAX_FILE_LINES = 1000
ALLOWED_NUMBERS = (0, 1)
VAR_NAME = re.compile(r"^[a-z_][a-z0-9_]*$|^[A-Z][A-Z0-9_]*$")
CLASS_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def python_files():
    """Все python-файлы из src и tests."""
    found = []
    for folder in ("src", "tests"):
        found.extend((ROOT / folder).rglob("*.py"))
    return sorted(found)


def parse(path):
    """Дерево ast для файла."""
    return ast.parse(path.read_text(encoding="utf-8"))


def functions(tree):
    """Все функции в дереве."""
    kinds = (ast.FunctionDef, ast.AsyncFunctionDef)
    return [n for n in ast.walk(tree) if isinstance(n, kinds)]


def complexity(func):
    """Простая оценка цикломатической сложности."""
    total = 1
    for node in ast.walk(func):
        if isinstance(node, ast.BoolOp):
            total += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            total += 1 + len(node.ifs)
        elif isinstance(node, (ast.If, ast.IfExp, ast.For, ast.While,
                               ast.ExceptHandler, ast.Assert)):
            total += 1
    return total


def arg_count(func):
    """Число аргументов функции."""
    args = func.args
    names = args.posonlyargs + args.args + args.kwonlyargs
    return len(names) + bool(args.vararg) + bool(args.kwarg)


def is_store(node):
    """Имя в этом месте присваивается."""
    return isinstance(node.ctx, ast.Store)


def test_line_length():
    """Строки не длиннее 80 символов."""
    for path in python_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            assert len(line) <= MAX_LINE, f"{path.name}:{number}"


def test_file_size():
    """Файлы не длиннее 1000 строк."""
    for path in python_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= MAX_FILE_LINES, path.name


def test_function_size_and_args():
    """Функции короткие и без большого числа аргументов."""
    for path in python_files():
        for func in functions(parse(path)):
            size = func.end_lineno - func.lineno + 1
            assert size <= MAX_FUNC_LINES, f"{path.name}:{func.name}"
            assert arg_count(func) <= MAX_ARGS, f"{path.name}:{func.name}"


def test_complexity():
    """Цикломатическая сложность не больше 10."""
    for path in python_files():
        for func in functions(parse(path)):
            assert complexity(func) <= MAX_COMPLEXITY, func.name


def test_docstrings():
    """У модулей, классов и функций есть docstring."""
    for path in python_files():
        tree = parse(path)
        assert ast.get_docstring(tree), path.name
        for func in functions(tree):
            assert ast.get_docstring(func), f"{path.name}:{func.name}"
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert ast.get_docstring(node), node.name


def test_no_magic_numbers_in_compare():
    """В сравнениях нет чисел кроме 0 и 1."""
    for path in python_files():
        for node in ast.walk(parse(path)):
            if not isinstance(node, ast.Compare):
                continue
            for item in [node.left] + node.comparators:
                if isinstance(item, ast.Constant):
                    value = item.value
                    is_num = isinstance(value, (int, float))
                    bad = is_num and value not in ALLOWED_NUMBERS
                    assert not bad, f"{path.name}:{node.lineno}"


def node_names(node):
    """Имена функций, переменных и псевдонимов, заданные узлом."""
    if isinstance(node, ast.FunctionDef):
        return [node.name]
    if isinstance(node, ast.alias):
        return [node.asname] if node.asname else []
    if isinstance(node, ast.Name) and is_store(node):
        return [node.id]
    return []


def test_names_follow_pep8():
    """Имена классов, функций, переменных и псевдонимов по PEP8."""
    for path in python_files():
        for node in ast.walk(parse(path)):
            if isinstance(node, ast.ClassDef):
                assert CLASS_NAME.match(node.name), node.name
            for name in node_names(node):
                assert VAR_NAME.match(name), f"{path.name}:{name}"
