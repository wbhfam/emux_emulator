"""Логирование вызовов команд в XML-файл."""

import os
import re
import sys
import xml.etree.ElementTree as xml_tree
from datetime import datetime

ROOT_TAG = "log"
BAD_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class LogError(Exception):
    """Ошибка открытия или записи лог-файла."""


def clean(text):
    """Убирает символы, которые нельзя записать в XML."""
    return BAD_CHARS.sub("", text)


class EventLogger:
    """Пишет события вызова команд в XML-файл."""

    def __init__(self, path):
        """Читает существующий лог или создает новый файл."""
        self.path = path
        self.root = self.load()
        try:
            self.save()
        except OSError as err:
            raise LogError(f"cannot write log file '{path}': {err}")

    def load(self):
        """Загружает корень XML из файла, если файл уже есть."""
        if not os.path.exists(self.path):
            return xml_tree.Element(ROOT_TAG)
        try:
            root = xml_tree.parse(self.path).getroot()
        except (xml_tree.ParseError, OSError) as err:
            raise LogError(f"cannot read log file '{self.path}': {err}")
        if root.tag != ROOT_TAG:
            raise LogError(f"wrong log format in '{self.path}'")
        return root

    def save(self):
        """Записывает дерево в файл."""
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        xml_tree.indent(self.root)
        tree = xml_tree.ElementTree(self.root)
        tree.write(self.path, encoding="utf-8", xml_declaration=True)

    def log(self, command, args, ok):
        """Добавляет событие вызова команды."""
        event = xml_tree.SubElement(self.root, "event")
        now = datetime.now().isoformat(timespec="seconds")
        xml_tree.SubElement(event, "datetime").text = now
        xml_tree.SubElement(event, "command").text = clean(command)
        items = xml_tree.SubElement(event, "args")
        for arg in args:
            xml_tree.SubElement(items, "arg").text = clean(arg)
        xml_tree.SubElement(event, "status").text = "ok" if ok else "error"
        try:
            self.save()
        except OSError as err:
            print(f"log error: {err}", file=sys.stderr)
