"use strict";
/**
 * Тонкая обёртка: делает уже существующую карточку скрипта перетаскиваемой —
 * саму карточку, клики и бейджи не трогаем и не копируем. Порт
 * ui/draggable_script_card.py.
 */
import { makeDraggable } from "./draggableBehavior.js";

export function makeCardDraggable(cell, onDragFinished) {
  return makeDraggable(cell, onDragFinished);
}
