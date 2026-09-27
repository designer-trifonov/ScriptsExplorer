"""Единственная реализация "пилюли" — цветного бейджика с текстом.
Используется везде, где раньше она рисовалась заново."""
from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

PILL_H = 17
PILL_FONT = QFont("Segoe UI", 9)


class Pill(QLabel):
    def __init__(self, text: str, object_name: str):
        super().__init__(text)
        self.setObjectName(object_name)
        self.setFixedHeight(PILL_H)
        self.setFont(PILL_FONT)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)


class ClickablePill(Pill):
    clicked = Signal()

    def __init__(self, text: str, object_name: str):
        super().__init__(text, object_name)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()
