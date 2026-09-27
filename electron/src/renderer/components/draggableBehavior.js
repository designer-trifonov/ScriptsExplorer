"use strict";
/**
 * Делает любой абсолютно позиционированный элемент перетаскиваемым мышью —
 * порт ui/draggable_behavior.py. stopPropagation на mousedown — аналог
 * того, что в Qt каждый installEventFilter вешается на конкретный виджет:
 * перетаскивание карточки не должно так же двигать её родительскую
 * песочницу.
 */
export function makeDraggable(el, onDragFinished) {
  let dragging = false;
  let startX = 0, startY = 0, origLeft = 0, origTop = 0;

  function onDown(e) {
    if (e.button !== 0) return;
    dragging = true;
    startX = e.clientX;
    startY = e.clientY;
    origLeft = parseFloat(el.style.left) || 0;
    origTop = parseFloat(el.style.top) || 0;
    e.stopPropagation();
  }

  function onMove(e) {
    if (!dragging) return;
    el.style.left = `${origLeft + (e.clientX - startX)}px`;
    el.style.top = `${origTop + (e.clientY - startY)}px`;
  }

  function onUp(e) {
    if (!dragging) return;
    dragging = false;
    onDragFinished && onDragFinished(e.clientX, e.clientY);
  }

  el.addEventListener("mousedown", onDown);
  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);

  return {
    destroy() {
      el.removeEventListener("mousedown", onDown);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    },
  };
}
