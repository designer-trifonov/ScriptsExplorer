from typing import Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QScrollArea
from PySide6.QtCore import Qt, Signal
from data.models import ScriptInfo
from data.summary_builder import build_summary
from ui.project_toolbar import ProjectToolbar
from ui.script_grid import ScriptGridWidget
from ui.script_detail import ScriptDetailDialog
from ui.summary_dialog import SummaryDialog
from ui.filter_bar import FilterBar
from ui.dependency_lane import DependencyLaneWidget
from ui.sandbox_controller import SandboxController

Scanner = Callable[[str, bool], list[ScriptInfo]]


class ProjectViewWidget(QWidget):
    back_requested = Signal()

    def __init__(self, scanner: Scanner):
        super().__init__()
        self._scanner = scanner
        self._project = None
        self._scripts: list[ScriptInfo] = []
        self._detail_dialog: ScriptDetailDialog | None = None
        self._sandbox = SandboxController()
        self._sandbox_activated_for: str | None = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(8)

        # ── Тулбар — своя, независимая зона экрана ─────────────
        self._toolbar = ProjectToolbar()
        self._toolbar.back_clicked.connect(self.back_requested.emit)
        self._toolbar.filter_toggled.connect(self._toggle_filter)
        self._toolbar.deps_toggled.connect(self._toggle_deps_mode)
        self._toolbar.sandbox_toggled.connect(self._toggle_sandbox_mode)
        self._toolbar.summary_clicked.connect(self._open_summary)
        self._toolbar.reload_clicked.connect(self._reload)
        root.addWidget(self._toolbar)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Панель фильтров ───────────────────────────────────
        self._filter_bar = FilterBar()
        self._filter_bar.scripts_only_changed.connect(self._reload)
        self._filter_bar.method_filters_changed.connect(self._grid_set_filters)
        root.addWidget(self._filter_bar)

        # ── Сетка ────────────────────────────────────────────
        self._grid = ScriptGridWidget()
        self._grid.script_clicked.connect(self._open_detail)

        self._grid_scroll = QScrollArea()
        self._grid_scroll.setWidgetResizable(True)
        self._grid_scroll.setFrameShape(QFrame.NoFrame)
        self._grid_scroll.setWidget(self._grid)
        root.addWidget(self._grid_scroll)

        # ── Лента зависимостей ────────────────────────────────
        self._lane = DependencyLaneWidget()
        self._lane.script_clicked.connect(self._open_detail)

        self._lane_scroll = QScrollArea()
        self._lane_scroll.setWidgetResizable(True)
        self._lane_scroll.setFrameShape(QFrame.NoFrame)
        self._lane_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._lane_scroll.setWidget(self._lane)
        self._lane_scroll.hide()
        root.addWidget(self._lane_scroll)

        # ── Песочница ───────────────────────────────────────────
        self._sandbox_scroll = QScrollArea()
        self._sandbox_scroll.setWidgetResizable(True)
        self._sandbox_scroll.setFrameShape(QFrame.NoFrame)
        self._sandbox_scroll.setWidget(self._sandbox.canvas())
        self._sandbox_scroll.hide()
        root.addWidget(self._sandbox_scroll)

    def open_project(self, project: dict):
        self._project = project
        self._toolbar.set_title(project["name"])
        self._reload()

    def _toggle_filter(self, checked: bool):
        self._filter_bar.setVisible(checked)

    def _toggle_deps_mode(self, checked: bool):
        if checked:
            self._toolbar.uncheck_sandbox()
            self._lane.set_scripts(self._scripts)
        self._lane_scroll.setVisible(checked)
        self._sandbox_scroll.setVisible(False)
        self._grid_scroll.setVisible(not checked)

    def _toggle_sandbox_mode(self, checked: bool):
        if checked:
            self._toolbar.uncheck_deps()
            self._activate_sandbox()
        self._sandbox_scroll.setVisible(checked)
        self._lane_scroll.setVisible(False)
        self._grid_scroll.setVisible(not checked)

    def _activate_sandbox(self):
        if not self._project:
            return
        path = self._project["path"]
        if self._sandbox_activated_for == path:
            return   # сессия для этого проекта уже подгружена в этом запуске
        self._sandbox.activate(path, self._scripts)
        self._sandbox_activated_for = path

    def _reload(self):
        if not self._project:
            return
        self._scripts = self._scanner(self._project["path"],
                                      self._filter_bar.scripts_only())
        self._toolbar.set_count(f"  {len(self._scripts)} файлов")
        self._grid.set_scripts(self._scripts)
        if self._toolbar.deps_checked():
            self._lane.set_scripts(self._scripts)

    def _open_summary(self):
        filters = self._filter_bar.active_filters()
        summaries = build_summary(self._scripts, active_filters=filters)
        dlg = SummaryDialog(summaries, total_scripts=len(self._scripts), parent=self)
        dlg.center_over(self.window())
        dlg.exec()

    def _grid_set_filters(self, filters: set):
        self._grid.set_filters(filters)

    def _open_detail(self, script: ScriptInfo):
        """Открывает окно скрипта. Немодальное — предыдущее окно (если было
        открыто) закрывается само, не нужно каждый раз жать на крестик."""
        if self._detail_dialog is not None:
            self._detail_dialog.close()

        dlg = ScriptDetailDialog(script, self._filter_bar.active_filters(), self)
        dlg.center_over(self.window())
        self._detail_dialog = dlg
        dlg.show()
