"""Считает, каким должен стать размер песочницы, чтобы вместить её содержимое."""
import logging

logger = logging.getLogger(__name__)

MIN_WIDTH  = 160
MIN_HEIGHT = 70
TITLE_H    = 22
_PADDING   = 10


def required_size(item_positions: list[tuple[int, int, int, int]]) -> tuple[int, int]:
    """item_positions — [(x, y, w, h), ...] уже размещённых элементов (координаты
    внутри содержимого песочницы, без учёта заголовка). Возвращает минимальный
    (width, height) всей песочницы вместе с заголовком."""
    if not item_positions:
        size = (MIN_WIDTH, MIN_HEIGHT)
        logger.info("Пустая песочница — размер по умолчанию %s", size)
        return size

    max_x = max(x + w for x, y, w, h in item_positions)
    max_y = max(y + h for x, y, w, h in item_positions)
    size = (max(MIN_WIDTH, max_x + _PADDING), max(MIN_HEIGHT, max_y + _PADDING + TITLE_H))
    logger.info("Требуемый размер песочницы под %d элементов: %s", len(item_positions), size)
    return size
