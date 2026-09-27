"use strict";
/**
 * Хаб (список проектов) — порт ui/hub.py.
 */
import { el } from "./dom.js";

export function createHub({ onProjectOpened }) {
  const listLayout = el("div", { style: { display: "flex", flexDirection: "column", gap: "6px" } });

  async function refresh() {
    const projects = await window.scriptExplorer.projects.load();
    renderProjects(projects);
  }

  function renderProjects(projects) {
    listLayout.replaceChildren();
    if (!projects.length) {
      listLayout.append(el("span", { className: "empty-label", text: "Нет проектов" }));
      return;
    }
    for (const p of projects) {
      const btn = el("button", {
        className: "btn-project",
        text: p.name,
        style: { width: "200px", height: "28px", textAlign: "left", paddingLeft: "10px" },
        onClick: () => onProjectOpened(p),
      });
      const btnRemove = el("button", {
        className: "btn-remove",
        text: "✕",
        style: { width: "28px", height: "28px" },
        onClick: async () => { await window.scriptExplorer.projects.remove(p.path); refresh(); },
      });
      const row = el("div", { style: { display: "flex", gap: "6px" } }, [btn, btnRemove]);
      listLayout.append(row);
    }
  }

  const addBtn = el("button", {
    className: "btn-primary",
    text: "+ Добавить проект",
    style: { height: "28px" },
    onClick: async () => {
      const path = await window.scriptExplorer.projects.pickFolder();
      if (!path) return;
      const name = path.replace(/[\\/]+$/, "").split(/[\\/]/).pop();
      await window.scriptExplorer.projects.add(name, path);
      refresh();
    },
  });

  const header = el("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between" } }, [
    el("span", { className: "hub-title", text: "Script Explorer" }),
    addBtn,
  ]);

  const root = el("div", {
    className: "screen",
    style: { flexDirection: "column", justifyContent: "flex-start", alignItems: "stretch", padding: "20px 28px", gap: "0" },
  }, [
    header,
    el("div", { style: { height: "12px" } }),
    el("hr", { className: "separator" }),
    el("div", { style: { height: "16px" } }),
    el("span", { className: "section-label", text: "Последние проекты" }),
    el("div", { style: { height: "10px" } }),
    listLayout,
  ]);

  refresh();

  return { element: root, refresh };
}
