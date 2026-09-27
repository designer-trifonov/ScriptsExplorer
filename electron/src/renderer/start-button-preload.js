"use strict";
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("startButton", {
  clicked: () => ipcRenderer.send("start-button-clicked"),
  reportWidth: (px) => ipcRenderer.send("start-button-width", px),
});
