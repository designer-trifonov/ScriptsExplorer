"use strict";
/**
 * S: только хранение списка проектов в JSON — порт data/project_store.py.
 */
const fs = require("fs");
const path = require("path");
const { getLogger } = require("../../main/logger");

const logger = getLogger("projectStore");

const STORE_PATH = path.join(__dirname, "..", "..", "..", "..", "projects.json");

function load() {
  if (!fs.existsSync(STORE_PATH)) return [];
  try {
    return JSON.parse(fs.readFileSync(STORE_PATH, "utf-8"));
  } catch (e) {
    logger.error(`Не удалось прочитать ${STORE_PATH}: ${e}`);
    return [];
  }
}

function save(projects) {
  try {
    fs.writeFileSync(STORE_PATH, JSON.stringify(projects, null, 2), "utf-8");
  } catch (e) {
    logger.error(`Не удалось сохранить ${STORE_PATH}: ${e}`);
  }
}

function add(name, projectPath) {
  const projects = load();
  if (!projects.some((p) => p.path === projectPath)) {
    projects.push({ name, path: projectPath });
    save(projects);
    logger.info(`Добавлен проект: ${name} (${projectPath})`);
  }
  return projects;
}

function remove(projectPath) {
  const projects = load().filter((p) => p.path !== projectPath);
  save(projects);
  logger.info(`Удалён проект: ${projectPath}`);
  return projects;
}

module.exports = { load, save, add, remove };
