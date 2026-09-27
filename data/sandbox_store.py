"""Сохраняет и загружает "сессию песочницы" — какие песочницы созданы, где
они стоят, какого цвета, что внутри каждой, и где лежат ещё не разложенные
скрипты. Хранится в конфиге конкретного проекта (data/project_config.py)."""
import logging
from dataclasses import dataclass, field

from data.project_config import load as load_project_config
from data.project_config import save as save_project_config

logger = logging.getLogger(__name__)


@dataclass
class SandboxNode:
    id: str
    name: str
    border_color: str
    background_color: str | None
    x: int
    y: int
    width: int
    height: int
    manually_positioned: bool = False
    script_paths: list[str] = field(default_factory=list)
    children: list["SandboxNode"] = field(default_factory=list)


@dataclass
class SandboxSession:
    root: SandboxNode
    loose_scripts: dict[str, tuple[int, int]] = field(default_factory=dict)


def _node_to_dict(node: SandboxNode) -> dict:
    return {
        "id": node.id,
        "name": node.name,
        "border_color": node.border_color,
        "background_color": node.background_color,
        "x": node.x, "y": node.y,
        "width": node.width, "height": node.height,
        "manually_positioned": node.manually_positioned,
        "script_paths": node.script_paths,
        "children": [_node_to_dict(c) for c in node.children],
    }


def _node_from_dict(data: dict) -> SandboxNode:
    return SandboxNode(
        id=data["id"],
        name=data["name"],
        border_color=data["border_color"],
        background_color=data.get("background_color"),
        x=data["x"], y=data["y"],
        width=data["width"], height=data["height"],
        manually_positioned=data.get("manually_positioned", False),
        script_paths=list(data.get("script_paths", [])),
        children=[_node_from_dict(c) for c in data.get("children", [])],
    )


def load_session(project_path: str) -> SandboxSession | None:
    config = load_project_config(project_path)
    raw = config.get("sandbox")
    if not raw:
        logger.info("У проекта %s ещё нет сохранённой сессии песочницы", project_path)
        return None
    try:
        session = SandboxSession(
            root=_node_from_dict(raw["root"]),
            loose_scripts={k: tuple(v) for k, v in raw.get("loose_scripts", {}).items()},
        )
        logger.info("Загружена сессия песочницы для %s", project_path)
        return session
    except (KeyError, TypeError) as e:
        logger.error("Сессия песочницы проекта %s повреждена, начинаю с чистого листа: %s",
                     project_path, e)
        return None


def save_session(project_path: str, session: SandboxSession) -> None:
    config = load_project_config(project_path)
    config["sandbox"] = {
        "root": _node_to_dict(session.root),
        "loose_scripts": {k: list(v) for k, v in session.loose_scripts.items()},
    }
    save_project_config(project_path, config)
    logger.info("Сохранена сессия песочницы для %s", project_path)
