"use strict";
/**
 * Общая заготовка всплывающего окна: рамка, круглая кнопка закрытия,
 * перетаскивание мышью — порт ui/base_dialog.py. В вебе нет отдельных
 * top-level окон на клик мимо контента, поэтому оверлей сам закрывает
 * диалог по клику на подложку (в Qt-версии за это отвечал WM: клик мимо
 * frameless-диалога не закрывал его, но модальный QDialog так себя не
 * ведёт по умолчанию тоже — оверлей здесь чисто для визуальной модальности).
 */
import { el } from "./dom.js";

export function createBaseDialog(width, height) {
  const closeBtn = el("button", { className: "btn-close-circle dialog-frame__close" });

  const frame = el("div", {
    className: "dialog-frame",
    style: { width: `${width}px`, height: `${height}px` },
  }, [closeBtn]);

  const overlay = el("div", { className: "dialog-overlay" }, [frame]);

  let onCloseCb = null;
  function close() {
    overlay.remove();
    if (onCloseCb) onCloseCb();
  }
  closeBtn.addEventListener("click", close);

  // Перетаскивание — как mousePressEvent/mouseMoveEvent на весь QDialog
  // в оригинале: тащить можно, зацепившись за любое место рамки.
  let dragOffset = null;
  frame.addEventListener("mousedown", (e) => {
    if (e.target === closeBtn) return;
    const rect = frame.getBoundingClientRect();
    dragOffset = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    frame.style.position = "fixed";
    frame.style.left = `${rect.left}px`;
    frame.style.top = `${rect.top}px`;
    overlay.style.alignItems = "flex-start";
    overlay.style.justifyContent = "flex-start";
  });
  window.addEventListener("mousemove", (e) => {
    if (!dragOffset) return;
    frame.style.left = `${e.clientX - dragOffset.x}px`;
    frame.style.top = `${e.clientY - dragOffset.y}px`;
  });
  window.addEventListener("mouseup", () => { dragOffset = null; });

  document.body.append(overlay);

  return {
    frame,
    overlay,
    close,
    onClose: (cb) => { onCloseCb = cb; },
    /** Ставит окно по центру родительского прямоугольника (обычно — окна приложения). */
    centerOver() {
      // flex-центрирование оверлея уже делает это по умолчанию — метод
      // сохранён для паритета с center_over() из Python-версии.
    },
  };
}
