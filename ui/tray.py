from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QFont
from PySide6.QtCore import Qt, QRect
from data.config import COLORS


def _make_icon() -> QIcon:
    """64×64 синий круг с буквами SE — масштабируется ОС под трей."""
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QBrush(QColor(COLORS["accent"])))
    p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, 60, 60)
    p.setPen(QColor("white"))
    p.setFont(QFont("Segoe UI", 20, QFont.Bold))
    p.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, "SE")
    p.end()
    return QIcon(pm)


class TrayIcon(QSystemTrayIcon):
    """Иконка в системном трее.

    Single Responsibility: управляет только значком и его меню.
    Не знает ни про окно, ни про кнопку-пуск напрямую — обо всём
    просит оркестратора (show_window/restart/quit), который и решает,
    что для этого нужно сделать (D).
    """

    def __init__(self, app_orchestrator, parent=None):
        super().__init__(_make_icon(), parent)
        self._app = app_orchestrator
        self.setToolTip("Script Explorer")

        menu = QMenu()
        menu.addAction("Show App").triggered.connect(self._show)
        menu.addAction("Restart").triggered.connect(self._restart)
        menu.addAction("Close App").triggered.connect(self._quit)
        self.setContextMenu(menu)

        self.activated.connect(self._on_activate)
        self.show()

    # ── public ────────────────────────────────────────────────────────────────
    def notify_hidden(self):
        """Показать balloon-уведомление при первом сворачивании в трей."""
        self.showMessage(
            "Script Explorer",
            "Приложение свёрнуто в трей",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    # ── private ───────────────────────────────────────────────────────────────
    def _show(self):
        self._app.show_window()

    def _restart(self):
        self._app.restart()

    def _quit(self):
        self._app.quit()

    def _on_activate(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show()
