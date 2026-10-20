"""Графический интерфейс эмулятора на tkinter."""

import tkinter as tk
from tkinter import scrolledtext

from startup import run_script

TITLE_TEMPLATE = "Эмулятор - [{}]"
FONT = ("Courier", 11)


class EmulatorApp:
    """Окно с областью вывода и строкой ввода."""

    def __init__(self, root, shell, vfs_name):
        """Ставит заголовок и создает виджеты."""
        self.root = root
        self.shell = shell
        root.title(TITLE_TEMPLATE.format(vfs_name))
        self.build_widgets()

    def build_widgets(self):
        """Создает виджеты окна."""
        self.output = scrolledtext.ScrolledText(
            self.root, width=90, height=26, font=FONT, state="disabled")
        self.output.pack(fill="both", expand=True)
        frame = tk.Frame(self.root)
        frame.pack(fill="x")
        self.prompt_label = tk.Label(frame, font=FONT)
        self.prompt_label.pack(side="left")
        self.entry = tk.Entry(frame, font=FONT)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()
        self.update_prompt()

    def update_prompt(self):
        """Обновляет текст приглашения."""
        self.prompt_label.config(text=self.shell.get_prompt())

    def print_text(self, text):
        """Добавляет строку в область вывода."""
        self.output.config(state="normal")
        self.output.insert("end", text + "\n")
        self.output.config(state="disabled")
        self.output.see("end")

    def on_enter(self, event):
        """Обработка нажатия Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.print_text(self.shell.get_prompt() + line)
        result = self.shell.execute(line)
        if result.output:
            self.print_text(result.output)
        self.update_prompt()
        if not self.shell.running:
            self.root.destroy()

    def start(self, lines, script_path):
        """Показывает стартовые строки и выполняет скрипт."""
        for line in lines:
            self.print_text(line)
        if script_path:
            run_script(self.shell, script_path, self.print_text)
            self.update_prompt()
            if not self.shell.running:
                self.root.destroy()

    def run(self, lines=(), script_path=None):
        """Запускает главный цикл окна."""
        self.root.after(0, self.start, lines, script_path)
        self.root.mainloop()
