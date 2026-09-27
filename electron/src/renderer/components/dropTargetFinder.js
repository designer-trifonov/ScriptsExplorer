"use strict";
/**
 * По точке (где отпустили мышь) находит, в какую песочницу попали, если
 * попали вообще — порт ui/drop_target_finder.py.
 */
export function findTarget(clientX, clientY, candidateBoxes) {
  const hits = candidateBoxes.filter((b) => {
    const r = b.element.getBoundingClientRect();
    return clientX >= r.left && clientX <= r.right && clientY >= r.top && clientY <= r.bottom;
  });
  if (hits.length === 0) return null;

  // Если точка попала в несколько вложенных друг в друга песочниц —
  // возвращаем самую маленькую по площади (самую "глубокую", внутреннюю).
  return hits.reduce((smallest, b) => {
    const areaB = b.element.offsetWidth * b.element.offsetHeight;
    const areaSmallest = smallest.element.offsetWidth * smallest.element.offsetHeight;
    return areaB < areaSmallest ? b : smallest;
  });
}
