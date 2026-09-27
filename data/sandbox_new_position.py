"""Считает, куда встаёт новая песочница при создании — по сетке, в первое
свободное от других песочниц того же уровня место."""
import logging

logger = logging.getLogger(__name__)

_CELL_W = 160
_CELL_H = 70
_MARGIN = 12
_MAX_COLS = 6


def _overlaps(a: tuple, b: tuple) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def next_position(existing_rects: list[tuple[int, int, int, int]]) -> tuple[int, int]:
    """existing_rects — [(x, y, w, h), ...] уже занятых мест того же уровня."""
    col = row = 0
    while True:
        x = _MARGIN + col * (_CELL_W + _MARGIN)
        y = _MARGIN + row * (_CELL_H + _MARGIN)
        candidate = (x, y, _CELL_W, _CELL_H)
        if not any(_overlaps(candidate, r) for r in existing_rects):
            logger.info("Новая песочница встанет в (%d, %d)", x, y)
            return x, y
        col += 1
        if col >= _MAX_COLS:
            col = 0
            row += 1
