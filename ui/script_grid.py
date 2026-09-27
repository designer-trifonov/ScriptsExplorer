from typing import Callable
from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Qt, Signal, QTimer
from data.models import ScriptInfo
from ui.cards.script_cell_view import ScriptCellView, BadgeFlags

_CELL_W = ScriptCellView.W + 20

CellFactory = Callable[[ScriptInfo, Callable, BadgeFlags], QWidget]


def _default_cell_factory(script: ScriptInfo, on_click: Callable,
                           badges: BadgeFlags) -> QWidget:
    cell = ScriptCellView(script, badges)
    cell.clicked.connect(on_click)
    return cell


class ScriptGridWidget(QWidget):
    script_clicked = Signal(object)

    def __init__(self, cell_factory: CellFactory = None):
        super().__init__()
        self._scripts: list[ScriptInfo] = []
        self._filters: set[str] = set()
        self._cell_factory = cell_factory or _default_cell_factory
        self._grid = QGridLayout(self)
        self._grid.setSpacing(14)
        self._grid.setContentsMargins(10, 10, 10, 10)
        self._grid.setAlignment(Qt.AlignTop)
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._rebuild)

    def set_scripts(self, scripts: list[ScriptInfo]):
        self._scripts = scripts
        self._rebuild()

    def set_filters(self, filters: set):
        self._filters = filters
        if self._scripts:
            self._rebuild()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._scripts:
            self._resize_timer.start(50)

    def _badge_flags(self, script: ScriptInfo) -> BadgeFlags:
        """Бейдж виден только пока включён его фильтр — переключение
        чекбокса сразу меняет то, что показано на карточках.
        Подсчёты — готовые значения из data-слоя (ScriptInfo), сетка
        только решает, какие из них показывать прямо сейчас."""
        f = self._filters
        return BadgeFlags(
            lifecycle_count=script.lifecycle_count if "lifecycle" in f else 0,
            incoming_count=len(script.incoming) if "incoming" in f else 0,
            outgoing_count=len(script.all_deps) if "outgoing" in f else 0,
            total_deps_count=script.total_deps if "dependencies" in f else 0,
            show_refactor="refactor" in f,
            show_antipatterns="antipatterns" in f,
            show_dead="dead" in f,
        )

    def _rebuild(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        cols = max(1, self.width() // _CELL_W)

        for c in range(self._grid.columnCount()):
            self._grid.setColumnStretch(c, 0)
        for c in range(cols):
            self._grid.setColumnStretch(c, 1)

        for i, script in enumerate(self._scripts):
            row, col = divmod(i, cols)
            cell = self._cell_factory(script, self.script_clicked.emit,
                                      self._badge_flags(script))
            self._grid.addWidget(cell, row, col, Qt.AlignHCenter)
