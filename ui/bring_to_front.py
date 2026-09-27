"""Поднимает виджет визуально выше остальных детей того же родителя при клике —
используется песочницами (выбранная всегда сверху)."""
import logging
from PySide6.QtCore import QObject, QEvent

logger = logging.getLogger(__name__)


class BringToFrontOnClick(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self._widget.raise_()
            logger.info("Поднят наверх: %s", self._widget)
        return False
