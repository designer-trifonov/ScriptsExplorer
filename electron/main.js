"use strict";
/**
 * Точка входа — порт main.py. Единственная задача: поднять процесс и
 * запустить оркестратор. Проверка "не второй экземпляр" в Electron не
 * нужно собирать вручную через QLocalServer — для этого есть штатный
 * app.requestSingleInstanceLock().
 */
const { app } = require("electron");
const { AppOrchestrator } = require("./src/main/orchestrator");
const { registerApi } = require("./src/main/api");
const { getLogger } = require("./src/main/logger");

const logger = getLogger("main");

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  logger.info("Уже запущен другой экземпляр — выходим");
  app.quit();
} else {
  let orchestrator = null;

  // Второй запуск: вместо нового окна поднимаем существующее — аналог
  // того, что делал QLocalServer/QLocalSocket-хэндшейк в main.py.
  app.on("second-instance", () => {
    if (orchestrator) orchestrator.showWindow();
  });

  // Сворачивание в трей не должно закрывать процесс — аналог
  // app.setQuitOnLastWindowClosed(False) в Qt-версии.
  app.on("window-all-closed", () => {});

  app.whenReady().then(async () => {
    logger.info("Script Explorer: запуск");
    registerApi();
    orchestrator = new AppOrchestrator();
    await orchestrator.start();
  });
}
