"""Оркестратор режима песочницы.

Единственное место, которое знает и про данные (data/sandbox_store,
sandbox_new_position, sandbox_grid_fill, sandbox_autosize), и про визуал
(sandbox_canvas, sandbox_box_view, draggable_script_card) одновременно.
При включении режима подгружает сохранённую сессию проекта в холст; при
любом изменении (создание/перетаскивание песочницы, перетаскивание
скрипта) — пересчитывает раскладку и сохраняет сессию обратно.
"""
import logging
import uuid
from PySide6.QtCore import QPoint

from data.models import ScriptInfo
from data.sandbox_store import SandboxNode, SandboxSession, load_session, save_session
from data.sandbox_new_position import next_position
from data.sandbox_grid_fill import fill_grid
from data.sandbox_autosize import required_size

from ui.sandbox_canvas import SandboxCanvas
from ui.sandbox_box_view import SandboxBoxView
from ui.draggable_behavior import DraggableBehavior
from ui.bring_to_front import BringToFrontOnClick
from ui.draggable_script_card import make_draggable
from ui.sandbox_drop_handler import handle_drop
from ui.cards.script_cell_view import ScriptCellView

logger = logging.getLogger(__name__)

_ROOT_SIZE = (900, 620)
_ROOT_ID = "root"
_DEFAULT_SANDBOX_COLORS = ["#1EA8E6", "#46BE78", "#E87820", "#D73232", "#8A6FD1"]


