"""Отвечает только за одно: построить обратный индекс вызовов методов —
какие методы проекта вызывают данный метод — и записать его в
MethodInfo.incoming.

Это приближённый анализ по совпадению имени метода (как и весь
остальной разбор в script_parser), а не полноценный резолвинг типов:
два разных класса с методом одного имени будут перепутаны.
"""
from data.models import ScriptInfo


def attach_method_incoming(scripts: list[ScriptInfo]) -> None:
    # индекс: имя метода -> список его определений (класс, сам метод)
    definers: dict[str, list[tuple]] = {}
    for script in scripts:
        for method in script.methods:
            definers.setdefault(method.name, []).append((script.class_name, method))

    for script in scripts:
        for method in script.methods:
            for called_name in method.calls:
                for owner_class, target_method in definers.get(called_name, []):
                    if owner_class == script.class_name:
                        continue   # вызов внутри своего же класса не считаем
                    caller_label = f"{script.class_name}.{method.name}"
                    if caller_label not in target_method.incoming:
                        target_method.incoming.append(caller_label)
