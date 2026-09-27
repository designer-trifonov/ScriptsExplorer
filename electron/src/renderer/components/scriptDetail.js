"use strict";
/**
 * Диалог деталей скрипта — порт ui/script_detail.py.
 */
import { el } from "./dom.js";
import { createBaseDialog } from "./baseDialog.js";
import { createClickablePill, createPill } from "./pill.js";
import { createConnectionDot } from "./connectionPopup.js";

const W = 384, H = Math.trunc(384 * 1.414);

function methodRow(method, filters) {
  const row = el("div", { className: "detail-method-row" }, [
    createPill(method.name, "pill-method"),
  ]);

  // Красный — исходящие вызовы метода, зелёный — входящие. Каждый виден
  // только пока включён его фильтр — как и на карточках в сетке.
  if (filters.has("outgoing") && method.depCount > 0) {
    row.append(createConnectionDot(method.depCount, "var(--badge-red)", method.deps, false));
  }
  if (filters.has("incoming") && method.incoming.length > 0) {
    row.append(createConnectionDot(method.incoming.length, "var(--pill-name)", method.incoming, true));
  }
  return row;
}

export function openScriptDetailDialog(script, activeFilters) {
  const filters = activeFilters || new Set();
  const dialog = createBaseDialog(W, H);

  const namePill = createClickablePill(script.className, "pill-name", () => {
    navigator.clipboard.writeText(script.filePath);
  });
  namePill.title = script.filePath;

  const nameRow = el("div", { className: "detail-name-row", style: { padding: "20px 20px 8px" } }, [namePill]);

  const methods = el("div", { className: "detail-methods" });
  if (!script.methods.length) {
    methods.append(el("span", { className: "empty-label", text: "Нет методов" }));
  } else {
    for (const m of script.methods) methods.append(methodRow(m, filters));
  }

  dialog.frame.append(nameRow, methods);
  return dialog;
}
