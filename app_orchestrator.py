"""Оркестратор приложения.

Единственное место, которое собирает визуал (MainWindow, HubWidget,
ProjectViewWidget) и логику (project_store, scan_project) вместе и
управляет жизненным циклом окна, трея и кнопки-пуска.

main.py — это только точка входа: она создаёт оркестратор и запускает его,
сама ничего не собирает и не решает.
"""
import logging
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QProcess

from ui.hub import HubWidget
from ui.project_view import ProjectViewWidget
from ui.main_window import MainWindow
from ui.tray import TrayIcon
from ui.start_button import StartButton
from data.script_scanner import scan_project
import data.project_store as project_store

logger = logging.getLogger(__name__)


class AppOrchestrator:
    def __init__(self):
        hub = HubWidget(store=project_store)
        view = ProjectViewWidget(scanner=scan_project)
        self._window = MainWindow(hub, view)
        self._window.hidden.connect(self._on_window_hidden)

        self._tray = None
        self._start_btn = None
        self._tray_noted = False   # balloon только один раз

    def start(self):
        logger.info("Оркестратор: показываю окно, создаю трей и кнопку-пуск")
        self._window.show()
        # Трей и кнопка-пуск создаются после show() — нужен готовый HWND/QApplication
        self._tray = TrayIcon(self, parent=self._window)
        self._start_btn = StartButton(self._window)

    # ── команды, которые трею и кнопке-пуску не нужно знать, как выполнять ──────
    def show_window(self):
        logger.info("Окно показано из трея/кнопки-пуска")
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def restart(self):
        logger.info("Перезапуск приложения")
        if self._start_btn:
            self._start_btn.quit()
        QProcess.startDetached(sys.executable, sys.argv)
        QApplication.quit()

    def quit(self):
        """Разблокируем StartButton перед выходом, иначе он заблокирует quit."""
        logger.info("Завершение приложения по команде пользователя")
        if self._start_btn:
            self._start_btn.quit()
        QApplication.quit()

    # ── реакция на события окна ──────────────────────────────────────────────
    def _on_window_hidden(self):
        logger.info("Окно свёрнуто в трей")
        if self._tray and not self._tray_noted:
            self._tray_noted = True
            self._tray.notify_hidden()
