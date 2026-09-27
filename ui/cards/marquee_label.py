from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor

_START_DELAY_MS = 3750   # на 25% дольше прежних 3000мс — дольше стоит перед прокруткой


class MarqueeLabel(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text   = text
        self._offset = 0.0

        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(16)
        self._scroll_timer.timeout.connect(self._tick)

        self._delay_timer = QTimer(self)
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._start_scroll)

        self._end_timer = QTimer(self)
        self._end_timer.setSingleShot(True)
        self._end_timer.setInterval(2000)
        self._end_timer.timeout.connect(self._after_end)

        self.setFixedHeight(16)

    def setText(self, text):
        self._text   = text
        self._offset = 0.0
        self.update()
        self._check()

    def showEvent(self, e):
        super().showEvent(e)
        self._check()

    def hideEvent(self, e):
        super().hideEvent(e)
        self._scroll_timer.stop()
        self._delay_timer.stop()
        self._end_timer.stop()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._check()

    def _needs_scroll(self) -> bool:
        return self.fontMetrics().horizontalAdvance(self._text) > self.width()

    def _check(self):
        if self._needs_scroll():
            if not self._scroll_timer.isActive() and \
               not self._delay_timer.isActive() and \
               not self._end_timer.isActive():
                self._offset = 0.0
                self._delay_timer.setInterval(_START_DELAY_MS)
                self._delay_timer.start()
        else:
            self._scroll_timer.stop()
            self._delay_timer.stop()
            self._end_timer.stop()
            self._offset = 0.0
            self.update()

    def _start_scroll(self):
        if self._needs_scroll():
            self._scroll_timer.start()

    def _after_end(self):
        self._offset = 0.0
        self.update()
        if self._needs_scroll():
            self._delay_timer.setInterval(_START_DELAY_MS)
            self._delay_timer.start()

    def _tick(self):
        fm         = self.fontMetrics()
        tw         = fm.horizontalAdvance(self._text)
        max_offset = max(0.0, tw - self.width() + 6)
        self._offset += 0.5
        if self._offset >= max_offset:
            self._scroll_timer.stop()
            self._end_timer.start()
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.transparent)
        p.setFont(self.font())
        p.setPen(QColor(80, 82, 90))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(self._text)
        if tw <= self.width():
            p.drawText(self.rect(), Qt.AlignCenter | Qt.AlignVCenter, self._text)
        else:
            p.setClipRect(self.rect())
            p.drawText(int(-self._offset), 0,
                       tw + 40, self.height(),
                       Qt.AlignLeft | Qt.AlignVCenter, self._text)
