"use strict";
/**
 * Единая точка правды для настроек приложения — порт data/config.py.
 *
 * Читает settings.json в корне проекта (тот же файл, что и Python-версия —
 * во время переходного периода обе версии смотрят на одни и те же
 * настройки). Если файла нет или он повреждён — используются значения
 * по умолчанию, чтобы приложение не падало.
 */
const fs = require("fs");
const path = require("path");

const CONFIG_PATH = path.join(__dirname, "..", "..", "..", "settings.json");

const DEFAULTS = {
  refactor_threshold: 4,
  colors: {
    bg: "#F5F5F8",
    surface: "#FFFFFF",
    text: "#1E1E28",
    black: "#000000",
    accent: "#1EA8E6",
    accent_hover: "#28BEF8",
    accent_pressed: "#1690C8",
    danger: "#E05050",
    danger_hover: "#F06060",
    danger_pressed: "#C03030",
    muted: "#8A8C96",
    faint: "#AAAAAA",
    link: "#1E6ED6",
    border: "#DCDCE4",
    border_strong: "#999999",
    border_soft: "#C3C6CD",
    pill_name: "#46BE78",
    pill_method: "#28A8E0",
    pill_incoming: "#E05050",
    pill_text: "#111111",
    dep_dot: "#E87820",
    close: "#D83232",
    close_hover: "#F04040",
    close_pressed: "#B02020",
    scrollbar_bg: "#F0F0F4",
    scrollbar_handle: "#C0C4CC",
    badge_orange: "#D7781E",
    badge_blue: "#1E6ED6",
    badge_red: "#D73232",
    badge_dead: "#1E1E1E",
    badge_white: "#FFFFFF",
  },
};

function _loadRaw() {
  if (!fs.existsSync(CONFIG_PATH)) return {};
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
  } catch {
    return {};
  }
}

function _merged() {
  const raw = _loadRaw();
  const colors = { ...DEFAULTS.colors, ...(raw.colors || {}) };
  return {
    refactor_threshold: raw.refactor_threshold ?? DEFAULTS.refactor_threshold,
    colors,
  };
}

const SETTINGS = _merged();

module.exports = {
  SETTINGS,
  REFACTOR_THRESHOLD: SETTINGS.refactor_threshold,
  COLORS: SETTINGS.colors,
};
