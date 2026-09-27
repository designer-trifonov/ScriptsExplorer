import ctypes
import ctypes.wintypes

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QFont, QFontMetrics

# ── Константы UI ──────────────────────────────────────────────────────────────
_LABEL   = "Script Explorer"
_FONT    = QFont("Segoe UI", 9, QFont.Bold)
_H       = 48
_PILL_H  = 32
_PILL_PX = 18
_PILL_R  = _PILL_H // 2

_ALPHA = 178
_C_BG  = QColor(0x40, 0x40, 0x40, _ALPHA)
_C_HOV = QColor(0x56, 0x56, 0x56, _ALPHA)
_C_PRE = QColor(0x2C, 0x2C, 0x2C, _ALPHA)
_C_TXT = QColor(0xFF, 0xFF, 0xFF)

_OFFSET_X = 10

# ── Win32 константы ───────────────────────────────────────────────────────────
_user32            = ctypes.windll.user32
_GWL_EXSTYLE       = -20
_GWLP_HWNDPARENT   = -8
_WS_EX_TOOLWINDOW  = 0x00000080
_WS_EX_NOACTIVATE  = 0x08000000
_HWND_TOPMOST      = -1
_SWP_NOSIZE        = 0x0001
_SWP_NOMOVE        = 0x0002
_SWP_NOACTIVATE    = 0x0010
_SWP_SHOWWINDOW    = 0x0040


def _pill_width() -> int:
    return QFontMetrics(_FONT).horizontalAdvance(_LABEL) + _PILL_PX * 2


def _win32_setup(hwnd: int):
    """Убираем owner и ставим стили — вызывается один раз после show()."""
    # Убираем неявный owner → Windows больше не скроет нас вместе с ним
    _user32.SetWindowLongPtrW(hwnd, _GWLP_HWNDPARENT, 0)
    # WS_EX_TOOLWINDOW: нет в таскбаре; WS_EX_NOACTIVATE: не крадём фокус
    style = _user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
    _user32.SetWindowLongW(hwnd, _GWL_EXSTYLE,
                           style | _WS_EX_TOOLWINDOW | _WS_EX_NOACTIVATE)


def _win32_force_show(hwnd: int, x: int, y: int, w: int, h: int):
    """SetWindowPos напрямую — показывает окно даже если Windows его скрыло."""
    _user32.SetWindowPos(
        hwnd, _HWND_TOPMOST,
        x, y, w, h,
        _SWP_NOSIZE | _SWP_NOMOVE | _SWP_NOACTIVATE | _SWP_SHOWWINDOW,
    )


class StartButton(QWidget):
    """Пилюля поверх таскбара — управляется через Win32 напрямую."""

    def __init__(self, main_window):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self._win     = main_window
        self._hover   = False
        self._press   = False
        self._pw      = _pill_width()
        self._closing = False
        self._hwnd    = None

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setFixedSize(self._pw, _H)
        self.setCursor(Qt.PointingHandCursor)

        self._reposition()
        self.show()

        # После show() HWND готов
        self._hwnd = int(self.winId())
        _win32_setup(self._hwnd)

        # Heartbeat: форсируем видимость через Win32. Каждые 100мс было
        # избыточно (лишняя syscall-нагрузка на UI-поток без выигрыша в
        # надёжности) — 250мс всё ещё достаточно часто, чтобы Windows
        # не успела спрятать окно.
        self._guard = QTimer(self)
        self._guard.timeout.connect(self._heartbeat)
        self._guard.start(250)

    # ── Геометрия ─────────────────────────────────────────────────────────────
    def _reposition(self):
        full = QApplication.primaryScreen().geometry()
        self.move(_OFFSET_X, full.height() - _H)

    # ── Heartbeat ─────────────────────────────────────────────────────────────
    def _heartbeat(self):
        if self._closing or not self._hwnd:
            return
        _win32_force_show(self._hwnd, self.x(), self.y(), self._pw, _H)

    # ── Защита на уровне Qt ───────────────────────────────────────────────────
    def setVisible(self, visible: bool):
        if not visible and not self._closing:
            return
        super().setVisible(visible)

    def closeEvent(self, e):
        e.accept() if self._closing else e.ignore()

    def quit(self):
        self._closing = True
        self._guard.stop()

    # ── Отрисовка ─────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        color = _C_PRE if self._press else (_C_HOV if self._hover else _C_BG)
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)

        top = (_H - _PILL_H) // 2
        p.drawRoundedRect(0, top, self._pw, _PILL_H, _PILL_R, _PILL_R)

        p.setPen(_C_TXT)
        p.setFont(_FONT)
        p.drawText(QRect(0, top, self._pw, _PILL_H), Qt.AlignCenter, _LABEL)
        p.end()

    # ── Мышь ─────────────────────────────────────────────────────────────────
    def enterEvent(self, _):
        self._hover = True;  self.update()

    def leaveEvent(self, _):
        self._hover = self._press = False;  self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press = True;  self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press = False;  self.update()
            if self.rect().contains(e.position().toPoint()):
                self._toggle()

    # ── Логика ────────────────────────────────────────────────────────────────
    def _toggle(self):
        if self._win.isVisible():
            self._win.hide()
        else:
            self._win.show()
            self._win.raise_()
            self._win.activateWindow()
