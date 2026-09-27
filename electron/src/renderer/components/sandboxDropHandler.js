"use strict";
/**
 * При отпускании мыши решает, куда попал перетаскиваемый элемент, и
 * просит пересчитать позиции — порт ui/sandbox_drop_handler.py.
 */
import { findTarget } from "./dropTargetFinder.js";

/** Возвращает найденную песочницу-цель (обёртку {element,...}) или null. */
export function handleDrop(draggedBox, clientX, clientY, candidateBoxes) {
  const others = candidateBoxes.filter((b) => b !== draggedBox);
  return findTarget(clientX, clientY, others);
}
