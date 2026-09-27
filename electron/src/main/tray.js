"use strict";
/**
 * Иконка в системном трее — порт ui/tray.py.
 *
 * Single Responsibility: управляет только значком и его меню. Не знает
 * ни про окно, ни про кнопку-пуск напрямую — обо всём просит
 * orchestrator (showWindow/restart/quit), который и решает, что для
 * этого нужно сделать.
 */
const { Tray, Menu } = require("electron");
const { generateTrayIcon } = require("./trayIcon");

class TrayIcon {
  static async create(orchestrator) {
    const icon = await generateTrayIcon();
    return new TrayIcon(icon, orchestrator);
  }

  constructor(icon, orchestrator) {
    this._app = orchestrator;
    this._tray = new Tray(icon);
    this._tray.setToolTip("Script Explorer");

    this._tray.setContextMenu(
      Menu.buildFromTemplate([
        { label: "Show App", click: () => this._app.showWindow() },
        { label: "Restart", click: () => this._app.restart() },
        { label: "Close App", click: () => this._app.quit() },
      ])
    );

    this._tray.on("double-click", () => this._app.showWindow());
  }

  /** Balloon-уведомление при первом сворачивании в трей — порт notify_hidden(). */
  notifyHidden() {
    this._tray.displayBalloon({
      title: "Script Explorer",
      content: "Приложение свёрнуто в трей",
    });
  }
}

module.exports = { TrayIcon };
