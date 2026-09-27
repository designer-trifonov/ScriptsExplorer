"use strict";
/**
 * IPC-мост между renderer и Node-слоем данных (fs-операции обязаны идти
 * в main-процессе, а не блокировать UI-поток renderer'а). Обычные вызовы
 * функций в Python-версии (scan_project(), project_store.load(), ...) —
 * здесь их эквиваленты, просто через ipcMain.handle/ipcRenderer.invoke.
 */
const { ipcMain, dialog, BrowserWindow } = require("electron");
const projectStore = require("../shared/data/projectStore");
const { scanProject } = require("../shared/data/scriptScanner");
const sandboxStore = require("../shared/data/sandboxStore");

function registerApi() {
  ipcMain.handle("projects:load", () => projectStore.load());
  ipcMain.handle("projects:add", (_e, name, projectPath) => projectStore.add(name, projectPath));
  ipcMain.handle("projects:remove", (_e, projectPath) => projectStore.remove(projectPath));

  ipcMain.handle("projects:pick-folder", async (e) => {
    const win = BrowserWindow.fromWebContents(e.sender);
    const result = await dialog.showOpenDialog(win, {
      title: "Выбери папку Unity проекта",
      properties: ["openDirectory"],
    });
    if (result.canceled || result.filePaths.length === 0) return null;
    return result.filePaths[0];
  });

  ipcMain.handle("scan:project", (_e, projectPath, scriptsOnly) => {
    const scripts = scanProject(projectPath, scriptsOnly);
    // JSON.stringify вызывает ScriptInfo.toJSON() — так геттеры (totalDeps,
    // isRefactor, ...) попадают в структуру ДО structured-clone на границе IPC.
    return JSON.parse(JSON.stringify(scripts));
  });

  ipcMain.handle("sandbox:load", (_e, projectPath) => sandboxStore.loadSession(projectPath));
  ipcMain.handle("sandbox:save", (_e, projectPath, session) => sandboxStore.saveSession(projectPath, session));
}

module.exports = { registerApi };
