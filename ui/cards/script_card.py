from dataclasses import dataclass, field
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from data.config import COLORS
from data.models import ScriptInfo


@dataclass
class CardStyle:
    card_color:      QColor = field(default_factory=lambda: QColor(195, 198, 205))
    zone_color:      QColor = field(default_factory=lambda: QColor(210, 213, 218))
    zone_text_color: QColor = field(default_factory=lambda: QColor(100, 105, 118))

DEFAULT_STYLE = CardStyle()

# Badge colours — единственный источник: settings.json (data/config.py)
_C_BLUE   = QColor(COLORS["badge_blue"])
_C_RED    = QColor(COLORS["badge_red"])
_C_GREEN  = QColor(COLORS["pill_name"])
_C_DEAD   = QColor(COLORS["badge_dead"])
_C_WHITE  = QColor(COLORS["badge_white"])
_C_BLACK  = QColor(COLORS["black"])

_BADGE_D  = 11      # normal badge diameter
_BADGE_D_DEAD = 14  # D badge — тот же коэффициент, что и раньше (×1.25)
_BADGE_R  = _BADGE_D // 2
_BADGE_R_DEAD = _BADGE_D_DEAD // 2
_BADGE_STEP = _BADGE_D + 2


class ScriptCard(QWidget):
    clicked = Signal(object)

    CARD_W = 45
    CARD_H = int(45 * 1.414)

    def __init__(self, script: ScriptInfo,
                 style: CardStyle = DEFAULT_STYLE,
                 filter_count: int = 0,
                 antipattern_count: int = 0,
                 is_refactor: bool = False,
                 is_dead: bool = False,
                 incoming_count: int = 0,
                 outgoing_count: int = 0,
                 total_deps_count: int = 0):
        super().__init__()
        self.script              = script
        self._style              = style
        self._filter_count       = filter_count
        self._antipattern_count  = antipattern_count
        self._is_refactor        = is_refactor
        self._is_dead            = is_dead
        self._incoming_count     = incoming_count
        self._outgoing_count     = outgoing_count
        self._total_deps_count   = total_deps_count
        self.setFixedSize(self.CARD_W + 14, self.CARD_H + 9)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.script)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._style

        W, H = self.CARD_W, self.CARD_H
        ox = (self.width() - W) // 2
        oy = 7

        # ── card body ────────────────────────────────────────
        p.setPen(Qt.NoPen)
        p.setBrush(s.card_color)
        p.drawRoundedRect(ox, oy, W, H, 5, 5)

        # ── text zone ────────────────────────────────────────
        zw, zh = 28, 14
        zx = ox + (W - zw) // 2
        zy = oy + (H - zh) // 2
        p.setBrush(s.zone_color)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(zx, zy, zw, zh, 3, 3)
        p.setFont(QFont("Segoe UI", 6))
        p.setPen(s.zone_text_color)
        p.drawText(zx, zy, zw, zh, Qt.AlignCenter, "{ }")

        # ── stacked badges (right side) ──────────────────────
        bx = ox + W - 3
        by = oy + 3

        # (заливка, цвет текста, цвет рамки или None, текст)
        stack = []
        if self._total_deps_count > 0:
            stack.append((_C_WHITE, _C_BLACK, _C_BLACK, str(self._total_deps_count)))
        if self._filter_count > 0:
            stack.append((_C_BLUE, _C_WHITE, None, str(self._filter_count)))
        if self._incoming_count > 0:
            stack.append((_C_GREEN, _C_WHITE, None, str(self._incoming_count)))
        if self._outgoing_count > 0:
            stack.append((_C_RED, _C_WHITE, None, str(self._outgoing_count)))
        if self._is_refactor:
            stack.append((_C_RED, _C_WHITE, None, "R"))
        if self._antipattern_count > 0:
            stack.append((_C_RED, _C_WHITE, None, "!"))

        for i, (fill, text_color, border, text) in enumerate(stack):
            cy = by + i * _BADGE_STEP
            p.setPen(QPen(border, 1) if border else Qt.NoPen)
            p.setBrush(fill)
            p.drawEllipse(bx - _BADGE_R, cy - _BADGE_R, _BADGE_D, _BADGE_D)
            p.setPen(text_color)
            p.setFont(QFont("Segoe UI", 5, QFont.Bold))
            p.drawText(bx - _BADGE_R, cy - _BADGE_R, _BADGE_D, _BADGE_D,
                       Qt.AlignCenter, text)

        # ── D badge in centre (dead script) ──────────────────
        if self._is_dead:
            dx = ox + W // 2
            dy = oy + H // 2
            p.setPen(Qt.NoPen)
            p.setBrush(_C_DEAD)
            p.drawEllipse(dx - _BADGE_R_DEAD, dy - _BADGE_R_DEAD,
                          _BADGE_D_DEAD, _BADGE_D_DEAD)
            p.setPen(_C_WHITE)
            p.setFont(QFont("Segoe UI", 6, QFont.Bold))
            p.drawText(dx - _BADGE_R_DEAD, dy - _BADGE_R_DEAD,
                       _BADGE_D_DEAD, _BADGE_D_DEAD, Qt.AlignCenter, "D")
