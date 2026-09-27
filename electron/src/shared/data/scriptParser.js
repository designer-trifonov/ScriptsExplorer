"use strict";
/**
 * Порт data/script_parser.py.
 */
const fs = require("fs");
const path = require("path");
const { getLogger } = require("../../main/logger");
const { MethodInfo, ScriptInfo } = require("./models");
const { findAntipatterns } = require("./antipatternChecker");
const { findCalls } = require("./methodCalls");
const { findMethods } = require("./methodFinder");

const logger = getLogger("scriptParser");

const _CLASS_RE = /\b(?:class|struct|interface|enum|record)\s+(\w+)/;
const _CLASS_DECL_RE = /\b(?:class|struct)\s+\w+[^:]*:\s*([\w\s,<>]+?)(?:\s*\{)/m;
const _MONO_BASES = new Set([
  "MonoBehaviour", "NetworkBehaviour", "ScriptableObject",
  "Editor", "EditorWindow", "PropertyDrawer",
]);

const _TYPE_RE = /\b([A-Z][a-zA-Z0-9_]*)\b/g;
const _COMMENT_RE = /\/\/[^\n]*|\/\*[\s\S]*?\*\//g;

/**
 * Заменяет содержимое комментариев пробелами, сохраняя длину и переносы
 * строк, чтобы позиции символов (скобки, номера строк) не сдвигались.
 */
function _stripComments(src) {
  return src.replace(_COMMENT_RE, (m) => m.replace(/[^\n]/g, " "));
}

function _findDeps(body, own, projectClasses) {
  const found = new Set();
  for (const m of body.matchAll(_TYPE_RE)) {
    const name = m[1];
    if (name !== own && projectClasses.has(name)) found.add(name);
  }
  return [...found].sort();
}

function collectClassNames(paths) {
  const names = new Set();
  for (const p of paths) {
    try {
      const src = fs.readFileSync(p, "utf-8");
      const m = _CLASS_RE.exec(_stripComments(src));
      if (m) names.add(m[1]);
    } catch (e) {
      logger.warn(`Не удалось прочитать файл ${p}: ${e}`);
    }
  }
  return names;
}

function parseFile(filePath, projectClasses = null) {
  let src = fs.readFileSync(filePath, "utf-8");
  src = _stripComments(src);

  const cm = _CLASS_RE.exec(src);
  const className = cm ? cm[1] : path.basename(filePath, path.extname(filePath));

  let isMono = false;
  let projectBases = [];
  const decl = _CLASS_DECL_RE.exec(src);
  if (decl) {
    const raw = new Set(decl[1].split(",").map((b) => b.trim().split("<")[0]));
    const pc = projectClasses || new Set();
    isMono = [...raw].some((b) => _MONO_BASES.has(b));
    projectBases = [...raw].filter((b) => pc.has(b)).sort();
  }

  const info = new ScriptInfo({ className, filePath, isMono, bases: projectBases });
  const seen = new Set();
  const pc = projectClasses || new Set();

  function add(methodName, body) {
    if (methodName === className || seen.has(methodName)) return;
    seen.add(methodName);
    const deps = _findDeps(body, className, pc);
    const antipatterns = findAntipatterns(body);
    const calls = findCalls(body);
    info.methods.push(new MethodInfo({ name: methodName, depCount: deps.length, deps, antipatterns, calls }));
  }

  for (const [methodName, body] of findMethods(src)) {
    add(methodName, body);
  }

  // Типы упомянутые вне тел методов (поля, инициализаторы, базовые типы)
  const already = new Set(info.methods.flatMap((m) => m.deps));
  const mentioned = new Set([...src.matchAll(_TYPE_RE)].map((m) => m[1]));
  info.classDeps = [...mentioned]
    .filter((name) => pc.has(name) && name !== className && !already.has(name))
    .sort();

  return info;
}

module.exports = { parseFile, collectClassNames };
