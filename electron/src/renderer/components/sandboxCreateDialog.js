"use strict";
/**
 * Диалог создания песочницы: имя + цвет. Единственный способ, которым в
 * приложении появляется новая песочница — по кнопке "Создать песочницу",
 * никакого автосоздания (двойной клик, дефолтные цвета по кругу — вырезано).
 */
import { el } from "./dom.js";
import { createBaseDialog } from "./baseDialog.js";

const W = 280, H = 180;
const DEFAULT_COLOR = "#1EA8E6";

export function openSandboxCreateDialog(onCreate) {
  const dialog = createBaseDialog(W, H);

  const nameInput = el("input", {
    attrs: { type: "text", placeholder: "Название песочницы" },
    style: { width: "100%", height: "26px", boxSizing: "border-box", marginBottom: "10px" },
  });
  const colorInput = el("input", { attrs: { type: "color", value: DEFAULT_COLOR } });

  const createBtn = el("button", { className: "btn-primary", text: "Создать" });
  const cancelBtn = el("button", { className: "btn-primary", text: "Отмена", style: { background: "var(--muted)" } });

  createBtn.addEventListener("click", () => {
    const name = nameInput.value.trim();
    if (!name) { nameInput.focus(); return; }
    onCreate(name, colorInput.value);
    dialog.close();
  });
  cancelBtn.addEventListener("click", () => dialog.close());
  nameInput.addEventListener("keydown", (e) => { if (e.key === "Enter") createBtn.click(); });

  dialog.frame.append(
    el("div", { style: { padding: "24px 16px 16px" } }, [
      el("div", { className: "section-label", text: "Новая песочница", style: { marginBottom: "10px" } }),
      nameInput,
      el("div", { style: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" } }, [
        el("span", { className: "section-label", text: "Цвет" }),
        colorInput,
      ]),
      el("div", { style: { display: "flex", gap: "8px" } }, [createBtn, cancelBtn]),
    ])
  );

  nameInput.focus();
  return dialog;
}
