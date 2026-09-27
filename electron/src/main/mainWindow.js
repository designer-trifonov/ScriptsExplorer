"use strict";
/**
 * Визуальная оболочка приложения — порт ui/main_window.py.
 *
 * Ничего не знает про трей, конфиг или источники данных — их подключает
 * orchestrator.js, реагируя на события этого модуля. Переключение
 * хаб/экран-проекта живёт в рендерере (src/renderer/main-window.js);
 * здесь только окно и приход/уход IPC-сигналов "open-project" / "go-back",
 * которые в PySide-версии были сигналами hub.project_opened /
 * view.back_requested.
 */
const path = require("path");
const { BrowserWindow, ipcMain } = require("electron");
const { EventEmitter } = require("events");
const { getLogger } = require("./logger");

const logger = getLogger("renderer");

// Минимальный осмысленный размер окна — песочница с видимым именем и хотя
// бы 4 скриптами внутри (2×2), иначе не помещается вообще ничего. Числа
// собраны из тех же констант, что и раскладка песочницы (CELL_W=59,
// CELL_H=88, SANDBOX_MARGIN=16 — src/renderer/components/scriptCard.js,
// scriptCellView.js, sandboxLayoutConstants.js), плюс отступы экрана
// проекта (padding .screen 16/12px) и высота тулбара с кнопкой создания.
const MIN_SANDBOX_CONTENT_W = 16 * 3 + 59 * 2; // = 166
const MIN_SANDBOX_CONTENT_H = 16 * 3 + 88 * 2; // = 224
const MIN_WIDTH = MIN_SANDBOX_CONTENT_W + 16 * 2; // + padding .screen слева/справа
const MIN_HEIGHT = MIN_SANDBOX_CONTENT_H + 100; // + тулбар/кнопка "Создать песочницу"/отступы

class MainWindow extends EventEmitter {
  constructor() {
    super();
    this._win = new BrowserWindow({
      width: 520,
      height: 735,
      minWidth: MIN_WIDTH,
      minHeight: MIN_HEIGHT,
      title: "Script Explorer",
      webPreferences: {
        preload: path.join(__dirname, "..", "renderer", "preload.js"),
        contextIsolation: true,
        // preload использует require() своих же Node-модулей (data-слой,
        // config) — песочница Electron по умолчанию это запрещает.
        sandbox: false,
      },
    });
    this._win.loadFile(path.join(__dirname, "..", "renderer", "index.html"));

    // Ошибки/варнинги из renderer-кода иначе падают молча — пишем их в
    // тот же лог, что и весь остальной процесс.
    this._win.webContents.on("console-message", (_e, level, message, line, sourceId) => {
      if (level >= 2) logger.error(`${sourceId}:${line} ${message}`);
    });

    // Сворачивание в трей вместо закрытия — саму нотификацию трея
    // делает тот, кто на это подписан (orchestrator.js), как и в Qt-версии.
    this._win.on("close", (e) => {
      if (this._closing) return;
      e.preventDefault();
      this._win.hide();
      this.emit("hidden");
    });

    ipcMain.on("project-opened", (_e, project) => this.emit("project-opened", project));
    ipcMain.on("back-requested", () => this.emit("back-requested"));
  }

  show() {
    this._win.show();
    this._win.focus();
  }

  isVisible() {
    return this._win.isVisible();
  }

  hide() {
    this._win.hide();
  }

  /** Разрешает окну реально закрыться — вызывается перед quit(). */
  allowClose() {
    this._closing = true;
  }
}

module.exports = { MainWindow };
