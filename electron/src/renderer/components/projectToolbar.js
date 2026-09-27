"use strict";
/**
 * Верхняя панель экрана проекта — порт ui/project_toolbar.py.
 * Кнопка режима песочницы стоит слева от "Фильтр" (см. фикс бага в
 * Python-версии, тот же порядок сохранён здесь с самого начала).
 */
import { el } from "./dom.js";
import { createModeToggleButton } from "./modeToggleButton.js";

export function createProjectToolbar(handlers) {
  const {
    onBack, onFilterToggled, onDepsToggled, onSandboxToggled,
    onSummary, onReload,
  } = handlers;

  const title = el("span", { className: "hub-title", style: { flex: "0 0 auto" } });
  const count = el("span", { className: "section-label" });

  const btnBack = el("button", { className: "btn-primary", text: "← Назад", onClick: onBack });

  let filterChecked = false;
  const btnFilter = el("button", { className: "btn-primary", text: "Фильтр" });
  btnFilter.addEventListener("click", () => {
    filterChecked = !filterChecked;
    btnFilter.classList.toggle("btn-primary--checked", filterChecked);
    onFilterToggled(filterChecked);
  });

  let depsChecked = false;
  const btnDeps = el("button", { className: "btn-primary", text: "Зависимости" });
  const setDepsChecked = (v) => {
    depsChecked = v;
    btnDeps.classList.toggle("btn-primary--checked", depsChecked);
  };
  btnDeps.addEventListener("click", () => {
    setDepsChecked(!depsChecked);
    onDepsToggled(depsChecked);
  });

  const sandbox = createModeToggleButton((checked) => onSandboxToggled(checked));

  const btnSummary = el("button", { className: "btn-primary", text: "Сводка", onClick: onSummary });
  const btnReload = el("button", { className: "btn-primary", text: "Обновить", onClick: onReload });

  const root = el("div", { className: "project-toolbar" }, [
    btnBack,
    el("div", { className: "project-toolbar__spacer" }),
    title,
    el("div", { className: "project-toolbar__spacer" }),
    sandbox.element,
    btnFilter,
    btnDeps,
    btnSummary,
    btnReload,
    count,
  ]);

  return {
    element: root,
    setTitle: (text) => { title.textContent = text; },
    setCount: (text) => { count.textContent = text; },
    depsChecked: () => depsChecked,
    sandboxChecked: () => sandbox.isChecked(),
    uncheckDeps: () => setDepsChecked(false),
    uncheckSandbox: () => sandbox.setChecked(false),
  };
}
