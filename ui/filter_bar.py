from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QFrame
from PySide6.QtCore import Signal


def _separator(parent=None) -> QFrame:
    sep = QFrame(parent)
    sep.setFrameShape(QFrame.VLine)
    sep.setObjectName("separator")
    return sep


class FilterBar(QWidget):
    scripts_only_changed   = Signal(bool)
    method_filters_changed = Signal(object)   # emits set[str] ключей

    def __init__(self):
        super().__init__()
        self._checks: dict[str, QCheckBox] = {}
        self._build()
        self.hide()

    def scripts_only(self) -> bool:
        return self._chk_scripts.isChecked()

    def active_filters(self) -> set:
        """Возвращает набор активных ключей: lifecycle / refactor / dead /
        antipatterns / incoming / outgoing."""
        return {k for k, c in self._checks.items() if c.isChecked()}

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 6, 16, 6)
        lay.setSpacing(10)

        # Только Scripts
        self._chk_scripts = QCheckBox("Только Scripts")
        self._chk_scripts.setChecked(True)
        self._chk_scripts.stateChanged.connect(
            lambda: self.scripts_only_changed.emit(self._chk_scripts.isChecked()))
        lay.addWidget(self._chk_scripts)
        lay.addWidget(_separator())

        # Смысловые фильтры
        filters = [
            ("lifecycle",    "OnEnable / Awake / Start"),
            ("refactor",     "Рефакторинг"),
            ("dead",         "Мёртвые"),
            ("antipatterns", "Антипаттерны"),
            ("incoming",     "Входящие связи"),
            ("outgoing",     "Исходящие связи"),
            ("dependencies", "Общее количество зависимостей"),
        ]
        for key, label in filters:
            chk = QCheckBox(label)
            chk.stateChanged.connect(self._emit)
            lay.addWidget(chk)
            self._checks[key] = chk

        lay.addStretch()

    def _emit(self):
        self.method_filters_changed.emit(self.active_filters())
