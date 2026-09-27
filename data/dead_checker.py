"""
dead_checker.py — одна задача: определить живые скрипты через сцены, префабы и ассеты.

Алгоритм:
  1. Для каждого ScriptInfo читаем .meta → берём GUID файла
  2. Сканируем .unity / .prefab / .asset → собираем GUID из m_Script
  3. Пересечение → имена живых классов

.asset покрывает ScriptableObject-экземпляры: они хранят m_Script
точно так же как MonoBehaviour, только в файле ассета а не сцены.
"""
import logging
import os
import re
from data.models import ScriptInfo

logger = logging.getLogger(__name__)

_META_GUID  = re.compile(r'^guid:\s*(\w+)', re.MULTILINE)
_SCENE_GUID = re.compile(r'm_Script:\s*\{[^}]*guid:\s*(\w+)')

_SCAN_EXT = (".unity", ".prefab", ".asset")


def _read_guid(meta_path: str) -> str | None:
    try:
        with open(meta_path, "r", encoding="utf-8", errors="ignore") as f:
            m = _META_GUID.search(f.read())
            return m.group(1) if m else None
    except OSError as e:
        logger.warning("Не удалось прочитать .meta файл %s: %s", meta_path, e)
        return None


def _collect_scene_guids(project_path: str) -> set[str]:
    guids: set[str] = set()
    assets = os.path.join(project_path, "Assets")
    if not os.path.exists(assets):
        return guids
    for root, _, files in os.walk(assets):
        for f in files:
            if not f.endswith(_SCAN_EXT):
                continue
            try:
                with open(os.path.join(root, f), "r",
                          encoding="utf-8", errors="ignore") as fh:
                    for m in _SCENE_GUID.finditer(fh.read()):
                        guids.add(m.group(1))
            except OSError as e:
                logger.warning("Не удалось прочитать файл сцены/ассета %s: %s",
                               os.path.join(root, f), e)
    return guids


def get_live_classes(scripts: list[ScriptInfo], project_path: str) -> set[str]:
    """Возвращает имена классов которые реально используются в сценах/префабах/ассетах."""
    scene_guids = _collect_scene_guids(project_path)

    live: set[str] = set()
    for script in scripts:
        meta = script.file_path + ".meta"
        guid = _read_guid(meta)
        if guid and guid in scene_guids:
            live.add(script.class_name)
    return live


def mark_dead_scripts(scripts: list[ScriptInfo], project_path: str) -> None:
    """Помечает script.is_dead для каждого скрипта: не на кого не ссылаются,
    не используются в сценах/префабах/ассетах и при этом что-то делают."""
    live_in_scenes = get_live_classes(scripts, project_path)
    for script in scripts:
        script.is_dead = (
            not script.incoming
            and script.class_name not in live_in_scenes
            and bool(script.methods)
        )
