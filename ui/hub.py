from typing import Protocol
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, Signal
import os


class ProjectStore(Protocol):
    def load(self) -> list[dict]: ...
    def add(self, name: str, path: str) -> list[dict]: ...
    def remove(self, path: str) -> list[dict]: ...


class HubWidget(QWidget):
    project_opened = Signal(dict)

    def __init__(self, store: ProjectStore):
        super().__init__()
        self._store = store
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Script Explorer")
        lbl.setObjectName("hub_title")
        header.addWidget(lbl)
        header.addStretch()

        btn_add = QPushButton("+ Добавить проект")
        btn_add.setObjectName("btn_primary")
        btn_add.setFixedHeight(28)
        btn_add.clicked.connect(self._add_project)
        header.addWidget(btn_add)

        root.addLayout(header)
        root.addSpacing(12)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        root.addWidget(line)
        root.addSpacing(16)

        lbl2 = QLabel("Последние проекты")
        lbl2.setObjectName("section_label")
        lbl2.setAlignment(Qt.AlignLeft)
        root.addWidget(lbl2)
        root.addSpacing(10)

        self._list_layout = QVBoxLayout()
        self._list_layout.setSpacing(6)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        root.addLayout(self._list_layout)
        root.addStretch()

        self._refresh()

    def _refresh(self):
        projects = self._store.load()
        self._render_projects(projects)

    def _render_projects(self, projects: list[dict]):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not projects:
            lbl = QLabel("Нет проектов")
            lbl.setObjectName("empty_label")
            self._list_layout.addWidget(lbl)
            return

        for p in projects:
            row = QHBoxLayout()
            row.setSpacing(6)
            row.setContentsMargins(0, 0, 0, 0)

            btn = QPushButton(p["name"])
            btn.setObjectName("btn_project")
            btn.setFixedHeight(28)
            btn.setFixedWidth(200)
            btn.setStyleSheet("text-align: left; padding-left: 10px;")
            btn.clicked.connect(lambda checked=False, proj=p: self._open(proj))

            btn_x = QPushButton("✕")
            btn_x.setObjectName("btn_remove")
            btn_x.setFixedSize(28, 28)
            btn_x.clicked.connect(lambda checked=False, path=p["path"]: self._remove(path))

            row.addWidget(btn)
            row.addWidget(btn_x)
            row.addStretch()

            container = QWidget()
            container.setLayout(row)
            self._list_layout.addWidget(container, alignment=Qt.AlignLeft)

    def _add_project(self):
        path = QFileDialog.getExistingDirectory(self, "Выбери папку Unity проекта")
        if not path:
            return
        name = os.path.basename(path)
        self._store.add(name, path)
        self._refresh()

    def _remove(self, path: str):
        self._store.remove(path)
        self._refresh()

    def _open(self, project: dict):
        self.project_opened.emit(project)
