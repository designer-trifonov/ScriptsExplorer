from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QWidget, QFrame, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from data.config import COLORS
from data.models import ScriptInfo
from ui.base_dialog import DraggableFramelessDialog
from ui.cards.pill import Pill, ClickablePill
from ui.connection_popup import ConnectionPopup

W, H = 384, int(384 * 1.414)


class _ConnectionDot(QLabel):
    """Кружок с числом связей метода. Сам показывает свой всплывающий список
    по наведению — через ConnectionPopup, а не системную Qt-подсказку."""

    def __init__(self, count: int, color_hex: str, names: list[str], incoming: bool):
        super().__init__(str(count))
        self._names = names
        self._incoming = incoming
        self._popup: ConnectionPopup | None = None

        self.setFixedSize(17, 17)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Segoe UI", 7))
        self.setStyleSheet(f"background-color: {color_hex}; border-radius: 8px; color: black;")

    def enterEvent(self, e):
        if self._names:
            self._popup = ConnectionPopup(self._names, self._incoming)
            self._popup.show_at(self.mapToGlobal(self.rect().bottomLeft()))

    def leaveEvent(self, e):
        if self._popup is not None:
            self._popup.close()
            self._popup = None


class ScriptDetailDialog(DraggableFramelessDialog):
    def __init__(self, script: ScriptInfo, active_filters: set = None, parent=None):
        super().__init__(W, H, parent)
        self._filters = active_filters or set()

        root = QVBoxLayout(self.frame)
        root.setContentsMargins(20, 30, 20, 20)
        root.setSpacing(0)

        # ── Зелёная пилюля — имя, по центру, ширина по тексту ─
        name_pill = ClickablePill(script.class_name, "pill_name")
        name_pill.setToolTip(script.file_path)
        name_pill.clicked.connect(
            lambda: QApplication.clipboard().setText(script.file_path))

        name_row = QHBoxLayout()
        name_row.addStretch()
        name_row.addWidget(name_pill)
        name_row.addStretch()
        root.addLayout(name_row)
        root.addSpacing(8)

        # ── Методы ─────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setObjectName("method_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("method_container")
        col = QVBoxLayout(container)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)

        if not script.methods:
            lbl = QLabel("Нет методов")
            lbl.setObjectName("empty_label")
            col.addWidget(lbl)
        else:
            for m in script.methods:
                row = QHBoxLayout()
                row.setContentsMargins(0, 0, 0, 0)
                row.setSpacing(4)

                pill = Pill(m.name, "pill_method")
                row.addWidget(pill)

                # Красный — исходящие вызовы метода, зелёный — входящие.
                # Каждый виден только пока включён его фильтр — как и на
                # карточках в сетке.
                if "outgoing" in self._filters and m.dep_count > 0:
                    out_dot = _ConnectionDot(m.dep_count, COLORS["badge_red"],
                                             m.deps, incoming=False)
                    row.addWidget(out_dot, alignment=Qt.AlignVCenter)

                if "incoming" in self._filters and m.incoming:
                    in_dot = _ConnectionDot(len(m.incoming), COLORS["pill_name"],
                                            m.incoming, incoming=True)
                    row.addWidget(in_dot, alignment=Qt.AlignVCenter)

                row.addStretch()

                w = QWidget()
                w.setLayout(row)
                col.addWidget(w)

        col.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)
