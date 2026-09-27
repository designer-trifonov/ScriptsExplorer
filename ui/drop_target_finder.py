"""По точке (обычно — где отпустили мышь) находит, в какую песочницу попали,
если попали вообще."""
import logging

logger = logging.getLogger(__name__)


def find_target(global_pos, candidate_boxes: list):
    """candidate_boxes — виджеты песочниц-кандидатов (без самой перетаскиваемой).
    Если точка попадает в несколько вложенных друг в друга песочниц — возвращает
    самую маленькую по площади (то есть самую "глубокую", внутреннюю)."""
    hits = [b for b in candidate_boxes if b.rect().contains(b.mapFromGlobal(global_pos))]
    if not hits:
        logger.info("Точка (%d, %d) не попала ни в одну песочницу", global_pos.x(), global_pos.y())
        return None

    target = min(hits, key=lambda b: b.width() * b.height())
    logger.info("Точка (%d, %d) попала в песочницу: %s", global_pos.x(), global_pos.y(), target)
    return target
