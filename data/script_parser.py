import logging
import os
import re
from data.models import MethodInfo, ScriptInfo
from data.antipattern_checker import find_antipatterns
from data.method_calls import find_calls
from data.method_finder import find_methods

logger = logging.getLogger(__name__)

_CLASS_RE      = re.compile(r'\b(?:class|struct|interface|enum|record)\s+(\w+)')
_CLASS_DECL_RE = re.compile(r'\b(?:class|struct)\s+\w+[^:]*:\s*([\w\s,<>]+?)(?:\s*\{)', re.MULTILINE)
_MONO_BASES    = {"MonoBehaviour", "NetworkBehaviour", "ScriptableObject",
                  "Editor", "EditorWindow", "PropertyDrawer"}

_TYPE_RE = re.compile(r'\b([A-Z][a-zA-Z0-9_]*)\b')

_COMMENT_RE = re.compile(r'//[^\n]*|/\*.*?\*/', re.DOTALL)


def _strip_comments(src: str) -> str:
    """Заменяет содержимое комментариев пробелами, сохраняя длину и переносы строк,
    чтобы позиции символов (скобки, номера строк) не сдвигались."""
    return _COMMENT_RE.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), src)


def _find_deps(body: str, own: str, project_classes: set) -> list[str]:
    found = set()
    for m in _TYPE_RE.finditer(body):
        name = m.group(1)
        if name != own and name in project_classes:
            found.add(name)
    return sorted(found)


def collect_class_names(paths: list) -> set:
    names = set()
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                src = f.read()
            m = _CLASS_RE.search(_strip_comments(src))
            if m:
                names.add(m.group(1))
        except OSError as e:
            logger.warning("Не удалось прочитать файл %s: %s", path, e)
    return names


def parse_file(path: str, project_classes: set = None) -> ScriptInfo:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()
    src = _strip_comments(src)

    cm = _CLASS_RE.search(src)
    class_name = cm.group(1) if cm else os.path.splitext(os.path.basename(path))[0]

    is_mono      = False
    project_bases: list[str] = []
    decl = _CLASS_DECL_RE.search(src)
    if decl:
        raw = {b.strip().split('<')[0] for b in decl.group(1).split(',')}
        is_mono = bool(raw & _MONO_BASES)
        # базовые классы из проекта (не Unity-built-ins)
        pc = project_classes or set()
        project_bases = sorted(b for b in raw if b in pc)

    info = ScriptInfo(
        class_name=class_name,
        file_path=path,
        is_mono=is_mono,
        bases=project_bases,
    )
    seen = set()

    def _add(method_name: str, body: str):
        if method_name == class_name or method_name in seen:
            return
        seen.add(method_name)
        deps         = _find_deps(body, class_name, project_classes or set())
        antipatterns = find_antipatterns(body)
        calls        = find_calls(body)
        info.methods.append(MethodInfo(
            name=method_name,
            dep_count=len(deps),
            deps=deps,
            antipatterns=antipatterns,
            calls=calls,
        ))

    for method_name, body in find_methods(src):
        _add(method_name, body)

    # Типы упомянутые вне тел методов (поля, инициализаторы, базовые типы)
    pc = project_classes or set()
    already = {dep for method in info.methods for dep in method.deps}
    info.class_deps = sorted(
        name for name in {m.group(1) for m in _TYPE_RE.finditer(src)}
        if name in pc and name != class_name and name not in already
    )

    return info
