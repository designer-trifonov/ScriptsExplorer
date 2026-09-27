"use strict";
/**
 * Панель фильтров — порт ui/filter_bar.py. Скрыта по умолчанию (как
 * self.hide() в оригинале), показывается по кнопке "Фильтр" тулбара.
 */
import { el } from "./dom.js";

const FILTERS = [
  ["lifecycle", "OnEnable / Awake / Start"],
  ["refactor", "Рефакторинг"],
  ["dead", "Мёртвые"],
  ["antipatterns", "Антипаттерны"],
  ["incoming", "Входящие связи"],
  ["outgoing", "Исходящие связи"],
  ["dependencies", "Общее количество зависимостей"],
];

export function createFilterBar({ onScriptsOnlyChanged, onMethodFiltersChanged }) {
  const checks = {};

  const chkScripts = el("input", { attrs: { type: "checkbox" } });
  chkScripts.checked = true;
  chkScripts.addEventListener("change", () => onScriptsOnlyChanged(chkScripts.checked));

  const activeFilters = () => new Set(Object.entries(checks).filter(([, c]) => c.checked).map(([k]) => k));

  const filterLabels = FILTERS.map(([key, label]) => {
    const chk = el("input", { attrs: { type: "checkbox" } });
    chk.addEventListener("change", () => onMethodFiltersChanged(activeFilters()));
    checks[key] = chk;
    return el("label", {}, [chk, document.createTextNode(label)]);
  });

  const root = el("div", { className: "filter-bar", style: { display: "none" } }, [
    el("label", {}, [chkScripts, document.createTextNode("Только Scripts")]),
    el("div", { className: "separator--v" }),
    ...filterLabels,
  ]);

  return {
    element: root,
    scriptsOnly: () => chkScripts.checked,
    activeFilters,
    setVisible: (v) => { root.style.display = v ? "flex" : "none"; },
  };
}
