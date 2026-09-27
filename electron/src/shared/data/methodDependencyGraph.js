"use strict";
/**
 * Отвечает только за одно: построить обратный индекс вызовов методов —
 * какие методы проекта вызывают данный метод — и записать его в
 * MethodInfo.incoming. Порт data/method_dependency_graph.py.
 *
 * Приближённый анализ по совпадению имени метода, а не полноценный
 * резолвинг типов: два разных класса с методом одного имени будут
 * перепутаны — так же, как и в оригинале.
 */
function attachMethodIncoming(scripts) {
  // индекс: имя метода -> список его определений (класс, сам метод)
  const definers = new Map();
  for (const script of scripts) {
    for (const method of script.methods) {
      if (!definers.has(method.name)) definers.set(method.name, []);
      definers.get(method.name).push([script.className, method]);
    }
  }

  for (const script of scripts) {
    for (const method of script.methods) {
      for (const calledName of method.calls) {
        for (const [ownerClass, targetMethod] of definers.get(calledName) || []) {
          if (ownerClass === script.className) continue; // вызов внутри своего же класса не считаем
          const callerLabel = `${script.className}.${method.name}`;
          if (!targetMethod.incoming.includes(callerLabel)) {
            targetMethod.incoming.push(callerLabel);
          }
        }
      }
    }
  }
}

module.exports = { attachMethodIncoming };
