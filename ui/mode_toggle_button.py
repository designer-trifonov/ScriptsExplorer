"""Кнопка-иконка переключения между режимом сетки и режимом песочницы."""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class ModeToggleButton(QPushButton):
    mode_changed = Signal(bool)   # True — песочница, False — сетка

    def __init__(self):
        super().__init__("🧩")
        self.setObjectName("btn_primary")
        # Глобальный QSS задаёт font-family: "Segoe UI" всем QWidget — в этом
        # шрифте нет глифа эмодзи, поэтому иконка была невидима. Локальный
        # stylesheet точнее (выше по специфичности) и не трогает остальные
        # свойства (фон, границы) из #btn_primary.
        self.setStyleSheet('font-family: "Segoe UI Emoji"; font-size: 14px;')
        self.setCheckable(True)
        self.setFixedSize(28, 24)
        self.setToolTip("Режим песочницы")
        self.clicked.connect(lambda checked: self.mode_changed.emit(checked))
