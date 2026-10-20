"""Выполнение стартового скрипта."""

import re

COMMENT = re.compile(r"(^|\s)#.*$")


def strip_comment(line):
    """Убирает комментарий (все после #) и пробелы по краям."""
    return COMMENT.sub("", line).strip()


def read_script(path):
    """Читает строки скрипта, при ошибке возвращает None и текст."""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().splitlines(), None
    except (OSError, UnicodeDecodeError) as err:
        return None, f"cannot read script '{path}': {err}"


def run_script(shell, path, emit):
    """Выполняет скрипт, показывая ввод и вывод через emit.

    Ошибочные строки не останавливают скрипт, о них сообщается.
    """
    lines, problem = read_script(path)
    if problem:
        emit(f"script error: {problem}")
        return False
    for number, raw in enumerate(lines, 1):
        line = strip_comment(raw)
        if not line:
            continue
        emit(shell.get_prompt() + line)
        result = shell.execute(line)
        if result.output:
            emit(result.output)
        if not result.ok:
            emit(f"script error: line {number}: {line}")
        if not shell.running:
            break
    return True
