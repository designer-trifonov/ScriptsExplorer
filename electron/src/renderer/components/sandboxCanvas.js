"use strict";
/**
 * Холст режима песочницы — показывает дерево песочниц. Сам ничего не
 * сохраняет и не загружает (это sandboxController.js), только строит то,
 * что ему передали. Порт ui/sandbox_canvas.py.
 */
import { el } from "./dom.js";

export function createSandboxCanvas() {
  const root = el("div", { className: "sandbox-canvas" });
  let rootBox = null;

  return {
    element: root,
    setRoot(box) {
      root.replaceChildren();
      rootBox = box;
      root.append(box.element);
    },
    root: () => rootBox,
  };
}
