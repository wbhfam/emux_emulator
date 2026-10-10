"""Тесты XML-логирования."""

import xml.etree.ElementTree as ET
from datetime import datetime

import pytest

from logger import EventLogger, LogError


def read_events(path):
    """Список событий из лог-файла."""
    return ET.parse(path).getroot().findall("event")


def test_event_has_command_args_status_and_time(tmp_path):
    """В событии есть команда, аргументы, статус и время."""
    path = tmp_path / "log.xml"
    EventLogger(str(path)).log("ls", ["-l", "a"], True)
    event = read_events(path)[0]
    assert event.findtext("command") == "ls"
    assert [a.text for a in event.find("args")] == ["-l", "a"]
    assert event.findtext("status") == "ok"
    datetime.fromisoformat(event.findtext("datetime"))


def test_error_status(tmp_path):
    """Неудачная команда пишется со статусом error."""
    path = tmp_path / "log.xml"
    EventLogger(str(path)).log("foo", [], False)
    assert read_events(path)[0].findtext("status") == "error"


def test_events_are_appended_to_existing_log(tmp_path):
    """Новый запуск дописывает события в старый файл."""
    path = tmp_path / "log.xml"
    EventLogger(str(path)).log("ls", [], True)
    EventLogger(str(path)).log("cd", ["a"], True)
    names = [e.findtext("command") for e in read_events(path)]
    assert names == ["ls", "cd"]


def test_creates_missing_folder(tmp_path):
    """Если папки для лога нет, она создается."""
    path = tmp_path / "deep" / "log.xml"
    EventLogger(str(path)).log("ls", [], True)
    assert path.exists()


def test_wrong_xml_is_error(tmp_path):
    """Файл не в формате XML это ошибка."""
    path = tmp_path / "log.xml"
    path.write_text("not xml", encoding="utf-8")
    with pytest.raises(LogError):
        EventLogger(str(path))


def test_wrong_root_is_error(tmp_path):
    """XML с чужим корневым тегом это ошибка."""
    path = tmp_path / "log.xml"
    path.write_text("<other/>", encoding="utf-8")
    with pytest.raises(LogError):
        EventLogger(str(path))


def test_control_chars_do_not_break_xml(tmp_path):
    """Управляющие символы в аргументах не ломают файл."""
    path = tmp_path / "log.xml"
    EventLogger(str(path)).log("ls", ["a\x01b"], True)
    assert read_events(path)[0].find("args")[0].text == "ab"
