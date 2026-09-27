"use strict";
/**
 * Определяет живые скрипты через сцены, префабы и ассеты — порт
 * data/dead_checker.py.
 *
 * Алгоритм:
 *   1. Для каждого ScriptInfo читаем .meta -> берём GUID файла
 *   2. Сканируем .unity/.prefab/.asset -> собираем GUID из m_Script
 *   3. Пересечение -> имена живых классов
 *
 * .asset покрывает ScriptableObject-экземпляры: они хранят m_Script
 * точно так же как MonoBehaviour, только в файле ассета а не сцены.
 */
const fs = require("fs");
const path = require("path");
const { getLogger } = require("../../main/logger");

const logger = getLogger("deadChecker");

const _META_GUID = /^guid:\s*(\w+)/m;
const _SCENE_GUID = /m_Script:\s*\{[^}]*guid:\s*(\w+)/g;

const _SCAN_EXT = [".unity", ".prefab", ".asset"];

function _readGuid(metaPath) {
  try {
    const m = _META_GUID.exec(fs.readFileSync(metaPath, "utf-8"));
    return m ? m[1] : null;
  } catch (e) {
    logger.warn(`Не удалось прочитать .meta файл ${metaPath}: ${e}`);
    return null;
  }
}

function _walk(dir, onFile) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) _walk(full, onFile);
    else onFile(full);
  }
}

function _collectSceneGuids(projectPath) {
  const guids = new Set();
  const assets = path.join(projectPath, "Assets");
  if (!fs.existsSync(assets)) return guids;

  _walk(assets, (filePath) => {
    if (!_SCAN_EXT.some((ext) => filePath.endsWith(ext))) return;
    try {
      const content = fs.readFileSync(filePath, "utf-8");
      for (const m of content.matchAll(_SCENE_GUID)) guids.add(m[1]);
    } catch (e) {
      logger.warn(`Не удалось прочитать файл сцены/ассета ${filePath}: ${e}`);
    }
  });
  return guids;
}

/** Возвращает имена классов, которые реально используются в сценах/префабах/ассетах. */
function getLiveClasses(scripts, projectPath) {
  const sceneGuids = _collectSceneGuids(projectPath);

  const live = new Set();
  for (const script of scripts) {
    const meta = script.filePath + ".meta";
    const guid = _readGuid(meta);
    if (guid && sceneGuids.has(guid)) live.add(script.className);
  }
  return live;
}

/**
 * Помечает script.isDead для каждого скрипта: ни на кого не ссылаются,
 * не используются в сценах/префабах/ассетах и при этом что-то делают.
 */
function markDeadScripts(scripts, projectPath) {
  const liveInScenes = getLiveClasses(scripts, projectPath);
  for (const script of scripts) {
    script.isDead =
      script.incoming.length === 0 &&
      !liveInScenes.has(script.className) &&
      script.methods.length > 0;
  }
}

module.exports = { getLiveClasses, markDeadScripts };
