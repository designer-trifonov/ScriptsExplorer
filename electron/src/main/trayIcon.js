"use strict";
/**
 * Рисует иконку трея так же, как _make_icon() в ui/tray.py:
 * 64×64 синий круг с буквами "SE". Electron не умеет растеризовать SVG
 * в nativeImage напрямую, поэтому рисуем на <canvas> в скрытом окне и
 * захватываем результат — это и есть аналог QPainter в Python-версии.
 */
const { BrowserWindow, nativeImage } = require("electron");
const { COLORS } = require("../shared/config");

const ACCENT = COLORS.accent;

const _HTML = `<!DOCTYPE html><html><body style="margin:0">
<canvas id="c" width="64" height="64"></canvas>
<script>
  const ctx = document.getElementById("c").getContext("2d");
  ctx.clearRect(0, 0, 64, 64);
  ctx.fillStyle = "${ACCENT}";
  ctx.beginPath();
  ctx.arc(32, 32, 30, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "white";
  ctx.font = "bold 20px 'Segoe UI'";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("SE", 32, 33);
</script>
</body></html>`;

async function generateTrayIcon() {
  const win = new BrowserWindow({
    width: 64,
    height: 64,
    show: false,
    transparent: true,
    webPreferences: { offscreen: true },
  });
  try {
    await win.loadURL("data:text/html;charset=utf-8," + encodeURIComponent(_HTML));
    const capture = await win.webContents.capturePage();
    return nativeImage.createFromBuffer(capture.toPNG());
  } finally {
    win.destroy();
  }
}

module.exports = { generateTrayIcon };
