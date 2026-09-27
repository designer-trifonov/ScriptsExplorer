"use strict";
/**
 * Хранит и загружает настройки конкретного проекта — порт
 * data/project_config.py. У каждого проекта свой файл (ключ — sha1 от
 * пути проекта, как и в Python-версии), чтобы обе версии приложения во
 * время переходного периода читали одни и те же файлы конфигов.
 */
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { getLogger } = require("../main/logger");

const logger = getLogger("projectConfig");

const CONFIG_DIR = path.join(__dirname, "..", "..", "..", "project_configs");

const DEFAULTS = {
  sandbox: null, // заполняется sandboxStore.js при первом сохранении
};

function _configPath(projectPath) {
  const key = crypto.createHash("sha1").update(projectPath, "utf-8").digest("hex").slice(0, 16);
  return path.join(CONFIG_DIR, `${key}.json`);
}

function load(projectPath) {
  const p = _configPath(projectPath);
  if (!fs.existsSync(p)) {
    logger.info(`Конфиг проекта не найден, использую значения по умолчанию: ${projectPath}`);
    return { ...DEFAULTS };
  }
  try {
    const data = JSON.parse(fs.readFileSync(p, "utf-8"));
    logger.info(`Загружен конфиг проекта ${projectPath} из ${p}`);
    return { ...DEFAULTS, ...data };
  } catch (e) {
    logger.error(`Не удалось прочитать конфиг проекта ${projectPath} (${p}): ${e}`);
    return { ...DEFAULTS };
  }
}

function save(projectPath, data) {
  try {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
    const p = _configPath(projectPath);
    fs.writeFileSync(p, JSON.stringify(data, null, 2), "utf-8");
    logger.info(`Сохранён конфиг проекта ${projectPath} в ${p}`);
  } catch (e) {
    logger.error(`Не удалось сохранить конфиг проекта ${projectPath}: ${e}`);
  }
}

module.exports = { load, save };
