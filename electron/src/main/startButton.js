"use strict";
/**
 * "Пилюля" поверх таскбара — порт ui/start_button.py.
 *
 * В Python-версии это было окно, которое приходилось силой удерживать
 * поверх таскбара через сырые Win32-вызовы (SetWindowPos на таймере),
 * потому что Qt-окно без owner'а Windows норовит спрятать. Electron даёт
 * то же самое (alwaysOnTop + skipTaskbar) как штатную кросс-платформенную
 * функцию — heartbeat/ctypes здесь не нужны.
 */
const path = require("path");
const { BrowserWindow, ipcMain, screen } = require("electron");

const H = 48;
const OFFSET_X = 10;

class StartButton {
  constructor(mainWindow) {
    this._win_ref = mainWindow;
    this._closing = false;

    const full = screen.getPrimaryDisplay().bounds;
    this._win = new BrowserWindow({
      width: 160, // временная ширина — уточняется по фактической ширине текста
      height: H,
      x: OFFSET_X,
      y: full.height - H,
      frame: false,
      transparent: true,
      resizable: false,
      alwaysOnTop: true,
      skipTaskbar: true,
      focusable: false,
      webPreferences: {
        preload: path.join(__dirname, "..", "renderer", "start-button-preload.js"),
        contextIsolation: true,
      },
    });
    this._win.setAlwaysOnTop(true, "screen-saver");
    this._win.loadFile(path.join(__dirname, "..", "renderer", "start-button.html"));

    ipcMain.on("start-button-clicked", () => this._toggle());
    ipcMain.on("start-button-width", (_e, px) => this._applyWidth(px));
  }

  _applyWidth(px) {
    const full = screen.getPrimaryDisplay().bounds;
    this._win.setBounds({ x: OFFSET_X, y: full.height - H, width: px, height: H });
  }

  _toggle() {
    if (this._win_ref.isVisible()) {
      this._win_ref.hide();
    } else {
      this._win_ref.show();
    }
  }

  quit() {
    this._closing = true;
    this._win.close();
  }
}

module.exports = { StartButton };
