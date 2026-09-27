from dataclasses import dataclass, field

from data.config import REFACTOR_THRESHOLD
from data.lifecycle import LIFECYCLE_METHODS


@dataclass
class MethodInfo:
    name:         str
    dep_count:    int
    deps:         list[str] = field(default_factory=list)
    antipatterns: list[str] = field(default_factory=list)
    calls:        list[str] = field(default_factory=list)   # имена вызываемых методов (для поиска входящих)
    incoming:     list[str] = field(default_factory=list)   # "Класс.Метод", которые вызывают этот метод


@dataclass
class ScriptInfo:
    class_name: str
    file_path:  str
    methods:    list[MethodInfo] = field(default_factory=list)
    incoming:   list[str]        = field(default_factory=list)
    bases:      list[str]        = field(default_factory=list)   # базовые классы из проекта
    class_deps: list[str]        = field(default_factory=list)   # типы в полях/вне методов
    is_mono:    bool             = False
    is_dead:    bool             = False

    @property
    def total_deps(self) -> int:
        return sum(m.dep_count for m in self.methods)

    @property
    def is_refactor(self) -> bool:
        """Единственное место, решающее, пора ли скрипту на рефакторинг."""
        return len(self.methods) >= REFACTOR_THRESHOLD

    @property
    def lifecycle_count(self) -> int:
        """Сколько методов скрипта — Unity lifecycle-методы (Awake/Start/OnEnable)."""
        return sum(1 for m in self.methods if m.name in LIFECYCLE_METHODS)

    @property
    def total_antipatterns(self) -> int:
        found = set()
        for m in self.methods:
            found.update(m.antipatterns)
        return len(found)

    @property
    def all_deps(self) -> list[str]:
        """Все скрипты проекта, от которых зависит этот скрипт (методы + поля + база)."""
        found = set()
        for m in self.methods:
            found.update(m.deps)
        found.update(self.class_deps)
        found.update(self.bases)
        found.discard(self.class_name)
        return sorted(found)
