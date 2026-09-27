"use strict";
/**
 * Раскладывает элементы по сетке строго слева направо, потом сверху вниз —
 * как обычная таблица: первый элемент занимает первую свободную клетку,
 * следующий — следующую в том же ряду, и так до конца ряда, потом перенос
 * на следующий ряд. Заменяет собой более "умную" skyline-упаковку (которая
 * искала любое ближайшее свободное место и из-за этого порядок заполнения
 * был не всегда предсказуем) — здесь порядок заполнения первичен, а не
 * плотность упаковки.
 *
 * Все элементы на одной глубине вложенности кратны одному и тому же юниту
 * (unitW x unitH — размер ячейки/скрипта на этой глубине, см.
 * sandboxController.js: и карточки, и вложенные песочницы после авторазмера
 * всегда получаются целым числом таких юнитов), поэтому раскладку можно
 * вести по обычной целочисленной сетке колонок/рядов, а не по пикселям —
 * число колонок вызывающая сторона тоже считает в целых числах (см. cols).
 *
 * items — [{key, w, h}, ...] в порядке заполнения (кто раньше в списке —
 * тот раньше получает клетку). cols — число колонок сетки, УЖЕ решённое
 * вызывающей стороной (а не ширина в пикселях, из которой это число нужно
 * было бы заново вычислять здесь делением — на глубокой вложенности из-за
 * погрешности чисел с плавающей запятой такое деление иногда давало
 * 2.9999999999996 вместо ровно 3, и Math.floor срезал целую колонку).
 * padding — отступ от краёв контейнера до сетки. gap — зазор между
 * соседними ячейками сетки (0 — впритык).
 * Возвращает { positions: [{key, x, y}, ...], bottom }.
 */
export function gridPack(items, cols, padding, gap, unitW, unitH) {
  const stepW = unitW + gap, stepH = unitH + gap;
  cols = Math.max(1, cols);

  const occupied = new Set(); // "row,col"
  const fits = (row, col, colsSpan, rowsSpan) => {
    if (col + colsSpan > cols) return false;
    for (let r = row; r < row + rowsSpan; r++) {
      for (let c = col; c < col + colsSpan; c++) {
        if (occupied.has(`${r},${c}`)) return false;
      }
    }
    return true;
  };

  const positions = [];
  let maxRow = 0;

  for (const item of items) {
    const colsSpan = Math.max(1, Math.round(item.w / unitW));
    const rowsSpan = Math.max(1, Math.round(item.h / unitH));

    let row = 0;
    let placed = false;
    while (!placed) {
      for (let col = 0; col <= cols - colsSpan; col++) {
        if (fits(row, col, colsSpan, rowsSpan)) {
          for (let r = row; r < row + rowsSpan; r++) {
            for (let c = col; c < col + colsSpan; c++) occupied.add(`${r},${c}`);
          }
          positions.push({ key: item.key, x: padding + col * stepW, y: padding + row * stepH });
          maxRow = Math.max(maxRow, row + rowsSpan);
          placed = true;
          break;
        }
      }
      row++;
    }
  }

  const bottom = positions.length > 0 ? padding + maxRow * stepH - gap : padding;
  return { positions, bottom };
}
