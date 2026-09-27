from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Signal


class MainWindow(QMainWindow):
    """Визуальная оболочка приложения: только переключение между хабом и экраном
    проекта. Ничего не знает про трей, конфиг или источники данных — их
    подключает AppOrchestrator, передавая сюда уже готовые виджеты.
    """
    hidden = Signal()   # окно свёрнуто в трей вместо закрытия

    def __init__(self, hub, view):
        super().__init__()
        self.setWindowTitle("Script Explorer")
        self.resize(520, 735)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._hub = hub
        self._view = view
        self._stack.addWidget(self._hub)
        self._stack.addWidget(self._view)

        self._hub.project_opened.connect(self._open_project)
        self._view.back_requested.connect(self._go_back)

    def _open_project(self, project: dict):
        self._view.open_project(project)
        self._stack.setCurrentWidget(self._view)

    def _go_back(self):
        self._stack.setCurrentWidget(self._hub)

    def closeEvent(self, e):
        """Сворачивание в трей вместо закрытия — саму нотификацию трея
        делает тот, кто на это подписан (AppOrchestrator)."""
        e.ignore()
        self.hide()
        self.hidden.emit()
