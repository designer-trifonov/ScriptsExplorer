"""Свой всплывающий блок со списком связей — вместо системной Qt-подсказки.

Системная подсказка на безрамочных/прозрачных окнах ведёт себя нестабильно
по таймингу (то сразу, то через несколько секунд, то не появляется вовсе).
Свой блок показывается и прячется по явному наведению, без зависимости от
внутренней логики Qt.

Раскладка — обычные Qt-виджеты (не HTML-таблица): у имени и у стрелки
всегда фиксированная ширина колонки, поэтому стрелка не "плавает" при
разной длине имени — обрезается (с многоточием) именно имя, по пикселям
через реальные метрики шрифта, а не по количеству символов.

Место зарезервировано под ДВЕ стрелки (у одной связи в будущем может быть
одновременно входящая и исходящая) — имя заранее ужато под этот случай,
чтобы добавление второй стрелки не сдвигало раскладку.
"""
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from data.config import COLORS

_WIDTH      = 220
_PADDING    = 10
_ARROW_W    = 20
_ARROW_SLOTS = 2   # запас под одновременно входящую и исходящую связь
_NAME_W     = _WIDTH - _PADDING * 2 - _ARROW_W * _ARROW_SLOTS

_ARROW_FONT = QFont("Segoe UI", 16, QFont.Black)   # +20% размера — визуально жирнее
_NAME_FONT  = QFont("Segoe UI", 9)


def _arrow_label(char: str, color_hex: str) -> QLabel:
    lbl = QLabel(char)
    lbl.setFont(_ARROW_FONT)
    lbl.setFixedWidth(_ARROW_W)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(f"color: {color_hex};")
    return lbl


def _empty_arrow_slot() -> QLabel:
    lbl = QLabel("")
    lbl.setFixedWidth(_ARROW_W)
    return lbl


class ConnectionPopup(QWidget):
    def __init__(self, names: list[str], incoming: bool):
        super().__init__(None, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        arrow_char  = "↓" if incoming else "↑"
        arrow_color = COLORS["pill_name"] if incoming else COLORS["badge_red"]

        frame = QFrame(self)
        frame.setStyleSheet(
            "background-color: rgba(35, 35, 40, 235); border-radius: 10px;"
        )
        col = QVBoxLayout(frame)
        col.setContentsMargins(_PADDING, _PADDING - 2, _PADDING, _PADDING - 2)
        col.setSpacing(3)

        fm = None
        for name in names:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(0)

            name_lbl = QLabel()
            name_lbl.setFont(_NAME_FONT)
            name_lbl.setStyleSheet("color: white;")
            name_lbl.setFixedWidth(_NAME_W)
            fm = fm or name_lbl.fontMetrics()
            name_lbl.setText(fm.elidedText(name, Qt.ElideRight, _NAME_W))
            row.addWidget(name_lbl)

            # Один слот занят активной стрелкой, второй — пустой резерв
            # под случай, когда связь одновременно входящая и исходящая.
            row.addWidget(_arrow_label(arrow_char, arrow_color))
            row.addWidget(_empty_arrow_slot())

            col.addLayout(row)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(frame)
        self.adjustSize()

    def show_at(self, global_pos) -> None:
        self.move(global_pos)
        self.show()
