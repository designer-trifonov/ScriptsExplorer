"""При отпускании мыши решает, куда попал перетаскиваемый элемент (пустое
место холста или другая песочница), и вызывает нужное правило расстановки.

Сама раскладка данных и сохранение — забота ui/sandbox_controller.py, этот
скрипт только определяет цель и просит пересчитать позиции.
"""
import logging
from ui.drop_target_finder import find_target
from data.sandbox_grid_fill import fill_grid

logger = logging.getLogger(__name__)


def handle_drop(dragged_widget, global_pos, candidate_boxes: list):
    """Возвращает найденную песочницу-цель или None (значит — свободное место)."""
    others = [b for b in candidate_boxes if b is not dragged_widget]
    target = find_target(global_pos, others)
    if target is None:
        logger.info("%s брошен на свободное место холста", dragged_widget)
    else:
        logger.info("%s брошен в песочницу %s", dragged_widget, target.node_id)
    return target


def reflow_content(item_sizes: list[tuple[int, int]], container_width: int):
    """Пересчитывает позиции содержимого песочницы после того, как в нём
    что-то изменилось (добавили/убрали/переставили элемент)."""
    return fill_grid(item_sizes, container_width)
