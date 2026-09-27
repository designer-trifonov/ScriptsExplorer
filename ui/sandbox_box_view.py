"""Визуал одной песочницы: рамка, фон, название сверху слева.

Без перетаскивания и без подъёма слоя — это отдельные поведения
(ui/draggable_behavior.py, ui/bring_to_front.py), которые цепляет к этому
виджету тот, кто его создаёт (ui/sandbox_controller.py)."""
import logging
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, Signal, QObject, QEvent

logger = logging.getLogger(__name__)

TITLE_H = 22
_RADIUS = 10


class _DoubleClickToCreate(QObject):
    """Ловит двойной клик на пустом месте content-области песочницы —
    сам content ничего не рисует, поэтому клик до него не всегда доходит
    как paintEvent, но событие мыши ловится исправно."""
    def __init__(self, box: "SandboxBoxView"):
        super().__init__(box)
        self._box = box
        box.content.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonDblClick:
            self._box.create_sandbox_requested.emit()
        return False


class SandboxBoxView(QWidget):
    create_sandbox_requested = Signal()

    def __init__(self, node_id: str, name: str, border_color: str,
                 background_color: str | None = None, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.name = name
        self.border_color = border_color
        self.background_color = background_color

        self._title = QLabel(name, self)
        self._title.setStyleSheet(f"color: {border_color}; background: transparent;")
        self._title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self._title.move(10, 4)

        self.content = QWidget(self)
        self.content.move(0, TITLE_H)
        self._dbl_click = _DoubleClickToCreate(self)

        logger.info("Создана песочница '%s' (%s)", name, node_id)

    def mouseDoubleClickEvent(self, e):
        logger.info("Двойной клик по песочнице %s — запрос вложенной песочницы", self.node_id)
        self.create_sandbox_requested.emit()

    def set_size(self, width: int, height: int):
        self.resize(width, height)
        self.content.resize(width, max(0, height - TITLE_H))

    def set_name(self, name: str):
        self.name = name
        self._title.setText(name)
        logger.info("Песочница %s переименована в '%s'", self.node_id, name)

    def set_colors(self, border_color: str, background_color: str | None):
        self.border_color = border_color
        self.background_color = background_color
        self._title.setStyleSheet(f"color: {border_color}; background: transparent;")
        self.update()
        logger.info("Песочница %s: цвета обновлены (рамка=%s, фон=%s)",
                    self.node_id, border_color, background_color)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self.background_color:
            p.setBrush(QColor(self.background_color))
        else:
            p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(self.border_color), 2))
        p.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, _RADIUS, _RADIUS)
