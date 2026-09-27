"use strict";
/**
 * Диалог сводки — порт ui/summary_dialog.py.
 */
import { el } from "./dom.js";
import { createBaseDialog } from "./baseDialog.js";

const W = 420, H = 560;

const BADGE_COLOR = { dep: "var(--badge-orange)", R: "var(--badge-red)", "!": "var(--badge-red)", D: "var(--badge-dead)" };
const BADGE_LABEL = { dep: "●", R: "R", "!": "!", D: "D" };

function badge(kind) {
  return el("span", {
    className: "summary-badge",
    text: BADGE_LABEL[kind] || "?",
    style: { background: BADGE_COLOR[kind] || "#888" },
  });
}

function scriptBlock(summary) {
  const rows = summary.items.map((item) => el("div", { className: "summary-item__row" }, [
    badge(item.badge),
    el("span", { text: item.text }),
  ]));
  return el("div", { className: "summary-item" }, [
    el("div", { className: "summary-item__name", text: summary.className }),
    ...rows,
  ]);
}

export function openSummaryDialog(summaries, totalScripts) {
  const dialog = createBaseDialog(W, H);

  const head = el("div", { className: "section-label", style: { padding: "20px 20px 8px", fontSize: "10px", fontWeight: "bold" } }, [
    document.createTextNode(`Аудит · ${totalScripts} скриптов · ${summaries.length} с замечаниями`),
  ]);
  const sep = el("hr", { className: "separator" });

  const list = el("div", { className: "summary-list" });
  if (summaries.length === 0) {
    list.append(el("span", { className: "empty-label", text: "Замечаний не найдено" }));
  } else {
    for (const s of summaries) list.append(scriptBlock(s));
  }

  const copyBtn = el("button", { className: "btn-primary", text: "Копировать" });
  copyBtn.addEventListener("click", () => {
    const lines = [];
    for (const s of summaries) {
      lines.push(s.className);
      for (const item of s.items) lines.push(`  [${item.badge}] ${item.text}`);
    }
    navigator.clipboard.writeText(lines.join("\n"));
  });
  const bottom = el("div", { className: "summary-bottom" }, [copyBtn]);

  dialog.frame.append(head, sep, list, bottom);
  return dialog;
}
