"use strict";
/**
 * Grid-раскладка карточек — порт ui/script_grid.py.
 *
 * Python-версия вручную считала число колонок по ширине окна и
 * пересобирала QGridLayout на resize (через таймер-дебаунс). CSS
 * flex-wrap (components.css: .script-grid) делает то же самое сам,
 * без слушателя resize и без пересборки DOM при изменении размеров окна.
 */
import { el } from "./dom.js";
import { createScriptCellView, badgeFlags } from "./scriptCellView.js";

export function createScriptGrid(onScriptClicked) {
  const root = el("div", { className: "script-grid" });
  let scripts = [];
  let filters = new Set();

  function badgeFlagsFor(script) {
    return badgeFlags({
      lifecycleCount: filters.has("lifecycle") ? script.lifecycleCount : 0,
      incomingCount: filters.has("incoming") ? script.incoming.length : 0,
      outgoingCount: filters.has("outgoing") ? script.allDeps.length : 0,
      totalDepsCount: filters.has("dependencies") ? script.totalDeps : 0,
      showRefactor: filters.has("refactor"),
      showAntipatterns: filters.has("antipatterns"),
      showDead: filters.has("dead"),
    });
  }

  function rebuild() {
    root.replaceChildren();
    for (const script of scripts) {
      root.append(createScriptCellView(script, badgeFlagsFor(script), onScriptClicked));
    }
  }

  return {
    element: root,
    setScripts(newScripts) {
      scripts = newScripts;
      rebuild();
    },
    setFilters(newFilters) {
      filters = newFilters;
      if (scripts.length) rebuild();
    },
  };
}
