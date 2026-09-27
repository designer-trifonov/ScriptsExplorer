"use strict";
/**
 * Окошко выбора цвета рамки/фона песочницы — порт ui/sandbox_color_picker.py.
 * QColorDialog -> нативный браузерный <input type="color">.
 */
export function pickColor(initial = "#1EA8E6") {
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "color";
    input.value = initial;
    input.style.position = "fixed";
    input.style.opacity = "0";
    input.style.pointerEvents = "none";
    document.body.append(input);

    let picked = false;
    input.addEventListener("input", () => { picked = true; });
    input.addEventListener("change", () => {
      resolve(picked ? input.value : null);
      input.remove();
    });
    // Если пользователь закрыл диалог без выбора — change не придёт;
    // блюр после короткой паузы страхует от зависшего <input> в DOM.
    input.addEventListener("blur", () => {
      setTimeout(() => {
        if (input.isConnected) { resolve(picked ? input.value : null); input.remove(); }
      }, 300);
    });

    input.click();
  });
}
