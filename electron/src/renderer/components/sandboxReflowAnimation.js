"use strict";
/**
 * Анимирует переезд элемента на новую позицию вместо мгновенного прыжка —
 * порт ui/sandbox_reflow_animation.py (QPropertyAnimation -> Web Animations API).
 */
const DURATION_MS = 200;

export function animateMove(el, newX, newY, durationMs = DURATION_MS) {
  const startX = parseFloat(el.style.left) || 0;
  const startY = parseFloat(el.style.top) || 0;

  el.animate(
    [
      { left: `${startX}px`, top: `${startY}px` },
      { left: `${newX}px`, top: `${newY}px` },
    ],
    { duration: durationMs, easing: "cubic-bezier(0.215, 0.61, 0.355, 1)" } // ~QEasingCurve.OutCubic
  );
  // Web Animations не меняет сами стили по умолчанию (fill:none) — как и
  // Python-версия, где по завершении anim целевое значение уже стоит в pos().
  el.style.left = `${newX}px`;
  el.style.top = `${newY}px`;
}
