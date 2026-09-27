"use strict";
/**
 * Визуал карточки скрипта — порт ui/cards/script_card.py.
 * QPainter-отрисовка заменена DOM+CSS (components.css), геометрия и
 * порядок бейджей — те же, что в оригинале.
 */
import { el } from "./dom.js";

export const CARD_W = 45;
export const CARD_H = Math.trunc(45 * 1.414); // как int(45 * 1.414) в Python

export function createScriptCard(script, opts = {}) {
  const {
    filterCount = 0,
    antipatternCount = 0,
    isRefactor = false,
    isDead = false,
    incomingCount = 0,
    outgoingCount = 0,
    totalDepsCount = 0,
  } = opts;

  const body = el("div", {
    className: "script-card__body",
    style: { width: `${CARD_W}px`, height: `${CARD_H}px` },
  }, [
    el("span", { className: "script-card__zone", text: "{ }" }),
  ]);

  // Порядок стека — как в script_card.py: dep-count, filter, incoming,
  // outgoing, refactor, antipatterns.
  const stack = [];
  if (totalDepsCount > 0) stack.push([totalDepsCount, "var(--badge-white)", "black", "1px solid black"]);
  if (filterCount > 0) stack.push([filterCount, "var(--badge-blue)", "white", "none"]);
  if (incomingCount > 0) stack.push([incomingCount, "var(--pill-name)", "white", "none"]);
  if (outgoingCount > 0) stack.push([outgoingCount, "var(--badge-red)", "white", "none"]);
  if (isRefactor) stack.push(["R", "var(--badge-red)", "white", "none"]);
  if (antipatternCount > 0) stack.push(["!", "var(--badge-red)", "white", "none"]);

  if (stack.length > 0) {
    const badges = el("div", { className: "script-card__badges" });
    for (const [text, bg, color, border] of stack) {
      badges.append(el("span", {
        className: "script-card__badge",
        text: String(text),
        style: { background: bg, color, border },
      }));
    }
    body.append(badges);
  }

  if (isDead) {
    body.append(el("span", { className: "script-card__dead", text: "D" }));
  }

  return el("div", {
    className: "script-card",
    style: { width: `${CARD_W + 14}px`, height: `${CARD_H + 9}px` },
  }, [body]);
}
