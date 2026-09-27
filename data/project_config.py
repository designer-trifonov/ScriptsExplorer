"""Хранит и загружает настройки конкретного проекта — у каждого проекта
свой файл. Если файла ещё нет — значения по умолчанию."""
import hashlib
import json
import logging
import os

logger = logging.getLogger(__name__)

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "project_configs")

_DEFAULTS = {
    "sandbox": None,   # заполняется data/sandbox_store.py при первом сохранении
}


def _config_path(project_path: str) -> str:
    key = hashlib.sha1(project_path.encode("utf-8")).hexdigest()[:16]
    return os.path.join(_CONFIG_DIR, f"{key}.json")


def load(project_path: str) -> dict:
    path = _config_path(project_path)
    if not os.path.exists(path):
        logger.info("Конфиг проекта не найден, использую значения по умолчанию: %s", project_path)
        return dict(_DEFAULTS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Загружен конфиг проекта %s из %s", project_path, path)
        return {**_DEFAULTS, **data}
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Не удалось прочитать конфиг проекта %s (%s): %s", project_path, path, e)
        return dict(_DEFAULTS)


def save(project_path: str, data: dict) -> None:
    try:
        os.makedirs(_CONFIG_DIR, exist_ok=True)
        path = _config_path(project_path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Сохранён конфиг проекта %s в %s", project_path, path)
    except OSError as e:
        logger.error("Не удалось сохранить конфиг проекта %s: %s", project_path, e)
