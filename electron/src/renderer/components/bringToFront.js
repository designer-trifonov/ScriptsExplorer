"use strict";
/**
 * Поднимает элемент визуально выше остальных детей того же родителя при
 * клике — порт ui/bring_to_front.py. Среди абсолютно позиционированных
 * siblings последний в DOM рисуется поверх — тот же эффект, что и raise_().
 */
export function bringToFrontOnClick(el) {
  const handler = () => {
    if (el.parentElement && el.parentElement.lastElementChild !== el) {
      el.parentElement.append(el);
    }
  };
  el.addEventListener("mousedown", handler);
  return { destroy: () => el.removeEventListener("mousedown", handler) };
}
