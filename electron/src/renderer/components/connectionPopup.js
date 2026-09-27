"use strict";
/**
 * Свой всплывающий блок со списком связей по наведению — порт
 * ui/connection_popup.py. В вебе системный tooltip timing тоже не нужен —
 * это просто div, показанный/убранный по mouseenter/mouseleave.
 */
import { el } from "./dom.js";

export function createConnectionDot(count, cssColorVar, names, incoming) {
  const dot = el("span", {
    className: "detail-dot",
    text: String(count),
    style: { background: cssColorVar },
  });

  let popup = null;
  const arrowChar = incoming ? "↓" : "↑";
  const arrowColorVar = incoming ? "var(--pill-name)" : "var(--badge-red)";

  dot.addEventListener("mouseenter", () => {
    if (!names.length) return;
    const rows = names.map((name) => el("div", { className: "connection-popup__row" }, [
      el("span", { text: name }),
      el("span", { className: "connection-popup__arrow", text: arrowChar, style: { color: arrowColorVar } }),
    ]));
    popup = el("div", { className: "connection-popup" }, rows);
    const rect = dot.getBoundingClientRect();
    popup.style.left = `${rect.left}px`;
    popup.style.top = `${rect.bottom}px`;
    document.body.append(popup);
  });

  dot.addEventListener("mouseleave", () => {
    if (popup) { popup.remove(); popup = null; }
  });

  return dot;
}
