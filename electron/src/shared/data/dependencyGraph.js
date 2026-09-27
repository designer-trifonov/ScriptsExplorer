"use strict";
/**
 * Отвечает только за одно: построить обратный индекс зависимостей —
 * кто из скриптов проекта ссылается на данный класс (через методы, поля
 * или наследование) — и записать его в ScriptInfo.incoming.
 * Порт data/dependency_graph.py.
 */
function attachIncoming(scripts) {
  const incoming = new Map(scripts.map((s) => [s.className, []]));

  const addRef = (dep, fromClass) => {
    const list = incoming.get(dep);
    if (list && !list.includes(fromClass)) list.push(fromClass);
  };

  for (const script of scripts) {
    for (const method of script.methods) {
      for (const dep of method.deps) addRef(dep, script.className);
    }
    for (const base of script.bases) addRef(base, script.className);
    for (const dep of script.classDeps) addRef(dep, script.className);
  }

  for (const script of scripts) {
    script.incoming = (incoming.get(script.className) || []).slice().sort();
  }
}

module.exports = { attachIncoming };
