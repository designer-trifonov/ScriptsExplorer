"use strict";
/**
 * Накатывает реальные цвета из settings.json (пробрасываются из main через
 * preload) поверх дефолтов в theme.css — то, что в Python-версии делал
 * Template.substitute(**COLORS) при сборке STYLESHEET.
 */
(function applyTheme() {
  const colors = window.scriptExplorer && window.scriptExplorer.colors;
  if (!colors) return;
  const root = document.documentElement.style;
  for (const [key, value] of Object.entries(colors)) {
    root.setProperty(`--${key.replace(/_/g, "-")}`, value);
  }
})();
