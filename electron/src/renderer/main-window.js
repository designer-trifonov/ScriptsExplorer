"use strict";
/**
 * Переключение хаб <-> экран проекта — порт _open_project/_go_back
 * из ui/main_window.py.
 */
import { createHub } from "./components/hub.js";
import { createProjectView } from "./components/projectView.js";

const stack = document.getElementById("stack");

function show(screen) {
  stack.replaceChildren(screen);
}

const projectView = createProjectView({
  onBack: () => {
    show(hub.element);
    window.scriptExplorer.backRequested();
  },
});

const hub = createHub({
  onProjectOpened: (project) => {
    projectView.openProject(project);
    show(projectView.element);
    window.scriptExplorer.projectOpened(project);
  },
});

show(hub.element);
