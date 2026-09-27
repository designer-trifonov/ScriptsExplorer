"use strict";
/**
 * Единственная задача: посчитать фон песочницы по её цвету рамки. У любой
 * песочницы — включая корень — обязан быть сплошной непрозрачный фон
 * (иначе просвет за холстом). Светлый, а не тёмный: подписи под
 * карточками рисуются тёмным текстом в расчёте на светлый фон.
 */
import { lighten } from "./colorUtils.js";

export const ROOT_BACKGROUND = "#F0F0F3"; // как основной фон приложения

const LIGHTEN_AMOUNT = 0.82;

export function backgroundFor(borderColor, isRoot) {
  return isRoot ? ROOT_BACKGROUND : lighten(borderColor, LIGHTEN_AMOUNT);
}

/** Если фон узла не задан явно — досчитывает и запоминает его в самом узле. */
export function ensureBackground(node, isRoot) {
  if (!node.backgroundColor) {
    node.backgroundColor = backgroundFor(node.borderColor, isRoot);
  }
  return node.backgroundColor;
}
