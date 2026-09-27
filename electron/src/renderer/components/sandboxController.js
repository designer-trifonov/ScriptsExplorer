"use strict";
/**
 * Оркестратор режима песочницы — порт ui/sandbox_controller.py.
 *
 * Единственное место, которое знает и про данные (sandboxStore и
 * остальные data/sandbox_*), и про визуал (sandboxCanvas, sandboxBoxView,
 * draggableScriptCard) одновременно. При включении режима подгружает
 * сохранённую сессию проекта в холст; при любом изменении (создание/
 * перетаскивание песочницы, перетаскивание скрипта) — пересчитывает
 * раскладку и сохраняет сессию обратно.
 */
import { el } from "./dom.js";
import { createSandboxCanvas } from "./sandboxCanvas.js";
import { createSandboxBoxView } from "./sandboxBoxView.js";
import { makeDraggable } from "./draggableBehavior.js";
import { bringToFrontOnClick } from "./bringToFront.js";
import { makeCardDraggable } from "./draggableScriptCard.js";
import { handleDrop } from "./sandboxDropHandler.js";
import { createScriptCellView, badgeFlags, CELL_W, CELL_H } from "./scriptCellView.js";
import { prioritizeSandboxes } from "./sandboxBoxLayout.js";
import { gridPack } from "./gridPack.js";
import { ensureBackground, backgroundFor, ROOT_BACKGROUND } from "./sandboxBackground.js";
import { SANDBOX_MARGIN } from "./sandboxLayoutConstants.js";
import { scaleForDepth } from "./sandboxScale.js";
import { watchElementResize } from "./watchElementResize.js";

const ROOT_SIZE = [900, 620];
const ROOT_ID = "root";
const ROOT_COLOR = "#000000";
// Слот сетки = ровно сама карточка, БЕЗ отступа — элементы сетки идут
// впритык друг к другу (см. gridPack: gap=0), единственный отступ
// (SANDBOX_MARGIN) — это отступ от границы песочницы до сетки целиком, а
// не зазор между её ячейками. SLOT_W/SLOT_H — базовый (глубина 0, масштаб 1)
// юнит, которым requiredSize (shared/data/sandboxAutosize.js) выравнивает
// размер песочницы; requiredSize сам не хранит эти числа — на любой глубине
// вложенности мы передаём ему slotW/slotH/margin, уже домноженные на
// scaleForDepth(depth), так что физически константа ровно одна (здесь).
const SLOT_W = CELL_W;
const SLOT_H = CELL_H;

