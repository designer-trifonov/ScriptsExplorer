"use strict";
/**
 * Порт data/summary_builder.py.
 */

/** Проверяет, попадает ли скрипт хотя бы под один активный фильтр. */
function _matchesFilters(script, filters) {
  if (filters.has("lifecycle") && script.lifecycleCount > 0) return true;
  if (filters.has("refactor") && script.isRefactor) return true;
  if (filters.has("dead") && script.isDead) return true;
  if (filters.has("antipatterns") && script.totalAntipatterns > 0) return true;
  if (filters.has("incoming") && script.incoming.length > 0) return true;
  if (filters.has("outgoing") && script.allDeps.length > 0) return true;
  if (filters.has("dependencies") && script.totalDeps > 0) return true;
  return false;
}

/**
 * Single Responsibility: строит список замечаний по скриптам.
 * activeFilters — если не пустой, показывает только скрипты, попадающие
 * хотя бы под один фильтр.
 */
function buildSummary(scripts, activeFilters = null) {
  const filters = activeFilters || new Set();
  const useFilter = filters.size > 0;
  const result = [];

  for (const script of scripts) {
    if (useFilter && !_matchesFilters(script, filters)) continue;

    const items = [];
    if (script.totalDeps > 0) {
      items.push({ badge: "dep", text: "Высокая связность. Нужно проверить зависимости" });
    }
    if (script.isRefactor) {
      items.push({ badge: "R", text: "Возможно, нарушение SRP. Нужно проверить" });
    }
    if (script.totalAntipatterns > 0) {
      items.push({ badge: "!", text: "Проверь антипаттерны" });
    }
    if (script.isDead) {
      items.push({ badge: "D", text: "Возможно, имеется мёртвый код. Нужно проверить" });
    }

    if (items.length > 0) {
      result.push({ className: script.className, items });
    }
  }

  return result;
}

module.exports = { buildSummary };
