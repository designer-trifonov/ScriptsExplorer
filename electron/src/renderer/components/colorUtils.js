"use strict";
/** Мелкая цветовая арифметика для фонов песочниц — держим отдельно от layout-кода. */

function hexToRgb(hex) {
  const n = parseInt(hex.replace("#", ""), 16);
  return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}

function rgbToHex(r, g, b) {
  const c = (v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0");
  return `#${c(r)}${c(g)}${c(b)}`;
}

/**
 * Затемняет цвет к чёрному в заданной пропорции — всегда возвращает
 * сплошной (не прозрачный) hex. factor=1 → исходный цвет, factor=0 → чёрный.
 */
export function darken(hex, factor) {
  const { r, g, b } = hexToRgb(hex);
  return rgbToHex(r * factor, g * factor, b * factor);
}

/**
 * Осветляет цвет к белому — используется для фона песочниц: подписи под
 * карточками (marquee_label) рисуются тёмным текстом в расчёте на светлый
 * фон, тёмная заливка делала бы их нечитаемыми. amount=0 → исходный цвет,
 * amount=1 → белый.
 */
export function lighten(hex, amount) {
  const { r, g, b } = hexToRgb(hex);
  const mix = (c) => c + (255 - c) * amount;
  return rgbToHex(mix(r), mix(g), mix(b));
}
