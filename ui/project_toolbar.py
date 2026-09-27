from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
from ui.mode_toggle_button import ModeToggleButton


class ProjectToolbar(QWidget):
    """Верхняя панель экрана проекта — своя, независимая зона экрана.

    Только сообщает о нажатиях через сигналы; ничего не знает о сетке,
    ленте зависимостей, песочнице или диалогах, которые эти нажатия
    обрабатывают.
    """
    back_clicked      = Signal()
    filter_toggled    = Signal(bool)
    deps_toggled      = Signal(bool)
    sandbox_toggled   = Signal(bool)
    summary_clicked   = Signal()
    reload_clicked    = Signal()

    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        btn_back = QPushButton("← Назад")
        btn_back.setObjectName("btn_primary")
        btn_back.setFixedHeight(24)
        btn_back.clicked.connect(self.back_clicked.emit)
        lay.addWidget(btn_back)

        lay.addStretch()

        self._title = QLabel("")
        self._title.setObjectName("hub_title")
        lay.addWidget(self._title)

        lay.addStretch()

        self._btn_sandbox = ModeToggleButton()
        self._btn_sandbox.mode_changed.connect(self.sandbox_toggled.emit)
        lay.addWidget(self._btn_sandbox)

        self._btn_filter = QPushButton("Фильтр")
        self._btn_filter.setObjectName("btn_primary")
        self._btn_filter.setFixedHeight(24)
        self._btn_filter.setCheckable(True)
        self._btn_filter.clicked.connect(lambda checked: self.filter_toggled.emit(checked))
        lay.addWidget(self._btn_filter)

        self._btn_deps = QPushButton("Зависимости")
        self._btn_deps.setObjectName("btn_primary")
        self._btn_deps.setFixedHeight(24)
        self._btn_deps.setCheckable(True)
        self._btn_deps.clicked.connect(lambda checked: self.deps_toggled.emit(checked))
        lay.addWidget(self._btn_deps)

        btn_summary = QPushButton("Сводка")
        btn_summary.setObjectName("btn_primary")
        btn_summary.setFixedHeight(24)
        btn_summary.clicked.connect(self.summary_clicked.emit)
        lay.addWidget(btn_summary)

        btn_reload = QPushButton("Обновить")
        btn_reload.setObjectName("btn_primary")
        btn_reload.setFixedHeight(24)
        btn_reload.clicked.connect(self.reload_clicked.emit)
        lay.addWidget(btn_reload)

        self._count_lbl = QLabel("")
        self._count_lbl.setObjectName("section_label")
        lay.addWidget(self._count_lbl)

    def set_title(self, text: str):
        self._title.setText(text)

    def set_count(self, text: str):
        self._count_lbl.setText(text)

    def deps_checked(self) -> bool:
        return self._btn_deps.isChecked()

    def sandbox_checked(self) -> bool:
        return self._btn_sandbox.isChecked()

    def uncheck_deps(self):
        self._btn_deps.blockSignals(True)
        self._btn_deps.setChecked(False)
        self._btn_deps.blockSignals(False)

    def uncheck_sandbox(self):
        self._btn_sandbox.blockSignals(True)
        self._btn_sandbox.setChecked(False)
        self._btn_sandbox.blockSignals(False)
