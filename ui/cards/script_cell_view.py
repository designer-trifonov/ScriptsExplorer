from dataclasses import dataclass
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from data.models import ScriptInfo
from ui.cards.script_card import ScriptCard
from ui.cards.marquee_label import MarqueeLabel


@dataclass(frozen=True)
class BadgeFlags:
    """Какие бейджи показывать на карточке прямо сейчас.

    Это решение экрана (какие фильтры включены), а не свойство самого
    скрипта — поэтому оно не хранится в ScriptInfo, а приходит снаружи
    и пересчитывается при каждом переключении фильтра.
    """
    lifecycle_count:   int  = 0
    incoming_count:    int  = 0
    outgoing_count:    int  = 0
    total_deps_count:  int  = 0
    show_refactor:     bool = False
    show_antipatterns: bool = False
    show_dead:         bool = False


class ScriptCellView(QWidget):
    """Только отображение: карточка + бегущая строка с именем.

    Что скрипт из себя представляет (нужен ли рефакторинг, есть ли
    антипаттерны) решает data-слой (ScriptInfo). Что из этого показать
    бейджем прямо сейчас — решают активные фильтры (BadgeFlags).
    """
    clicked = Signal(object)

    W = ScriptCard.CARD_W + 14

    def __init__(self, script: ScriptInfo, badges: BadgeFlags = None):
        super().__init__()
        badges = badges or BadgeFlags()
        self.setFixedWidth(self.W)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        card = ScriptCard(
            script,
            filter_count=badges.lifecycle_count,
            incoming_count=badges.incoming_count,
            outgoing_count=badges.outgoing_count,
            total_deps_count=badges.total_deps_count,
            antipattern_count=script.total_antipatterns if badges.show_antipatterns else 0,
            is_refactor=script.is_refactor and badges.show_refactor,
            is_dead=script.is_dead and badges.show_dead,
        )
        card.clicked.connect(self.clicked)
        lay.addWidget(card, alignment=Qt.AlignHCenter)

        lbl = MarqueeLabel(script.class_name)
        name_font = QFont("Segoe UI")
        name_font.setPointSizeF(1.28)   # ещё на 20% меньше прежних 1.6pt
        lbl.setFont(name_font)
        lbl.setFixedWidth(self.W)
        lay.addWidget(lbl)
