"use strict";
/**
 * Отвечает только за одно: найти имена методов, которые вызываются
 * в теле метода — порт data/method_calls.py. Приближённый анализ по
 * совпадению имени, без резолвинга типов.
 */
const _CALL_RE = /\b([A-Za-z_]\w*)\s*\(/g;

const _NOT_CALLS = new Set([
  "if", "for", "foreach", "while", "switch", "catch", "using", "lock",
  "new", "typeof", "nameof", "sizeof", "return", "base", "this",
]);

function findCalls(body) {
  const found = new Set();
  for (const m of body.matchAll(_CALL_RE)) {
    if (!_NOT_CALLS.has(m[1])) found.add(m[1]);
  }
  return [...found].sort();
}

module.exports = { findCalls };
