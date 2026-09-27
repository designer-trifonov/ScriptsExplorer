"use strict";
/**
 * Контейнер экрана проекта — порт ui/project_view.py.
 */
import { el } from "./dom.js";
import { createProjectToolbar } from "./projectToolbar.js";
import { createFilterBar } from "./filterBar.js";
import { createScriptGrid } from "./scriptGrid.js";
import { createDependencyLane } from "./dependencyLane.js";
import { openSummaryDialog } from "./summaryDialog.js";
import { openScriptDetailDialog } from "./scriptDetail.js";
import { createSandboxController } from "./sandboxController.js";
import { openSandboxCreateDialog } from "./sandboxCreateDialog.js";

export function createProjectView({ onBack }) {
  let project = null;
  let scripts = [];
  let detailDialog = null;
  let sandboxActivatedFor = null;

  const openDetail = (script) => {
    if (detailDialog) detailDialog.close();
    detailDialog = openScriptDetailDialog(script, filterBar.activeFilters());
    detailDialog.onClose(() => { detailDialog = null; });
  };

  const grid = createScriptGrid(openDetail);
  const lane = createDependencyLane(openDetail);
  const sandbox = createSandboxController();

  const filterBar = createFilterBar({
    onScriptsOnlyChanged: () => reload(),
    onMethodFiltersChanged: (filters) => grid.setFilters(filters),
  });

  const gridScroll = el("div", { style: { flex: "1", overflow: "hidden" } }, [grid.element]);
  const laneScroll = el("div", { style: { flex: "1", overflow: "hidden", display: "none" } }, [lane.element]);

  const btnCreateSandbox = el("button", {
    className: "btn-primary",
    text: "+ Создать песочницу",
    // Без левого/правого margin — левый край должен совпадать с "Назад" и
    // с песочницей ниже: единственный источник отступа слева/справа —
    // padding самого .screen, а не свой собственный margin поверх него.
    style: { alignSelf: "flex-start", margin: "0 0 8px 0", flexShrink: "0" },
    onClick: () => openSandboxCreateDialog((name, color) => sandbox.addSandbox(name, color)),
  });
  const sandboxCanvasEl = sandbox.canvas();
  sandboxCanvasEl.style.flex = "1";
  sandboxCanvasEl.style.minHeight = "0"; // иначе flex-элемент не сжимается меньше контента
  const sandboxScroll = el("div", {
    style: { flex: "1", overflow: "auto", display: "none", flexDirection: "column" },
  }, [btnCreateSandbox, sandboxCanvasEl]);

  function reload() {
    if (!project) return;
    window.scriptExplorer.scanProject(project.path, filterBar.scriptsOnly()).then((result) => {
      scripts = result;
      toolbar.setCount(`  ${scripts.length} файлов`);
      grid.setScripts(scripts);
      if (toolbar.depsChecked()) lane.setScripts(scripts);
    });
  }

  function activateSandbox() {
    if (!project) return;
    // сессия для этого проекта уже подгружена в этом запуске
    if (sandboxActivatedFor === project.path) return;
    sandbox.activate(project.path, scripts);
    sandboxActivatedFor = project.path;
  }

  const toolbar = createProjectToolbar({
    onBack,
    onFilterToggled: (checked) => filterBar.setVisible(checked),
    onDepsToggled: (checked) => {
      if (checked) {
        toolbar.uncheckSandbox();
        lane.setScripts(scripts);
      }
      laneScroll.style.display = checked ? "block" : "none";
      sandboxScroll.style.display = "none";
      gridScroll.style.display = checked ? "none" : "block";
    },
    onSandboxToggled: (checked) => {
      // Сначала видимость, потом активация: холст должен уже иметь реальные
      // размеры в DOM (display не none), иначе корень-заполнитель при
      // первом рендере измерит себя нулевым.
      sandboxScroll.style.display = checked ? "flex" : "none";
      laneScroll.style.display = "none";
      gridScroll.style.display = checked ? "none" : "block";
      if (checked) {
        toolbar.uncheckDeps();
        activateSandbox();
      }
    },
    onSummary: () => {
      const filters = filterBar.activeFilters();
      const summaries = window.scriptExplorer.buildSummary(scripts, [...filters]);
      openSummaryDialog(summaries, scripts.length);
    },
    onReload: reload,
  });

  const root = el("div", {
    className: "screen",
    style: { flexDirection: "column", justifyContent: "flex-start", alignItems: "stretch", padding: "12px 16px", gap: "8px" },
  }, [
    toolbar.element,
    el("hr", { className: "separator" }),
    filterBar.element,
    gridScroll,
    laneScroll,
    sandboxScroll,
  ]);

  return {
    element: root,
    openProject(p) {
      project = p;
      toolbar.setTitle(p.name);
      reload();
    },
  };
}
