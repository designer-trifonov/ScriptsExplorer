"""Считает, куда встаёт каждый элемент (скрипт или вложенная песочница)
внутри сетки одной песочницы — слева направо, сверху вниз, с переносом
по ширине контейнера."""
import logging

logger = logging.getLogger(__name__)

_MARGIN = 8


def fill_grid(item_sizes: list[tuple[int, int]], container_width: int,
              margin: int = _MARGIN) -> list[tuple[int, int]]:
    """item_sizes — [(w, h), ...] в порядке следования. Возвращает [(x, y), ...]
    той же длины и в том же порядке."""
    positions = []
    x = y = margin
    row_h = 0
    for w, h in item_sizes:
        if x > margin and x + w + margin > container_width:
            x = margin
            y += row_h + margin
            row_h = 0
        positions.append((x, y))
        x += w + margin
        row_h = max(row_h, h)

    logger.info("Разложено %d элементов по сетке (ширина контейнера %d)",
                len(item_sizes), container_width)
    return positions
