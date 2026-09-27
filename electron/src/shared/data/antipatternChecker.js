"use strict";
/**
 * Отвечает только за одно: найти известные Unity-антипаттерны в теле
 * метода — порт data/antipattern_checker.py.
 */
const _ANTIPATTERNS = [
  ["FindObjectOfType", /\bFindObjectsOfType\b|\bFindObjectOfType\b/],
  ["GameObject.Find",  /\bGameObject\.Find\b/],
  ["Camera.main",      /\bCamera\.main\b/],
  ["GetComponent",     /\bGetComponent\b/],
  ["CompareTag",       /\bCompareTag\b/],
  ["tag ==",           /\btag\s*==|==\s*\btag\b/],
  ["SendMessage",      /\bSendMessage\b/],
  ["Resources.Load",   /\bResources\.Load\b/],
];

function findAntipatterns(body) {
  return _ANTIPATTERNS.filter(([, pat]) => pat.test(body)).map(([name]) => name);
}

module.exports = { findAntipatterns };
