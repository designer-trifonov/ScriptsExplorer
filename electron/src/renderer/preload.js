"use strict";
const { contextBridge, ipcRenderer } = require("electron");
const { COLORS } = require("../shared/config");
const { buildSummary } = require("../shared/data/summaryBuilder");
const { nextPosition } = require("../shared/data/sandboxNewPosition");
const { requiredSize } = require("../shared/data/sandboxAutosize");

contextBridge.exposeInMainWorld("scriptExplorer", {
  projectOpened: (project) => ipcRenderer.send("project-opened", project),
  backRequested: () => ipcRenderer.send("back-requested"),
  colors: COLORS,

  projects: {
    load: () => ipcRenderer.invoke("projects:load"),
    add: (name, path) => ipcRenderer.invoke("projects:add", name, path),
    remove: (path) => ipcRenderer.invoke("projects:remove", path),
    pickFolder: () => ipcRenderer.invoke("projects:pick-folder"),
  },

  scanProject: (projectPath, scriptsOnly) => ipcRenderer.invoke("scan:project", projectPath, scriptsOnly),

  // Чистые CPU-функции без fs — гонять через main незачем, как и в
  // Python-версии (эти data/-модули вызывались прямо из ui/).
  buildSummary: (scripts, activeFilters) => buildSummary(scripts, new Set(activeFilters)),

  sandbox: {
    load: (projectPath) => ipcRenderer.invoke("sandbox:load", projectPath),
    save: (projectPath, session) => ipcRenderer.invoke("sandbox:save", projectPath, session),
    nextPosition,
    requiredSize,
  },
});
