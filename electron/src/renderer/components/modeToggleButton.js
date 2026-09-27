"use strict";
/**
 * Кнопка-иконка переключения между режимом сетки и режимом песочницы —
 * порт ui/mode_toggle_button.py. В отличие от Qt, эмодзи в браузере не
 * нужно чинить отдельным font-family — системный emoji-фолбэк уже есть.
 */
import { el } from "./dom.js";

export function createModeToggleButton(onChange) {
  let active = false;
  const btn = el("button", {
    className: "btn-primary mode-toggle-btn",
    text: "🧩",
    attrs: { title: "Режим песочницы" },
  });

  function apply() {
    btn.classList.toggle("btn-primary--checked", active);
  }

  btn.addEventListener("click", () => {
    active = !active;
    apply();
    onChange && onChange(active);
  });

  return {
    element: btn,
    setChecked(value) {
      active = value;
      apply();
    },
    isChecked: () => active,
  };
}
