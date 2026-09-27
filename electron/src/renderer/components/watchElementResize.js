"use strict";
/**
 * Единственная задача: сообщить, что элемент изменил размер (окно
 * свернули/развернули/потянули за край) — с антидребезгом, чтобы не
 * пересчитывать раскладку на каждый промежуточный пиксель во время
 * протяжки. Ничего не знает ни про песочницы, ни про раскладку внутри
 * них — тот, кто подписывается, сам решает, что делать при изменении.
 */
import { debounce } from "./debounce.js";

const DEFAULT_DELAY_MS = 120;

export function watchElementResize(element, onResize, delayMs = DEFAULT_DELAY_MS) {
  const debounced = debounce(onResize, delayMs);
  const observer = new ResizeObserver(debounced);
  observer.observe(element);
  return { stop: () => observer.disconnect() };
}
