"use strict";
/**
 * Единственная задача: не дать функции вызываться чаще, чем раз в delayMs —
 * общая утилита, не специфичная ни для resize, ни для песочницы, ни для
 * чего-либо ещё конкретного.
 */
export function debounce(fn, delayMs) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delayMs);
  };
}
