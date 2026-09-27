"""Анимирует переезд виджета на новую позицию — вместо мгновенного прыжка,
когда содержимое песочницы переставляется."""
import logging
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

logger = logging.getLogger(__name__)

_DURATION_MS = 200


def animate_move(widget, new_pos, duration_ms: int = _DURATION_MS) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(widget.pos())
    anim.setEndValue(new_pos)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    logger.info("Анимация перемещения: %s -> (%d, %d)", widget, new_pos.x(), new_pos.y())
    return anim
