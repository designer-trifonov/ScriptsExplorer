"""Координирует шаги сканирования проекта. Сам ничего не ищет и не решает —
каждый шаг делегирован своему модулю:
  1. file_finder             — найти .cs файлы на диске
  2. script_parser           — разобрать каждый файл
  3. dependency_graph        — построить связи "кто на кого ссылается" (классы)
  4. method_dependency_graph — то же самое, но по методам
  5. dead_checker            — определить мёртвые скрипты
"""
import logging

from data.file_finder import find_cs_files
from data.script_parser import parse_file, collect_class_names
from data.dependency_graph import attach_incoming
from data.method_dependency_graph import attach_method_incoming
from data.dead_checker import mark_dead_scripts
from data.models import ScriptInfo

logger = logging.getLogger(__name__)


def scan_project(project_path: str, scripts_only: bool = True,
                 exclude: set = None) -> list[ScriptInfo]:
    logger.info("Сканирование проекта: %s (scripts_only=%s)", project_path, scripts_only)

    paths = find_cs_files(project_path, scripts_only, exclude)
    if not paths:
        logger.warning("В проекте не найдено ни одного .cs файла: %s", project_path)
        return []

    project_classes = collect_class_names(paths)
    results = [parse_file(p, project_classes) for p in paths]

    attach_incoming(results)
    attach_method_incoming(results)
    mark_dead_scripts(results, project_path)

    dead_count = sum(1 for s in results if s.is_dead)
    logger.info("Просканировано %d скриптов, мёртвых: %d", len(results), dead_count)

    return results