export function createSandboxController() {
  const canvas = createSandboxCanvas();
  let projectPath = null;
  let session = null;
  let scriptsByPath = new Map();
  const boxById = new Map();
  const cardByPath = new Map();
  // Песочница, в которую попадёт следующая созданная песочница. По умолчанию —
  // корень (основное "облако"); клик по любой песочнице (см. buildBox)
  // переключает активную на неё, вне зависимости от глубины вложенности.
  let activeId = ROOT_ID;

  // Холст должен реагировать на изменение размера окна (развернули,
  // потянули за край) — раскладка иначе считается один раз и застывает.
  // Реакция и сам пересчёт — раздельные ответственности: watchElementResize
  // ничего не знает про песочницы, а rebuild() ничего не знает про resize.
  watchElementResize(canvas.element, () => rebuild());

  // ── включение режима песочницы для конкретного проекта ────────────
  async function activate(newProjectPath, scripts) {
    projectPath = newProjectPath;
    scriptsByPath = new Map(scripts.map((s) => [s.filePath, s]));
    boxById.clear();
    cardByPath.clear();
    activeId = ROOT_ID; // по умолчанию активна основная (корневая) песочница

    let newSession = await window.scriptExplorer.sandbox.load(projectPath);
    if (newSession === null) {
      newSession = {
        root: {
          id: ROOT_ID, name: "Все скрипты", borderColor: ROOT_COLOR,
          backgroundColor: ROOT_BACKGROUND, x: 0, y: 0,
          width: ROOT_SIZE[0], height: ROOT_SIZE[1], manuallyPositioned: true,
          draggable: false, scriptPaths: [...scriptsByPath.keys()], children: [],
        },
        looseScripts: {},
      };
    } else {
      // Корень — всегда один, чёрный, неподвижный, со сплошным фоном
      // (в т.ч. чинит старые сессии, где эти поля были другими/пустыми).
      newSession.root.backgroundColor = ROOT_BACKGROUND;
      newSession.root.borderColor = ROOT_COLOR;
      newSession.root.draggable = false;
    }

    session = newSession;
    syncNewScripts();
    rebuild();
  }

  // ── создать новую песочницу внутри указанной (по умолчанию — внутри
  // активной, см. setActive; изначально активна корневая) ────────────
  // Единственный способ появления песочницы — явный вызов отсюда (кнопка
  // "Создать песочницу" с именем и цветом от пользователя). Никакого
  // автосоздания по двойному клику или дефолтных цветов по кругу.
  function addSandbox(name, color, parentId = activeId) {
    if (!session) return;
    const parent = findNode(session.root, parentId) || session.root;
    const existing = parent.children.map((c) => [c.x, c.y, c.width, c.height]);
    // Дефолтный размер и шаг размещения — ровно один слот сетки основной
    // песочницы (SLOT_W x SLOT_H, глубина 0/масштаб 1), как и у слота
    // скрипта: своей отдельной геометрии у новой песочницы нет. Реальный
    // размер тут же переопределит requiredSize в buildBox под её содержимое
    // и фактическую глубину/масштаб — это лишь стартовая точка.
    const [x, y] = window.scriptExplorer.sandbox.nextPosition(existing, SLOT_W, SLOT_H, SANDBOX_MARGIN);
    const node = {
      id: Math.random().toString(16).slice(2, 10), name,
      borderColor: color, backgroundColor: backgroundFor(color, false), x, y, width: SLOT_W, height: SLOT_H,
      manuallyPositioned: false, draggable: true, scriptPaths: [], children: [],
    };
    parent.children.push(node);
    rebuild();
    save();
  }

  // ── какая песочница сейчас активна (цель для addSandbox) ───────────
  function setActive(nodeId) {
    if (activeId === nodeId) return;
    const prevBox = boxById.get(activeId);
    if (prevBox) prevBox.element.classList.remove("sandbox-box--active");
    activeId = nodeId;
    const nextBox = boxById.get(activeId);
    if (nextBox) nextBox.element.classList.add("sandbox-box--active");
  }

  // ── построение всего визуального дерева из модели ──────────────────
  function rebuild() {
    if (!session) return;
    boxById.clear();
    cardByPath.clear();
    const rootBox = buildBox(session.root, null);
    canvas.setRoot(rootBox);
  }

  // parentScale — масштаб сетки РОДИТЕЛЯ этого узла (т.е. тот scale, которым
  // размечены соседние карточки/песочницы, среди которых этот box лежит).
  // Отдельно от собственного scale узла (который красит его же содержимое)
  // — иначе пустая/новая вложенная песочница мерилась бы своей же, более
  // мелкой от вложенности сеткой и не совпадала бы по размеру с соседней
  // ячейкой скрипта на одном с ней уровне (баг: сетка "плыла").
  function buildBox(node, parentContent, depth = 0, parentScale = 1) {
    const isRoot = parentContent === null;
    // Единственное место, где вложенность превращается в масштаб — дальше
    // по всей функции это просто число, домножающее обычные CELL_W/CELL_H/
    // SANDBOX_MARGIN/SLOT_W/SLOT_H. Корень не масштабируется (scale===1),
    // каждый следующий уровень вложенности — рекурсивно меньше на тот же
    // множитель (см. sandboxScale.js).
    const scale = scaleForDepth(depth);
    ensureBackground(node, isRoot);
    const box = createSandboxBoxView(node.id, node.name, node.borderColor, node.backgroundColor, scale);
    if (!isRoot) {
      // Вложенная песочница — абсолютно спозиционирована внутри родителя.
      box.element.style.position = "absolute";
      box.element.style.left = `${node.x}px`;
      box.element.style.top = `${node.y}px`;
      parentContent.append(box.element);
    } else {
      // Корень — ровно один, всегда заполняет собой весь холст целиком
      // (статичный, не таскается — x/y модели ему не нужны).
      box.element.style.position = "relative";
      box.fill();
    }
    boxById.set(node.id, box);
    box.element.dataset.draggable = String(!!node.draggable);
    if (node.id === activeId) box.element.classList.add("sandbox-box--active");

    // Клик по песочнице (в т.ч. по любому её содержимому — скрипту или
    // вложенной песочнице, которая сама не перехватила клик раньше) делает
    // её активной целью для addSandbox. stopPropagation — чтобы клик по
    // вложенной песочнице не "протекал" наверх и не переактивировал её
    // родителя: активной становится самая глубокая из кликнутых.
    box.element.addEventListener("mousedown", (e) => {
      e.stopPropagation();
      setActive(node.id);
    });

    if (node.draggable) {
      makeDraggable(box.element, (clientX, clientY) => onBoxDropped(node, box, clientX, clientY));
      bringToFrontOnClick(box.element);
    }

    // Песочницы получают место первыми (упорядочены отдельной формулой —
    // самая крупная первой), но скрипты не ждут своей отдельной секции
    // снизу: они ищут любое свободное место adaptively — в том числе
    // справа от узкой песочницы, если она не на всю ширину контейнера.
    // Одна общая skyline-упаковка вместо двух раздельных "ярусов" (раньше
    // это оставляло пустым весь свободный верхний ряд справа от песочницы).
    const autoBoxes = []; // {key, node, w, h}
    for (const child of node.children) {
      const childBox = buildBox(child, box.content, depth + 1, scale);
      if (child.manuallyPositioned) {
        childBox.element.style.left = `${child.x}px`;
        childBox.element.style.top = `${child.y}px`;
      } else {
        autoBoxes.push({
          key: `box:${child.id}`, node: child,
          w: childBox.width || child.width,
          h: childBox.height || child.height,
        });
      }
    }

    const looseHere = Object.fromEntries(
      Object.entries(session.looseScripts).filter(([p]) => node.scriptPaths.includes(p))
    );
    const autoCards = []; // {key, path, w, h}
    for (const path of node.scriptPaths) {
      const card = makeCard(path, box.content, scale);
      if (!card) continue;
      if (path in looseHere) {
        card.style.position = "absolute";
        card.style.left = `${looseHere[path][0]}px`;
        card.style.top = `${looseHere[path][1]}px`;
      } else {
        autoCards.push({ key: `card:${path}`, path, w: CELL_W * scale, h: CELL_H * scale });
      }
    }

    // Число колонок: у корня — сколько реально влезает по ширине холста в
    // DOM (он заполняет контейнер целиком). У вложенной песочницы брать её
    // ТЕКУЩУЮ node.width нельзя — это замкнутый круг: ширина уже посчитана
    // под МЕНЬШЕЕ число элементов (например, под один-единственный первый
    // файл), значит колонка ровно одна, значит второй/третий файл может
    // только уйти вниз тем же единственным столбцом, и песочница никогда
    // не расширится вширь. Вместо этого считаем от количества элементов —
    // примерно квадратная сетка (⌈√N⌉ колонок): 1 элемент — 1 колонка (по
    // центру), 2–4 — уже 2 колонки, 5–9 — уже 3, и так далее.
    //
    // Считаем целое число колонок ОДИН раз здесь и передаём его в gridPack
    // напрямую (а не ширину в пикселях, которую пришлось бы делить внутри
    // ещё раз) — деление на глубокой вложенности из-за погрешности чисел с
    // плавающей запятой иногда давало, например, 2.9999999999996 вместо
    // ровно 3, и Math.floor срезал целую колонку.
    const itemCount = autoBoxes.length + autoCards.length;
    const unitW = SLOT_W * scale;
    const cols = isRoot
      ? Math.max(1, Math.floor((Math.max(canvas.element.clientWidth, SLOT_W) - SANDBOX_MARGIN * scale * 2) / unitW))
      : Math.max(1, Math.ceil(Math.sqrt(itemCount)));

    const orderedBoxes = prioritizeSandboxes(autoBoxes);
    const combined = [...orderedBoxes, ...autoCards];
    // padding — только от края песочницы до сетки; gap=0 — сами карточки/
    // песочницы внутри идут впритык друг к другу, без зазора между ними.
    const { positions } = gridPack(combined, cols, SANDBOX_MARGIN * scale, 0, unitW, SLOT_H * scale);

    const byKey = new Map(combined.map((it) => [it.key, it]));
    const placedRects = [];
    for (const { key, x, y } of positions) {
      const item = byKey.get(key);
      if (key.startsWith("box:")) {
        boxById.get(item.node.id).element.style.left = `${x}px`;
        boxById.get(item.node.id).element.style.top = `${y}px`;
      } else {
        const c = cardByPath.get(item.path);
        c.style.position = "absolute";
        c.style.left = `${x}px`;
        c.style.top = `${y}px`;
      }
      placedRects.push([x, y, item.w, item.h]);
    }

    // ручные элементы тоже учитываем в размере, чтобы песочница не обрезала их
    for (const child of node.children) {
      if (child.manuallyPositioned) placedRects.push([child.x, child.y, child.width, child.height]);
    }
    for (const [, pos] of Object.entries(looseHere)) {
      placedRects.push([pos[0], pos[1], CELL_W, 90]);
    }

    if (!isRoot) {
      // Размер по содержимому — считается в СОБСТВЕННОЙ сетке узла (scale),
      // как и раньше: requiredSize возвращает минимум "один свой слот" для
      // пустой песочницы. node.width/height НЕ используются как пол поверх
      // этого — иначе устаревшее значение с момента создания держало бы
      // песочницу шире/больше, чем реально нужно её содержимому.
      const [contentW, contentH] = window.scriptExplorer.sandbox.requiredSize(
        placedRects, SLOT_W * scale, SLOT_H * scale, SANDBOX_MARGIN * scale
      );
      // Но САМ box — это элемент сетки РОДИТЕЛЯ (лежит вперемешку с его
      // карточками скриптов и другими песочницами), поэтому его внешний
      // футпринт обязан быть кратен родительскому слоту — иначе пустая
      // песочница (у которой contentW/H меньше родительского слота из-за
      // более мелкого собственного масштаба) окажется чуть уже/ниже соседней
      // карточки скрипта и сдвинет всю раскладку. Округляем ВВЕРХ до целого
      // числа родительских слотов — если содержимое (уже вместе с отступами,
      // см. requiredSize) не влезает в текущее число слотов по ширине или
      // высоте, песочница обязана вырасти ещё на слот именно по той оси, где
      // не хватает места — отступы никогда не ужимаются ради "влезания".
      const parentSlotW = SLOT_W * parentScale, parentSlotH = SLOT_H * parentScale;
      const reqW = Math.ceil(contentW / parentSlotW) * parentSlotW;
      const reqH = Math.ceil(contentH / parentSlotH) * parentSlotH;
      box.setSize(reqW, reqH);

      // requiredSize уже включает отступ со всех четырёх сторон (contentW/H
      // = сетка + margin*2) — но округление ШИРИНЫ до целого числа
      // родительских слотов выше может оставить ЕЩЁ немного лишнего места
      // по горизонтали (когда reqW больше, чем строго нужно). Это лишнее
      // делим поровну между левым и правым отступом — тогда левый и правый
      // отступы остаются равными друг другу (а не "весь запас справа").
      // По вертикали НЕ центрируем: привязка к верхнему краю, единственный
      // (обычный) отступ сверху — весь лишний запас по высоте остаётся
      // снизу, ничего не сдвигаем вниз лишний раз.
      const shiftX = (reqW - contentW) / 2;
      const shiftY = 0;
      if (shiftX !== 0 || shiftY !== 0) {
        for (const { key } of positions) {
          const item = byKey.get(key);
          const target = key.startsWith("box:") ? boxById.get(item.node.id).element : cardByPath.get(item.path);
          target.style.left = `${parseFloat(target.style.left) + shiftX}px`;
          target.style.top = `${parseFloat(target.style.top) + shiftY}px`;
        }
      }
    }
    return box;
  }

  function makeCard(path, parentContent, scale = 1) {
    const script = scriptsByPath.get(path);
    if (!script) return null;
    // В песочнице карточка всегда без фильтров-бейджей — так же, как в
    // Python-версии (ScriptCellView(script) без badges).
    const cell = createScriptCellView(script, badgeFlags(), null);
    // Сама карточка/подпись рисуются в своём обычном (немасштабированном)
    // размере — тем же кодом, что и на глубине 0 — а видимую уменьшенную
    // версию для вложенной песочницы даёт один-единственный CSS transform.
    // Раскладка (slot ниже) уже размерена под итоговый, уменьшенный
    // отпечаток, поэтому визуально карточка остаётся точно внутри своего
    // слота на любой глубине вложенности.
    cell.style.transform = `scale(${scale})`;
    cell.style.transformOrigin = "center center";

    // Видимая граница слота — ровно тот прямоугольник, которым карточка
    // реально владеет в раскладке (SLOT_W x SLOT_H === CELL_W x CELL_H,
    // без отступа). Слоты соседних карточек примыкают друг к другу впритык
    // (gap=0 в gridPack) — вместе они и есть та самая сетка (уменьшенная
    // по той же формуле, что и сама карточка).
    const slot = el("div", {
      className: "script-slot",
      style: { width: `${SLOT_W * scale}px`, height: `${SLOT_H * scale}px`, position: "absolute" },
    }, [cell]);

    parentContent.append(slot);
    makeCardDraggable(slot, (clientX, clientY) => onCardDropped(path, slot, clientX, clientY));
    cardByPath.set(path, slot);
    return slot;
  }

  // ── реакция на отпускание перетаскиваемой песочницы ────────────────
  function onBoxDropped(node, box, clientX, clientY) {
    if (node.id === ROOT_ID) return;
    const candidates = [...boxById.values()].filter((b) => b !== box);
    const target = handleDrop(box, clientX, clientY, candidates);
    if (target && target.nodeId !== node.id) {
      moveNodeInto(node, target.nodeId);
    } else {
      node.x = parseFloat(box.element.style.left) || 0;
      node.y = parseFloat(box.element.style.top) || 0;
      node.manuallyPositioned = true;
    }
    rebuild();
    save();
  }

  // ── реакция на отпускание перетаскиваемого скрипта ─────────────────
  function onCardDropped(path, card, clientX, clientY) {
    const candidates = [...boxById.values()];
    const target = handleDrop({ element: card }, clientX, clientY, candidates);

    removeScriptEverywhere(session.root, path);
    delete session.looseScripts[path];

    if (target) {
      const targetNode = findNode(session.root, target.nodeId);
      if (targetNode) targetNode.scriptPaths.unshift(path);
    } else {
      const pos = [parseFloat(card.style.left) || 0, parseFloat(card.style.top) || 0];
      session.root.scriptPaths.push(path);
      session.looseScripts[path] = pos;
    }

    rebuild();
    save();
  }

  // ── операции над деревом модели ────────────────────────────────────
  function moveNodeInto(node, targetId) {
    removeNode(session.root, node.id);
    const targetNode = findNode(session.root, targetId);
    if (targetNode) {
      node.manuallyPositioned = false;
      targetNode.children.unshift(node);
    } else {
      session.root.children.push(node);
    }
  }

  function removeNode(root, nodeId) {
    root.children = root.children.filter((c) => c.id !== nodeId);
    for (const c of root.children) removeNode(c, nodeId);
  }

  function findNode(root, nodeId) {
    if (root.id === nodeId) return root;
    for (const c of root.children) {
      const found = findNode(c, nodeId);
      if (found) return found;
    }
    return null;
  }

  function removeScriptEverywhere(node, path) {
    const i = node.scriptPaths.indexOf(path);
    if (i !== -1) node.scriptPaths.splice(i, 1);
    for (const c of node.children) removeScriptEverywhere(c, path);
  }

  function syncNewScripts() {
    const known = collectPaths(session.root);
    for (const path of scriptsByPath.keys()) {
      if (!known.has(path)) session.root.scriptPaths.push(path);
    }
  }

  function collectPaths(node) {
    const paths = new Set(node.scriptPaths);
    for (const c of node.children) for (const p of collectPaths(c)) paths.add(p);
    return paths;
  }

  function save() {
    if (projectPath && session) {
      window.scriptExplorer.sandbox.save(projectPath, session).catch((e) => console.error("sandbox save failed", e));
    }
  }

  return { canvas: () => canvas.element, activate, addSandbox };
}
