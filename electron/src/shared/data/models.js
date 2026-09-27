"use strict";
/**
 * Порт data/models.py. Классы вместо dataclass — вычисляемые поля
 * (total_deps, is_refactor, ...) остаются геттерами, как @property в Python.
 */
const { REFACTOR_THRESHOLD } = require("../config");
const { LIFECYCLE_METHODS } = require("./lifecycle");

class MethodInfo {
  constructor({ name, depCount, deps = [], antipatterns = [], calls = [], incoming = [] }) {
    this.name = name;
    this.depCount = depCount;
    this.deps = deps;
    this.antipatterns = antipatterns;
    this.calls = calls;          // имена вызываемых методов (для поиска входящих)
    this.incoming = incoming;    // "Класс.Метод", которые вызывают этот метод
  }
}

class ScriptInfo {
  constructor({ className, filePath, methods = [], incoming = [], bases = [],
                classDeps = [], isMono = false, isDead = false }) {
    this.className = className;
    this.filePath = filePath;
    this.methods = methods;
    this.incoming = incoming;
    this.bases = bases;         // базовые классы из проекта
    this.classDeps = classDeps; // типы в полях/вне методов
    this.isMono = isMono;
    this.isDead = isDead;
  }

  get totalDeps() {
    return this.methods.reduce((sum, m) => sum + m.depCount, 0);
  }

  /** Единственное место, решающее, пора ли скрипту на рефакторинг. */
  get isRefactor() {
    return this.methods.length >= REFACTOR_THRESHOLD;
  }

  /** Сколько методов скрипта — Unity lifecycle-методы (Awake/Start/OnEnable). */
  get lifecycleCount() {
    return this.methods.filter((m) => LIFECYCLE_METHODS.has(m.name)).length;
  }

  get totalAntipatterns() {
    const found = new Set();
    for (const m of this.methods) for (const a of m.antipatterns) found.add(a);
    return found.size;
  }

  /** Все скрипты проекта, от которых зависит этот скрипт (методы + поля + база). */
  get allDeps() {
    const found = new Set();
    for (const m of this.methods) for (const d of m.deps) found.add(d);
    for (const d of this.classDeps) found.add(d);
    for (const b of this.bases) found.add(b);
    found.delete(this.className);
    return [...found].sort();
  }

  /**
   * IPC (ipcRenderer.invoke) клонирует возвращаемые значения через
   * Structured Clone, который копирует только собственные свойства —
   * геттеры класса (totalDeps, isRefactor, ...) теряются. Явный toJSON()
   * решает это: JSON.parse(JSON.stringify(scripts)) на main-стороне
   * материализует геттеры в обычные поля перед отправкой в renderer.
   */
  toJSON() {
    return {
      className: this.className,
      filePath: this.filePath,
      methods: this.methods,
      incoming: this.incoming,
      bases: this.bases,
      classDeps: this.classDeps,
      isMono: this.isMono,
      isDead: this.isDead,
      totalDeps: this.totalDeps,
      isRefactor: this.isRefactor,
      lifecycleCount: this.lifecycleCount,
      totalAntipatterns: this.totalAntipatterns,
      allDeps: this.allDeps,
    };
  }
}

module.exports = { MethodInfo, ScriptInfo };
