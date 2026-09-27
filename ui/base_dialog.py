"""Общая заготовка всплывающего окна: без рамки, с круглой кнопкой закрытия
и перетаскиванием мышью. Любое новое окно в приложении наследуется отсюда
вместо копирования этого кода."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QPoint


class DraggableFramelessDialog(QDialog):
    def __init__(self, width: int, height: int, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(width, height)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame()
        self.frame.setObjectName("detail_frame")
        outer.addWidget(self.frame)

        btn_close = QPushButton(self.frame)
        btn_close.setObjectName("btn_close_circle")
        btn_close.setFixedSize(14, 14)
        btn_close.move(width - 6 - 14, 8)
        btn_close.clicked.connect(self.accept)

        self._drag_pos = QPoint()

    def center_over(self, window) -> None:
        """Ставит окно по центру другого окна (обычно — главного окна приложения)."""
        geo = window.geometry()
        self.move(
            geo.x() + (geo.width() - self.width()) // 2,
            geo.y() + (geo.height() - self.height()) // 2,
        )

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            self.move(e.globalPosition().toPoint() - self._drag_pos)
