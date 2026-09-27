"use strict";
/**
 * Бегущая строка с именем скрипта — порт ui/cards/marquee_label.py.
 * Оригинал вручную гонял таймеры (задержка -> скролл -> пауза -> заново);
 * здесь та же последовательность отдана CSS-анимации (marquee-scroll в
 * components.css) — Chromium-композитор справляется с этим сам, без
 * requestAnimationFrame на каждый тик.
 */
import { el } from "./dom.js";

export function createMarqueeLabel(text, width) {
  const inner = el("span", { className: "marquee__inner", text });
  const wrap = el("div", { className: "marquee", style: { width: `${width}px` } }, [inner]);

  // После вставки в DOM меряем реальную ширину текста — если не влезает,
  // включаем скролл (аналог _needs_scroll()).
  requestAnimationFrame(() => {
    const overflow = inner.scrollWidth - wrap.clientWidth;
    if (overflow > 0) {
      wrap.classList.add("marquee--scroll");
      wrap.style.setProperty("--marquee-distance", `-${overflow + 6}px`);
      inner.style.animationDuration = `${Math.max(3, overflow / 20)}s`;
    } else {
      inner.style.textAlign = "center";
      inner.style.width = "100%";
    }
  });

  return wrap;
}
