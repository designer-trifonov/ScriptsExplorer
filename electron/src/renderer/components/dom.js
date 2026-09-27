"use strict";
/** Общий хелпер создания элементов — тот же приём, что в PromptBlocks. */
export function el(tag, opts = {}, children = []) {
  const e = document.createElement(tag);
  if (opts.className) e.className = opts.className;
  if (opts.text != null) e.textContent = opts.text;
  if (opts.attrs) for (const [k, v] of Object.entries(opts.attrs)) e.setAttribute(k, v);
  if (opts.style) Object.assign(e.style, opts.style);
  if (opts.onClick) e.addEventListener("click", opts.onClick);
  for (const c of children) e.append(c);
  return e;
}
