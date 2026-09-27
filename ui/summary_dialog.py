from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget, QFrame, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from data.config import COLORS
from data.summary_builder import ScriptSummary
from ui.base_dialog import DraggableFramelessDialog

W, H = 420, 560

_FONT_NAME  = QFont("Segoe UI", 9,  QFont.Bold)
_FONT_ITEM  = QFont("Segoe UI", 9)
_FONT_HEAD  = QFont("Segoe UI", 10, QFont.Bold)

_BADGE_COLOR = {
    "dep": COLORS["badge_orange"],
    "R":   COLORS["badge_red"],
    "!":   COLORS["badge_red"],
    "D":   COLORS["badge_dead"],
}
_BADGE_LABEL = {
    "dep": "●",
    "R":   "R",
    "!":   "!",
    "D":   "D",
}


def _badge(badge: str) -> QLabel:
    lbl = QLabel(_BADGE_LABEL[badge])
    lbl.setFixedSize(17, 17)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
    color = _BADGE_COLOR.get(badge, "#888")
    lbl.setStyleSheet(
        f"background:{color}; color:white; border-radius:8px;"
    )
    return lbl


class SummaryDialog(DraggableFramelessDialog):
    def __init__(self, summaries: list[ScriptSummary],
                 total_scripts: int, parent=None):
        super().__init__(W, H, parent)

        root = QVBoxLayout(self.frame)
        root.setContentsMargins(20, 30, 20, 12)
        root.setSpacing(8)

        # ── Заголовок ─────────────────────────────────────────
        n_issues = len(summaries)
        head = QLabel(f"Аудит · {total_scripts} скриптов · {n_issues} с замечаниями")
        head.setFont(_FONT_HEAD)
        head.setObjectName("section_label")
        root.addWidget(head)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Список ────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setObjectName("method_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("method_container")
        col = QVBoxLayout(container)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)

        for summary in summaries:
            col.addWidget(self._make_script_block(summary))

        if not summaries:
            empty = QLabel("Замечаний не найдено")
            empty.setObjectName("empty_label")
            col.addWidget(empty)

        col.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

        # ── Нижняя панель ─────────────────────────────────────
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setObjectName("separator")
        root.addWidget(sep2)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        btn_copy = QPushButton("Копировать")
        btn_copy.setObjectName("btn_primary")
        btn_copy.setFixedHeight(24)
        btn_copy.clicked.connect(lambda: self._copy(summaries))
        bottom.addWidget(btn_copy)
        bottom.addStretch()
        root.addLayout(bottom)

    # ── Блок одного скрипта ───────────────────────────────────
    def _make_script_block(self, summary: ScriptSummary) -> QWidget:
        w = QWidget()
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)

        name = QLabel(summary.class_name)
        name.setFont(_FONT_NAME)
        col.addWidget(name)

        for item in summary.items:
            row = QHBoxLayout()
            row.setContentsMargins(12, 0, 0, 0)
            row.setSpacing(8)
            row.addWidget(_badge(item.badge))
            lbl = QLabel(item.text)
            lbl.setFont(_FONT_ITEM)
            row.addWidget(lbl)
            row.addStretch()
            rw = QWidget()
            rw.setLayout(row)
            col.addWidget(rw)

        return w

    # ── Копировать в буфер ────────────────────────────────────
    def _copy(self, summaries: list[ScriptSummary]):
        lines = []
        for s in summaries:
            lines.append(s.class_name)
            for item in s.items:
                lines.append(f"  [{item.badge}] {item.text}")
        QApplication.clipboard().setText("\n".join(lines))
