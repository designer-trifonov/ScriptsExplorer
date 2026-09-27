"""Точка входа. Единственная задача — поднять процесс и запустить оркестратор:
проверить, что мы не второй экземпляр, создать QApplication, применить тему
оформления и передать управление AppOrchestrator.
"""
import logging
import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from ui.theme import STYLESHEET
from app_orchestrator import AppOrchestrator

_INSTANCE_KEY = "ScriptExplorer_v1"
_LOG_PATH = os.path.join(os.path.dirname(__file__), "script_explorer.log")

logger = logging.getLogger(__name__)


def _setup_logging():
    """Логирование всего проекта в один файл — вместо тихого проглатывания
    ошибок. INFO — обычный ход работы, WARNING/ERROR — что-то пошло не так."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        filename=_LOG_PATH,
        encoding="utf-8",
    )


def _ensure_single_instance():
    """Возвращает QLocalServer если мы первый экземпляр, иначе завершает процесс."""
    sock = QLocalSocket()
    sock.connectToServer(_INSTANCE_KEY)
    if sock.waitForConnected(200):
        sock.disconnectFromServer()
        logger.info("Уже запущен другой экземпляр — выходим")
        sys.exit(0)                      # уже запущен — выходим
    QLocalServer.removeServer(_INSTANCE_KEY)   # убираем возможный мусор
    server = QLocalServer()
    server.listen(_INSTANCE_KEY)
    return server                        # держим живым пока работает приложение


if __name__ == "__main__":
    _setup_logging()
    logger.info("Script Explorer: запуск")
    app = QApplication(sys.argv)
    _lock = _ensure_single_instance()    # убиваем дубликаты до создания окна
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(STYLESHEET)

    orchestrator = AppOrchestrator()
    orchestrator.start()

    exit_code = app.exec()
    logger.info("Script Explorer: завершение, код %d", exit_code)
    sys.exit(exit_code)
