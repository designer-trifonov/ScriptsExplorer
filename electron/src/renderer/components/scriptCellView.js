"use strict";
/**
 * Карточка + бегущая строка с именем — порт ui/cards/script_cell_view.py.
 */
import { el } from "./dom.js";
import { createScriptCard, CARD_W, CARD_H } from "./scriptCard.js";
import { createMarqueeLabel } from "./marqueeLabel.js";

const MARQUEE_H = 16;

export const CELL_W = CARD_W + 14;
// Общая высота ячейки (карточка + бегущая строка с именем) — единственное
// место, которое это знает; кому нужен размер ячейки для раскладки
// (например sandboxController.js), берёт готовую константу, а не
// пересчитывает/дублирует геометрию карточки у себя.
export const CELL_H = CARD_H + 9 + MARQUEE_H;

/** Какие бейджи показывать на карточке прямо сейчас — порт BadgeFlags. */
export function badgeFlags(overrides = {}) {
  return {
    lifecycleCount: 0,
    incomingCount: 0,
    outgoingCount: 0,
    totalDepsCount: 0,
    showRefactor: false,
    showAntipatterns: false,
    showDead: false,
    ...overrides,
  };
}

export function createScriptCellView(script, flags, onClick) {
  const card = createScriptCard(script, {
    filterCount: flags.lifecycleCount,
    incomingCount: flags.incomingCount,
    outgoingCount: flags.outgoingCount,
    totalDepsCount: flags.totalDepsCount,
    antipatternCount: flags.showAntipatterns ? script.totalAntipatterns : 0,
    isRefactor: script.isRefactor && flags.showRefactor,
    isDead: script.isDead && flags.showDead,
  });

  const label = createMarqueeLabel(script.className, CELL_W);

  const cell = el("div", { className: "script-cell", style: { width: `${CELL_W}px` } }, [card, label]);
  cell.addEventListener("click", () => onClick && onClick(script));
  return cell;
}
