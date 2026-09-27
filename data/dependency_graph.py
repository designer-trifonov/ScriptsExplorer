"""Отвечает только за одно: построить обратный индекс зависимостей —
кто из скриптов проекта ссылается на данный класс (через методы, поля
или наследование) — и записать его в ScriptInfo.incoming.
"""
from data.models import ScriptInfo


def attach_incoming(scripts: list[ScriptInfo]) -> None:
    """Заполняет script.incoming для каждого скрипта в списке."""
    incoming: dict[str, list[str]] = {s.class_name: [] for s in scripts}

    for script in scripts:
        for method in script.methods:
            for dep in method.deps:
                if dep in incoming and script.class_name not in incoming[dep]:
                    incoming[dep].append(script.class_name)
        for base in script.bases:
            if base in incoming and script.class_name not in incoming[base]:
                incoming[base].append(script.class_name)
        for dep in script.class_deps:
            if dep in incoming and script.class_name not in incoming[dep]:
                incoming[dep].append(script.class_name)

    for script in scripts:
        script.incoming = sorted(incoming.get(script.class_name, []))
