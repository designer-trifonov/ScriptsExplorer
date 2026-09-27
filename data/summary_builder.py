from dataclasses import dataclass, field
from data.models import ScriptInfo


@dataclass
class SummaryItem:
    badge: str   # "dep" | "R" | "!" | "D"
    text:  str


@dataclass
class ScriptSummary:
    class_name: str
    items: list[SummaryItem] = field(default_factory=list)


def _matches_filters(script: ScriptInfo, filters: set[str]) -> bool:
    """Проверяет попадает ли скрипт хотя бы под один активный фильтр."""
    if "lifecycle" in filters:
        if script.lifecycle_count > 0:
            return True
    if "refactor" in filters:
        if script.is_refactor:
            return True
    if "dead" in filters:
        if script.is_dead:
            return True
    if "antipatterns" in filters:
        if script.total_antipatterns > 0:
            return True
    if "incoming" in filters:
        if script.incoming:
            return True
    if "outgoing" in filters:
        if script.all_deps:
            return True
    if "dependencies" in filters:
        if script.total_deps > 0:
            return True
    return False


def build_summary(scripts: list[ScriptInfo],
                  active_filters: set[str] = None) -> list[ScriptSummary]:
    """Single Responsibility: строит список замечаний по скриптам.

    active_filters — если не пустой, показывает только скрипты
    попадающие хотя бы под один фильтр.
    """
    use_filter = bool(active_filters)
    result = []

    for script in scripts:
        if use_filter and not _matches_filters(script, active_filters):
            continue

        items = []
        if script.total_deps > 0:
            items.append(SummaryItem("dep", "Высокая связность. Нужно проверить зависимости"))
        if script.is_refactor:
            items.append(SummaryItem("R",   "Возможно, нарушение SRP. Нужно проверить"))
        if script.total_antipatterns > 0:
            items.append(SummaryItem("!",   "Проверь антипаттерны"))
        if script.is_dead:
            items.append(SummaryItem("D",   "Возможно, имеется мёртвый код. Нужно проверить"))

        if items:
            result.append(ScriptSummary(class_name=script.class_name, items=items))

    return result
