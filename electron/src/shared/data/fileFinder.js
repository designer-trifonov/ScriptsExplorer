"use strict";
/**
 * Отвечает только за одно: найти .cs файлы Unity-проекта на диске —
 * порт data/file_finder.py.
 */
const fs = require("fs");
const path = require("path");
const { getLogger } = require("../../main/logger");

const logger = getLogger("fileFinder");

const DEFAULT_EXCLUDE = new Set(["Editor", "TextMesh Pro", "ithappy", "Examples", "Extras"]);

function _walk(base, exclude, onFile) {
  let entries;
  try {
    entries = fs.readdirSync(base, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (exclude.has(entry.name)) continue;
      _walk(path.join(base, entry.name), exclude, onFile);
    } else {
      onFile(path.join(base, entry.name));
    }
  }
}

function findCsFiles(projectPath, scriptsOnly = true, exclude = null) {
  const excludeSet = exclude || DEFAULT_EXCLUDE;
  const base = scriptsOnly
    ? path.join(projectPath, "Assets", "Scripts")
    : path.join(projectPath, "Assets");

  if (!fs.existsSync(base)) {
    logger.warn(`Папка проекта не найдена: ${base}`);
    return [];
  }

  const paths = [];
  _walk(base, excludeSet, (filePath) => {
    if (filePath.endsWith(".cs")) paths.push(filePath);
  });

  logger.info(`Найдено ${paths.length} .cs файлов в ${base}`);
  return paths;
}

module.exports = { findCsFiles, DEFAULT_EXCLUDE };
