from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from data.models import ScriptInfo
from ui.cards.pill import Pill

_SLOT_W = 140


def _centered(widget: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.addStretch()
    row.addWidget(widget)
    row.addStretch()
    return row


class DependencySlot(QFrame):
    clicked = Signal(object)

    def __init__(self, script: ScriptInfo):
        super().__init__()
        self.script = script
        self.setObjectName("dep_slot")
        self.setFixedWidth(_SLOT_W)
        self.setCursor(Qt.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(6)

        name_pill = Pill(script.class_name, "pill_name")
        name_pill.setToolTip(script.file_path)
        lay.addLayout(_centered(name_pill))

        lay.addWidget(self._section("Исходящие", script.all_deps, "pill_method"))
        lay.addWidget(self._section("Входящие", script.incoming, "pill_incoming"))

        lay.addStretch()

    def _section(self, title: str, names: list[str], pill_object_name: str) -> QWidget:
        box = QWidget()
        col = QVBoxLayout(box)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)

        header = QLabel(title)
        header.setObjectName("section_label")
        header.setAlignment(Qt.AlignCenter)
        col.addWidget(header)

        if not names:
            empty = QLabel("—")
            empty.setObjectName("empty_label")
            empty.setAlignment(Qt.AlignCenter)
            col.addWidget(empty)
        else:
            for name in names:
                col.addLayout(_centered(Pill(name, pill_object_name)))

        return box

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.script)


class DependencyLaneWidget(QWidget):
    script_clicked = Signal(object)

    def __init__(self):
        super().__init__()
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(10, 10, 10, 10)
        self._lay.setSpacing(14)
        self._lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def set_scripts(self, scripts: list[ScriptInfo]):
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        ordered = sorted(scripts, key=lambda s: len(s.all_deps), reverse=True)
        for script in ordered:
            slot = DependencySlot(script)
            slot.clicked.connect(self.script_clicked.emit)
            self._lay.addWidget(slot)
