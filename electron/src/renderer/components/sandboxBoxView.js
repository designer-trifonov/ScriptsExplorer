"use strict";
/**
 * Визуал одной песочницы: рамка, фон, название сверху слева — порт
 * ui/sandbox_box_view.py. Без перетаскивания и без подъёма слоя — это
 * отдельные поведения (draggableBehavior.js, bringToFront.js), которые
 * цепляет к этому виджету тот, кто его создаёт (sandboxController.js).
 */
import { el } from "./dom.js";

// Заголовок больше не резервирует отдельную полосу высоты — он рисуется
// НАД тем же самым margin-отступом, что и остальные три стороны (иначе
// сверху получался бы отступ в 2 раза больше боковых — заголовок+margin
// против одного margin). Текст помещается внутри SANDBOX_MARGIN=16px
// (см. CSS .sandbox-box__title: top 2px + ~11px строка = 13px < 16px).

export function createSandboxBoxView(nodeId, name, borderColor, backgroundColor, scale = 1) {
  const title = el("span", { className: "sandbox-box__title", text: name });
  // Заголовок делит масштаб с содержимым этой песочницы (см. sandboxScale.js)
  // — та же единственная формула, а не отдельное число для "текста
  // заголовка": иначе на глубокой вложенности из-за уменьшенного
  // SANDBOX_MARGIN заголовок начал бы наезжать на первый ряд содержимого.
  if (scale !== 1) title.style.fontSize = `${8 * scale}px`;
  const content = el("div", { className: "sandbox-box__content" });

  const box = el("div", { className: "sandbox-box" }, [title, content]);
  box.dataset.nodeId = nodeId;

  function applyColors(border, bg) {
    title.style.color = border;
    box.style.borderColor = border;
    box.style.background = bg || "transparent";
  }
  applyColors(borderColor, backgroundColor);

  // width/height как обычные JS-поля, а не offsetWidth/offsetHeight —
  // весь холст строится ОТКЛЮЧЁННЫМ от document (canvas.setRoot() вставляет
  // готовое дерево целиком только в конце rebuild()), а offsetWidth/
  // offsetHeight для отсоединённых от document элементов всегда 0. Именно
  // это давало неправильный (нулевой -> дефолтный 160x70) размер вложенной
  // песочницы при расчёте отступа для родительской раскладки — отсюда была
  // накладка скриптов на песочницу и "просвечивание".
  const boxApi = {
    element: box,
    content,
    nodeId,
    width: 0,
    height: 0,
    setSize(width, height) {
      box.style.width = `${width}px`;
      box.style.height = `${height}px`;
      content.style.width = `${width}px`;
      content.style.height = `${height}px`;
      boxApi.width = width;
      boxApi.height = height;
    },
    /** Заполняет весь доступный контейнер — вместо фиксированного px-размера. */
    fill() {
      box.style.width = "100%";
      box.style.height = "100%";
      content.style.width = "100%";
      content.style.height = "100%";
    },
    setName(newName) {
      title.textContent = newName;
    },
    setColors(border, bg) {
      applyColors(border, bg);
    },
  };
  return boxApi;
}
