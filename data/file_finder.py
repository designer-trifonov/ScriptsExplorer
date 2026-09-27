"""Отвечает только за одно: найти .cs файлы Unity-проекта на диске."""
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_EXCLUDE = {"Editor", "TextMesh Pro", "ithappy", "Examples", "Extras"}


def find_cs_files(project_path: str, scripts_only: bool = True,
                   exclude: set = None) -> list[str]:
    if exclude is None:
        exclude = DEFAULT_EXCLUDE

    base = os.path.join(project_path, "Assets", "Scripts") if scripts_only \
           else os.path.join(project_path, "Assets")

    if not os.path.exists(base):
        logger.warning("Папка проекта не найдена: %s", base)
        return []

    paths = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in exclude]
        for f in files:
            if f.endswith(".cs"):
                paths.append(os.path.join(root, f))

    logger.info("Найдено %d .cs файлов в %s", len(paths), base)
    return paths
