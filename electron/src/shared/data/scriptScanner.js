"use strict";
/**
 * Координирует шаги сканирования проекта. Сам ничего не ищет и не
 * решает — каждый шаг делегирован своему модулю. Порт data/script_scanner.py.
 *   1. fileFinder             — найти .cs файлы на диске
 *   2. scriptParser           — разобрать каждый файл
 *   3. dependencyGraph        — построить связи "кто на кого ссылается" (классы)
 *   4. methodDependencyGraph  — то же самое, но по методам
 *   5. deadChecker            — определить мёртвые скрипты
 */
const { getLogger } = require("../../main/logger");
const { findCsFiles } = require("./fileFinder");
const { parseFile, collectClassNames } = require("./scriptParser");
const { attachIncoming } = require("./dependencyGraph");
const { attachMethodIncoming } = require("./methodDependencyGraph");
const { markDeadScripts } = require("./deadChecker");

const logger = getLogger("scriptScanner");

function scanProject(projectPath, scriptsOnly = true, exclude = null) {
  logger.info(`Сканирование проекта: ${projectPath} (scriptsOnly=${scriptsOnly})`);

  const paths = findCsFiles(projectPath, scriptsOnly, exclude);
  if (paths.length === 0) {
    logger.warn(`В проекте не найдено ни одного .cs файла: ${projectPath}`);
    return [];
  }

  const projectClasses = collectClassNames(paths);
  const results = paths.map((p) => parseFile(p, projectClasses));

  attachIncoming(results);
  attachMethodIncoming(results);
  markDeadScripts(results, projectPath);

  const deadCount = results.filter((s) => s.isDead).length;
  logger.info(`Просканировано ${results.length} скриптов, мёртвых: ${deadCount}`);

  return results;
}

module.exports = { scanProject };
