"use strict";
/**
 * Считает, куда встаёт новая песочница при создании — по сетке, в первое
 * свободное от других песочниц того же уровня место. Порт
 * data/sandbox_new_position.py.
 */
const { getLogger } = require("../../main/logger");

const logger = getLogger("sandboxNewPosition");

const MAX_COLS = 6;

function _overlaps(a, b) {
  const [ax, ay, aw, ah] = a;
  const [bx, by, bw, bh] = b;
  return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
}

/**
 * existingRects — [[x, y, w, h], ...] уже занятых мест того же уровня.
 * slotW/slotH/margin приходят от вызывающего (тот же слот сетки, что и
 * requiredSize) — этот модуль, как и sandboxAutosize.js, не хранит
 * собственную геометрию, а раскладывает то, что ему передали.
 */
function nextPosition(existingRects, slotW, slotH, margin) {
  let col = 0, row = 0;
  for (;;) {
    const x = margin + col * (slotW + margin);
    const y = margin + row * (slotH + margin);
    const candidate = [x, y, slotW, slotH];
    if (!existingRects.some((r) => _overlaps(candidate, r))) {
      logger.info(`Новая песочница встанет в (${x}, ${y})`);
      return [x, y];
    }
    col += 1;
    if (col >= MAX_COLS) {
      col = 0;
      row += 1;
    }
  }
}

module.exports = { nextPosition };
