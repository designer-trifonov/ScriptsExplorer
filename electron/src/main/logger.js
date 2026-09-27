"use strict";
/**
 * Логирование всего приложения в один файл — порт data/config.py's
 * соседа main.py::_setup_logging(). INFO — обычный ход работы,
 * WARN/ERROR — что-то пошло не так.
 */
const fs = require("fs");
const path = require("path");

const LOG_PATH = path.join(__dirname, "..", "..", "script_explorer.log");

function _write(level, scope, message) {
  const line = `${new Date().toISOString()} ${level} ${scope}: ${message}\n`;
  fs.appendFile(LOG_PATH, line, () => {});
}

function getLogger(scope) {
  return {
    info: (message) => _write("INFO", scope, message),
    warn: (message) => _write("WARNING", scope, message),
    error: (message) => _write("ERROR", scope, message),
  };
}

module.exports = { getLogger };
