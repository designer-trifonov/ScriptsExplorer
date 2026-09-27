"""Окошко выбора цвета рамки/фона песочницы."""
import logging
from PySide6.QtWidgets import QColorDialog
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


def pick_color(parent, initial: str = "#1EA8E6") -> str | None:
    color = QColorDialog.getColor(QColor(initial), parent, "Выбери цвет")
    if not color.isValid():
        logger.info("Выбор цвета отменён")
        return None
    hex_color = color.name()
    logger.info("Выбран цвет: %s", hex_color)
    return hex_color
