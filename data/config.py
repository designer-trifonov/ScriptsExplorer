"""Единая точка правды для настроек приложения.

Читает settings.json в корне проекта. Если файла нет или он повреждён —
используются значения по умолчанию, чтобы приложение не падало.
"""
import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")

_DEFAULTS = {
    "refactor_threshold": 4,
    "colors": {
        "bg": "#F5F5F8",
        "surface": "#FFFFFF",
        "text": "#1E1E28",
        "black": "#000000",
        "accent": "#1EA8E6",
        "accent_hover": "#28BEF8",
        "accent_pressed": "#1690C8",
        "danger": "#E05050",
        "danger_hover": "#F06060",
        "danger_pressed": "#C03030",
        "muted": "#8A8C96",
        "faint": "#AAAAAA",
        "link": "#1E6ED6",
        "border": "#DCDCE4",
        "border_strong": "#999999",
        "border_soft": "#C3C6CD",
        "pill_name": "#46BE78",
        "pill_method": "#28A8E0",
        "pill_incoming": "#E05050",
        "pill_text": "#111111",
        "dep_dot": "#E87820",
        "close": "#D83232",
        "close_hover": "#F04040",
        "close_pressed": "#B02020",
        "scrollbar_bg": "#F0F0F4",
        "scrollbar_handle": "#C0C4CC",
        "badge_orange": "#D7781E",
        "badge_blue": "#1E6ED6",
        "badge_red": "#D73232",
        "badge_dead": "#1E1E1E",
        "badge_white": "#FFFFFF",
    },
}


def _load_raw() -> dict:
    if not os.path.exists(_CONFIG_PATH):
        return {}
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _merged() -> dict:
    raw = _load_raw()
    colors = {**_DEFAULTS["colors"], **raw.get("colors", {})}
    return {
        "refactor_threshold": raw.get("refactor_threshold", _DEFAULTS["refactor_threshold"]),
        "colors": colors,
    }


SETTINGS = _merged()
REFACTOR_THRESHOLD: int = SETTINGS["refactor_threshold"]
COLORS: dict = SETTINGS["colors"]
