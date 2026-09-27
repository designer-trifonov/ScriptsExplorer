"""Тонкая обёртка: делает уже существующую карточку скрипта перетаскиваемой —
саму карточку, клики и бейджи не трогаем и не копируем."""
import logging
from ui.cards.script_cell_view import ScriptCellView
from ui.draggable_behavior import DraggableBehavior

logger = logging.getLogger(__name__)


def make_draggable(cell: ScriptCellView) -> DraggableBehavior:
    behavior = DraggableBehavior(cell)
    logger.info("Карточка %s стала перетаскиваемой в режиме песочницы", cell.objectName() or cell)
    return behavior
