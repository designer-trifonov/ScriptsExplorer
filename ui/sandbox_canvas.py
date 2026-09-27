"""Холст режима песочницы — показывает дерево песочниц. Сам ничего не
сохраняет и не загружает (это ui/sandbox_controller.py), только строит
то, что ему передали."""
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout
from ui.sandbox_box_view import SandboxBoxView

logger = logging.getLogger(__name__)


class SandboxCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self._root_box: SandboxBoxView | None = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def set_root(self, root_box: SandboxBoxView):
        if self._root_box is not None:
            self._layout.removeWidget(self._root_box)
            self._root_box.deleteLater()
        self._root_box = root_box
        self._layout.addWidget(root_box)
        logger.info("Холст песочницы: корень обновлён")

    def root(self) -> SandboxBoxView | None:
        return self._root_box
