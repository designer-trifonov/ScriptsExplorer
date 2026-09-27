import json
import logging
import os

logger = logging.getLogger(__name__)

# S: только хранение списка проектов в JSON
STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "projects.json")


def load() -> list[dict]:
    if not os.path.exists(STORE_PATH):
        return []
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Не удалось прочитать %s: %s", STORE_PATH, e)
        return []


def save(projects: list[dict]):
    try:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.error("Не удалось сохранить %s: %s", STORE_PATH, e)


def add(name: str, path: str) -> list[dict]:
    projects = load()
    if not any(p["path"] == path for p in projects):
        projects.append({"name": name, "path": path})
        save(projects)
        logger.info("Добавлен проект: %s (%s)", name, path)
    return projects


def remove(path: str) -> list[dict]:
    projects = [p for p in load() if p["path"] != path]
    save(projects)
    logger.info("Удалён проект: %s", path)
    return projects
