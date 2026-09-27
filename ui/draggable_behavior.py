"""Делает любой QWidget перетаскиваемым мышью — не пишем эту логику в каждом
виджете отдельно (карточка скрипта, песочница — используют этот же кусок)."""
import logging
from PySide6.QtCore import QObject, QEvent, Qt, Signal

logger = logging.getLogger(__name__)


class DraggableBehavior(QObject):
    """Подключается к виджету через installEventFilter — сам виджет ничего
    про перетаскивание не знает."""
    drag_finished = Signal(object)   # QPoint — глобальная позиция курсора при отпускании

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self._drag_offset = None
        widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()
        if et == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._drag_offset = event.position().toPoint()
            logger.info("Начато перетаскивание: %s", self._widget)
            return False

        if et == QEvent.MouseMove and self._drag_offset is not None:
            if event.buttons() & Qt.LeftButton:
                delta = event.position().toPoint() - self._drag_offset
                self._widget.move(self._widget.pos() + delta)
            return False

        if et == QEvent.MouseButtonRelease and self._drag_offset is not None:
            self._drag_offset = None
            global_pos = event.globalPosition().toPoint()
            logger.info("Перетаскивание завершено: %s -> (%d, %d)",
                        self._widget, global_pos.x(), global_pos.y())
            self.drag_finished.emit(global_pos)
            return False

        return False
