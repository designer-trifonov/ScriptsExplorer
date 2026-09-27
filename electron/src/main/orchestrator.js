"use strict";
/**
 * Оркестратор приложения — порт app_orchestrator.py.
 *
 * Единственное место, которое собирает визуал (MainWindow) и системную
 * интеграцию (трей, кнопка-пуск) вместе и управляет жизненным циклом
 * окна. main.js — это только точка входа: создаёт оркестратор и
 * запускает его, сама ничего не собирает и не решает.
 */
const { app } = require("electron");
const { MainWindow } = require("./mainWindow");
const { TrayIcon } = require("./tray");
const { StartButton } = require("./startButton");
const { getLogger } = require("./logger");

const logger = getLogger("orchestrator");

class AppOrchestrator {
  constructor() {
    this._window = new MainWindow();
    this._window.on("hidden", () => this._onWindowHidden());

    this._tray = null;
    this._startBtn = null;
    this._trayNoted = false; // balloon только один раз
  }

  async start() {
    logger.info("Оркестратор: показываю окно, создаю трей и кнопку-пуск");
    this._window.show();
    // Трей и кнопка-пуск создаются после show() — как и в Qt-версии, нужно
    // готовое окно, прежде чем цеплять к нему системную интеграцию.
    this._tray = await TrayIcon.create(this);
    this._startBtn = new StartButton(this._window);
  }

  // ── команды, которые трею и кнопке-пуску не нужно знать, как выполнять ──
  showWindow() {
    logger.info("Окно показано из трея/кнопки-пуска");
    this._window.show();
  }

  restart() {
    logger.info("Перезапуск приложения");
    if (this._startBtn) this._startBtn.quit();
    app.relaunch();
    app.exit(0);
  }

  quit() {
    // Разблокируем окно перед выходом, иначе close-хендлер заблокирует quit.
    logger.info("Завершение приложения по команде пользователя");
    if (this._startBtn) this._startBtn.quit();
    this._window.allowClose();
    app.quit();
  }

  // ── реакция на события окна ──────────────────────────────────────────
  _onWindowHidden() {
    logger.info("Окно свёрнуто в трей");
    if (this._tray && !this._trayNoted) {
      this._trayNoted = true;
      this._tray.notifyHidden();
    }
  }
}

module.exports = { AppOrchestrator };
