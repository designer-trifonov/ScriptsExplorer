"""Оформление приложения. Единственное место, которое собирает QSS —
цвета берутся из data/config.py (settings.json), а не хранятся здесь заново."""
from string import Template
from data.config import COLORS

_TEMPLATE = Template("""
QMainWindow, QWidget {
    background-color: $bg;
    font-family: "Segoe UI";
    font-size: 13px;
    color: $text;
}

/* Заголовок хаба */
QLabel#hub_title {
    font-size: 16.5px;
    font-weight: 400;
    color: $accent;
}

QLabel#section_label {
    color: $muted;
    font-size: 10px;
}

QLabel#empty_label {
    color: $faint;
    font-size: 12px;
}

QLabel#card_label {
    color: $link;
    font-size: 11px;
}

/* Разделитель */
QFrame#separator {
    border: none;
    border-top: 1px solid $border;
    max-height: 1px;
}

/* Основная кнопка */
QPushButton#btn_primary {
    background-color: $accent;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0 14px;
    font-size: 10px;
}
QPushButton#btn_primary:hover  { background-color: $accent_hover; }
QPushButton#btn_primary:pressed { background-color: $accent_pressed; }

/* Кнопка проекта */
QPushButton#btn_project {
    background-color: $accent;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0 14px;
    text-align: left;
    font-size: 12px;
}
QPushButton#btn_project:hover  { background-color: $accent_hover; }
QPushButton#btn_project:pressed { background-color: $accent_pressed; }

/* Кнопка удалить */
QPushButton#btn_remove {
    background-color: $danger;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 11px;
}
QPushButton#btn_remove:hover  { background-color: $danger_hover; }
QPushButton#btn_remove:pressed { background-color: $danger_pressed; }

/* ── Диалог детали скрипта ── */
QFrame#detail_frame {
    background-color: $surface;
    border: 1px solid $border_strong;
    border-radius: 12px;
}

QWidget#method_container, QScrollArea#method_scroll {
    background-color: $surface;
    border: none;
}

/* Пилюли — одинаковая высота, шрифт, скругление */
QLabel#pill_name, QLabel#pill_method, QLabel#pill_incoming {
    border-radius: 8px;
    padding: 0 10px;
    font-size: 9px;
    font-family: "Segoe UI";
    color: $pill_text;
}

QLabel#pill_name     { background-color: $pill_name; }
QLabel#pill_method   { background-color: $pill_method; }
QLabel#pill_incoming { background-color: $pill_incoming; }

/* Слот скрипта в ленте зависимостей */
QFrame#dep_slot {
    background-color: $surface;
    border: 1px solid $border_soft;
    border-radius: 10px;
}

/* Кружок зависимостей */
QLabel#dep_dot {
    background-color: $dep_dot;
    border-radius: 8px;
    min-width: 17px;  max-width: 17px;
    min-height: 17px; max-height: 17px;
    color: $black;
    font-size: 9px;
    font-weight: bold;
}

/* Кнопка закрыть */
QPushButton#btn_close_circle {
    background-color: $close;
    border: none;
    border-radius: 7px;
}
QPushButton#btn_close_circle:hover   { background-color: $close_hover; }
QPushButton#btn_close_circle:pressed { background-color: $close_pressed; }

QScrollBar:vertical {
    background: $scrollbar_bg;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: $scrollbar_handle;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
""")

STYLESHEET = _TEMPLATE.substitute(**COLORS)
