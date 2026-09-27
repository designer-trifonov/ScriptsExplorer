"use strict";
/**
 * Отвечает только за одно: надёжно найти методы в C#-исходнике и вернуть
 * их имя и тело для дальнейшего анализа — порт data/method_finder.py.
 * Комментарии по формам объявления методов и сознательно непокрытым
 * случаям — см. оригинал; логика скопирована один в один, включая
 * ручное сопоставление скобок (регулярка вида "[^)]*" ломается на
 * вложенных скобках generic/default-параметров).
 */
const _MODIFIERS = "(?:public|private|protected|internal|static|override|virtual|" +
  "abstract|async|new|sealed|readonly|extern|unsafe|partial|ref)";

const _RETURN_TYPE =
  "(?:" +
  "\\([^()]*\\)" +                                   // кортеж
  "|" +
  "[\\w.]+(?:<[^>{};]*>)?(?:\\[[,\\s]*\\])*[?*]?" +  // обычный/generic/массив
  ")";

const _OPERATOR_SYMBOLS = "(?:[+\\-*/%&|^!~<>=]+|true|false)";
const _METHOD_NAME = "(?:operator\\s*" + _OPERATOR_SYMBOLS + "|[\\w.]+)";

const _NOT_METHOD_HEAD = new Set([
  "return", "if", "else", "while", "for", "foreach", "switch", "catch",
  "using", "lock", "throw", "yield", "await", "checked", "unchecked",
  "new", "typeof", "nameof", "sizeof", "case", "do", "fixed",
]);

const _METHOD_HEAD_RE = new RegExp(
  "(?:" + _MODIFIERS + "\\s+)*" +
  "(" + _RETURN_TYPE + ")" +
  "\\s+(" + _METHOD_NAME + ")" +
  "(?:<[^>{};]*>)?" +   // generic у самого метода
  "\\s*\\(",
  "g"
);

/** Позиция ')', соответствующей '(' в openPos, с учётом вложенности. */
function _matchParen(src, openPos) {
  let depth = 0;
  for (let i = openPos; i < src.length; i++) {
    if (src[i] === "(") depth++;
    else if (src[i] === ")") {
      depth--;
      if (depth === 0) return i;
    }
  }
  return null;
}

function _extractBracedBody(src, openPos) {
  let depth = 0;
  const start = openPos;
  for (let i = openPos; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  return src.slice(start);
}

/** Конец expression-bodied тела (';' на верхнем уровне вложенности). */
function _findExprEnd(src, start) {
  let depth = 0;
  for (let i = start; i < src.length; i++) {
    const c = src[i];
    if (c === "(" || c === "[" || c === "{") depth++;
    else if (c === ")" || c === "]" || c === "}") depth--;
    else if (c === ";" && depth === 0) return i;
  }
  return null;
}

function findMethods(src) {
  const results = [];
  _METHOD_HEAD_RE.lastIndex = 0;
  let m;
  while ((m = _METHOD_HEAD_RE.exec(src)) !== null) {
    const returnType = m[1].split(".").pop();
    const name = m[2];
    if (_NOT_METHOD_HEAD.has(returnType) || _NOT_METHOD_HEAD.has(name)) continue;

    const closeParen = _matchParen(src, m.index + m[0].length - 1);
    if (closeParen === null) continue;

    let i = closeParen + 1;
    while (i < src.length && " \t\r\n".includes(src[i])) i++;

    // generic-ограничения ("where T : ...") стоят перед телом — если они
    // есть, тело всё равно начинается с ближайшей после них '{'.
    if (src.slice(i, i + 5) === "where") {
      const j = src.indexOf("{", i);
      if (j === -1) continue;
      i = j;
    }

    if (i < src.length && src[i] === "{") {
      results.push([name, _extractBracedBody(src, i)]);
    } else if (src.slice(i, i + 2) === "=>") {
      const end = _findExprEnd(src, i + 2);
      if (end !== null) results.push([name, src.slice(i, end + 1)]);
    }
    // иначе объявление заканчивается ';' без тела — пропускаем
  }
  return results;
}

module.exports = { findMethods };
