"use strict";
/**
 * Единственная реализация "пилюли" — порт ui/cards/pill.py.
 * cssClass — один из .pill-name/.pill-method/.pill-incoming (theme.css).
 */
import { el } from "./dom.js";

export function createPill(text, cssClass) {
  return el("span", { className: `pill ${cssClass}`, text });
}

export function createClickablePill(text, cssClass, onClick) {
  const pill = createPill(text, cssClass);
  pill.classList.add("pill--clickable");
  pill.addEventListener("click", onClick);
  return pill;
}