class SandboxController:
    def __init__(self):
        self._canvas = SandboxCanvas()
        self._project_path: str | None = None
        self._session: SandboxSession | None = None
        self._scripts_by_path: dict[str, ScriptInfo] = {}
        self._box_by_id: dict[str, SandboxBoxView] = {}
        self._card_by_path: dict[str, ScriptCellView] = {}
        self._color_i = 0

    def canvas(self) -> SandboxCanvas:
        return self._canvas

    # ── включение режима песочницы для конкретного проекта ────────────
    def activate(self, project_path: str, scripts: list[ScriptInfo]):
        self._project_path = project_path
        self._scripts_by_path = {s.file_path: s for s in scripts}
        self._box_by_id.clear()
        self._card_by_path.clear()

        session = load_session(project_path)
        if session is None:
            logger.info("Для проекта %s ещё нет сессии песочницы — создаю с нуля", project_path)
            root = SandboxNode(
                id=_ROOT_ID, name="Все скрипты", border_color="#1E1E28",
                background_color=None, x=0, y=0,
                width=_ROOT_SIZE[0], height=_ROOT_SIZE[1], manually_positioned=True,
                script_paths=list(self._scripts_by_path.keys()),
            )
            session = SandboxSession(root=root, loose_scripts={})
        else:
            # старые сохранённые сессии могли унести непрозрачный белый фон
            # корневой песочницы (прежний баг) — корень всегда должен быть
            # прозрачным, поэтому чиним его и при загрузке
            session.root.background_color = None

        self._session = session
        self._sync_new_scripts()
        self._rebuild()
        logger.info("Режим песочницы активирован для %s", project_path)

    # ── создать новую песочницу внутри указанной (по умолчанию — в корне) ──
    def add_sandbox(self, parent_id: str = _ROOT_ID):
        if self._session is None:
            logger.warning("Попытка создать песочницу без активного проекта")
            return
        parent = self._find_node(self._session.root, parent_id) or self._session.root
        existing = [(c.x, c.y, c.width, c.height) for c in parent.children]
        x, y = next_position(existing)
        color = _DEFAULT_SANDBOX_COLORS[self._color_i % len(_DEFAULT_SANDBOX_COLORS)]
        self._color_i += 1
        node = SandboxNode(
            id=str(uuid.uuid4())[:8], name=f"Песочница {len(parent.children) + 1}",
            border_color=color, background_color=None, x=x, y=y, width=160, height=70,
        )
        parent.children.append(node)
        logger.info("Создана новая песочница '%s' (%s) внутри '%s'", node.name, node.id, parent.name)
        self._rebuild()
        self._save()

    # ── построение всего визуального дерева из модели ──────────────────
    def _rebuild(self):
        if self._session is None:
            return
        self._box_by_id.clear()
        self._card_by_path.clear()
        root_box = self._build_box(self._session.root, None)
        self._canvas.set_root(root_box)

    def _build_box(self, node: SandboxNode, parent) -> SandboxBoxView:
        box = SandboxBoxView(node.id, node.name, node.border_color, node.background_color, parent)
        box.move(node.x, node.y)
        box.show()
        self._box_by_id[node.id] = box

        drag = DraggableBehavior(box)
        drag.drag_finished.connect(lambda pos, n=node, b=box: self._on_box_dropped(n, b, pos))
        BringToFrontOnClick(box)
        box.create_sandbox_requested.connect(lambda n=node: self.add_sandbox(n.id))

        # сначала вложенные песочницы, потом обычные скрипты — так песочницы
        # всегда идут раньше скриптов внутри одной и той же сетки
        auto_items: list[tuple[str, object, int, int]] = []   # (kind, obj, w, h)

        for child in node.children:
            if child.manually_positioned:
                child_box = self._build_box(child, box.content)
                child_box.move(child.x, child.y)
            else:
                child_box = self._build_box(child, box.content)
                auto_items.append(("box", child, child_box.width(), child_box.height()))

        loose_here = {p: pos for p, pos in self._session.loose_scripts.items()
                      if p in node.script_paths}
        for path in node.script_paths:
            card = self._make_card(path, box.content)
            if card is None:
                continue
            if path in loose_here:
                card.move(*loose_here[path])
            else:
                auto_items.append(("card", path, card.width(), card.height()))

        positions = fill_grid([(w, h) for _, _, w, h in auto_items], max(node.width, 160))
        placed_rects = []
        for (kind, obj, w, h), (x, y) in zip(auto_items, positions):
            if kind == "box":
                self._box_by_id[obj.id].move(x, y)
            else:
                self._card_by_path[obj].move(x, y)
            placed_rects.append((x, y, w, h))

        # ручные элементы тоже учитываем в размере, чтобы песочница не обрезала их
        for child in node.children:
            if child.manually_positioned:
                placed_rects.append((child.x, child.y, child.width, child.height))
        for p, (x, y) in loose_here.items():
            placed_rects.append((x, y, ScriptCellView.W, 90))

        size = required_size(placed_rects)
        box.set_size(max(node.width, size[0]), max(node.height, size[1]))
        return box

    def _make_card(self, path: str, parent) -> ScriptCellView | None:
        script = self._scripts_by_path.get(path)
        if script is None:
            logger.warning("Скрипт %s из сохранённой сессии песочницы не найден в проекте", path)
            return None
        card = ScriptCellView(script)
        card.setParent(parent)
        card.show()
        behavior = make_draggable(card)
        behavior.drag_finished.connect(lambda pos, p=path, c=card: self._on_card_dropped(p, c, pos))
        self._card_by_path[path] = card
        return card

    # ── реакция на отпускание перетаскиваемой песочницы ────────────────
    def _on_box_dropped(self, node: SandboxNode, box: SandboxBoxView, global_pos: QPoint):
        if node.id == _ROOT_ID:
            return
        candidates = [b for b in self._box_by_id.values() if b is not box]
        target = handle_drop(box, global_pos, candidates)
        if target is not None and target.node_id != node.id:
            self._move_node_into(node, target.node_id)
        else:
            node.x, node.y = box.pos().x(), box.pos().y()
            node.manually_positioned = True
            logger.info("Песочница '%s' перемещена на (%d, %d)", node.name, node.x, node.y)
        self._rebuild()
        self._save()

    # ── реакция на отпускание перетаскиваемого скрипта ─────────────────
    def _on_card_dropped(self, path: str, card: ScriptCellView, global_pos: QPoint):
        candidates = list(self._box_by_id.values())
        target = handle_drop(card, global_pos, candidates)

        self._remove_script_everywhere(self._session.root, path)
        self._session.loose_scripts.pop(path, None)

        if target is not None:
            target_node = self._find_node(self._session.root, target.node_id)
            if target_node is not None:
                target_node.script_paths.insert(0, path)
                logger.info("Скрипт %s перемещён в песочницу '%s'", path, target_node.name)
        else:
            pos = (card.pos().x(), card.pos().y())
            self._session.root.script_paths.append(path)
            self._session.loose_scripts[path] = pos
            logger.info("Скрипт %s оставлен на свободном месте (%d, %d)", path, *pos)

        self._rebuild()
        self._save()

    # ── операции над деревом модели ────────────────────────────────────
    def _move_node_into(self, node: SandboxNode, target_id: str):
        self._remove_node(self._session.root, node.id)
        target_node = self._find_node(self._session.root, target_id)
        if target_node is not None:
            node.manually_positioned = False
            target_node.children.insert(0, node)
            logger.info("Песочница '%s' вложена в '%s'", node.name, target_node.name)
        else:
            logger.error("Цель вложения %s не найдена — песочница '%s' потеряна бы, возвращаю в корень",
                         target_id, node.name)
            self._session.root.children.append(node)

    def _remove_node(self, root: SandboxNode, node_id: str):
        root.children = [c for c in root.children if c.id != node_id]
        for c in root.children:
            self._remove_node(c, node_id)

    def _find_node(self, root: SandboxNode, node_id: str) -> SandboxNode | None:
        if root.id == node_id:
            return root
        for c in root.children:
            found = self._find_node(c, node_id)
            if found is not None:
                return found
        return None

    def _remove_script_everywhere(self, node: SandboxNode, path: str):
        if path in node.script_paths:
            node.script_paths.remove(path)
        for c in node.children:
            self._remove_script_everywhere(c, path)

    def _sync_new_scripts(self):
        known = self._collect_paths(self._session.root)
        added = 0
        for path in self._scripts_by_path:
            if path not in known:
                self._session.root.script_paths.append(path)
                added += 1
        if added:
            logger.info("Добавлено %d новых скриптов в корневую песочницу", added)

    def _collect_paths(self, node: SandboxNode) -> set[str]:
        paths = set(node.script_paths)
        for c in node.children:
            paths |= self._collect_paths(c)
        return paths

    def _save(self):
        if self._project_path and self._session:
            save_session(self._project_path, self._session)
