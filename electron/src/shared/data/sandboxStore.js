"use strict";
/**
 * Сохраняет и загружает "сессию песочницы" — порт data/sandbox_store.py.
 * Хранится в конфиге конкретного проекта (projectConfig.js).
 */
const { getLogger } = require("../../main/logger");
const projectConfig = require("../projectConfig");

const logger = getLogger("sandboxStore");

/**
 * @typedef {Object} SandboxNode
 * @property {string} id
 * @property {string} name
 * @property {string} borderColor
 * @property {string|null} backgroundColor
 * @property {number} x
 * @property {number} y
 * @property {number} width
 * @property {number} height
 * @property {boolean} manuallyPositioned
 * @property {boolean} draggable — false только у корня: его нельзя таскать
 * @property {string[]} scriptPaths
 * @property {SandboxNode[]} children
 */

function makeNode({ id, name, borderColor, backgroundColor = null, x, y, width, height,
                     manuallyPositioned = false, draggable = true, scriptPaths = [], children = [] }) {
  return { id, name, borderColor, backgroundColor, x, y, width, height, manuallyPositioned, draggable, scriptPaths, children };
}

function _nodeFromRaw(data) {
  return makeNode({
    id: data.id,
    name: data.name,
    borderColor: data.border_color,
    backgroundColor: data.background_color ?? null,
    x: data.x, y: data.y,
    width: data.width, height: data.height,
    manuallyPositioned: data.manually_positioned ?? false,
    draggable: data.draggable ?? true,
    scriptPaths: [...(data.script_paths || [])],
    children: (data.children || []).map(_nodeFromRaw),
  });
}

function _nodeToRaw(node) {
  return {
    id: node.id,
    name: node.name,
    border_color: node.borderColor,
    background_color: node.backgroundColor,
    x: node.x, y: node.y,
    width: node.width, height: node.height,
    manually_positioned: node.manuallyPositioned,
    draggable: node.draggable,
    script_paths: node.scriptPaths,
    children: node.children.map(_nodeToRaw),
  };
}

function loadSession(projectPath) {
  const config = projectConfig.load(projectPath);
  const raw = config.sandbox;
  if (!raw) {
    logger.info(`У проекта ${projectPath} ещё нет сохранённой сессии песочницы`);
    return null;
  }
  try {
    const session = {
      root: _nodeFromRaw(raw.root),
      looseScripts: Object.fromEntries(Object.entries(raw.loose_scripts || {})),
    };
    logger.info(`Загружена сессия песочницы для ${projectPath}`);
    return session;
  } catch (e) {
    logger.error(`Сессия песочницы проекта ${projectPath} повреждена, начинаю с чистого листа: ${e}`);
    return null;
  }
}

function saveSession(projectPath, session) {
  const config = projectConfig.load(projectPath);
  config.sandbox = {
    root: _nodeToRaw(session.root),
    loose_scripts: session.looseScripts,
  };
  projectConfig.save(projectPath, config);
  logger.info(`Сохранена сессия песочницы для ${projectPath}`);
}

module.exports = { makeNode, loadSession, saveSession };
