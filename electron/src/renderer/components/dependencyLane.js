"use strict";
/**
 * Лента зависимостей — порт ui/dependency_lane.py.
 */
import { el } from "./dom.js";
import { createPill } from "./pill.js";

function centered(child) {
  return el("div", { className: "dep-slot__row" }, [child]);
}

function section(title, names, pillClass) {
  const box = el("div", { className: "dep-slot__section" }, [
    el("span", { className: "section-label", text: title }),
  ]);
  if (!names.length) {
    box.append(el("span", { className: "empty-label", text: "—" }));
  } else {
    for (const name of names) box.append(centered(createPill(name, pillClass)));
  }
  return box;
}

function createDependencySlot(script, onClick) {
  const namePill = createPill(script.className, "pill-name");
  namePill.title = script.filePath;

  const slot = el("div", { className: "dep-slot" }, [
    centered(namePill),
    section("Исходящие", script.allDeps, "pill-method"),
    section("Входящие", script.incoming, "pill-incoming"),
  ]);
  slot.addEventListener("click", () => onClick && onClick(script));
  return slot;
}

export function createDependencyLane(onScriptClicked) {
  const root = el("div", { className: "dep-lane" });

  return {
    element: root,
    setScripts(scripts) {
      root.replaceChildren();
      const ordered = [...scripts].sort((a, b) => b.allDeps.length - a.allDeps.length);
      for (const script of ordered) {
        root.append(createDependencySlot(script, onScriptClicked));
      }
    },
  };
}
