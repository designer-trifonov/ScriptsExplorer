"""Отвечает только за одно: надёжно найти методы в C#-исходнике и вернуть
их имя и тело для дальнейшего анализа (зависимости, антипаттерны, вызовы).

Учитывает основные формы объявления метода в C#:
  - обычный: [модификаторы] Тип Имя(параметры) { ... }
  - без модификатора доступа (по умолчанию private) — модификатор необязателен
  - void, generic-тип, generic-метод: Тип<T> Имя<U>(...)
  - nullable/pointer/массив (в т.ч. многомерный) в возврате: Тип? Тип* Тип[] Тип[,]
  - ref-возврат: ref Тип Имя(...) / ref readonly Тип Имя(...)
  - tuple-возврат: (Тип a, Тип b) Имя(...)
  - expression-bodied: Тип Имя(...) => выражение;
  - перегрузка оператора: Тип operator +(...) { ... }
  - явная реализация интерфейса: Тип IFoo.Bar(...) { ... }
  - generic-ограничения между скобками и телом: Тип Имя<T>(...) where T : ... { }

Сознательно не покрыто (редкие случаи, отдельная задача при необходимости):
  локальные функции внутри других методов, индексаторы (this[...]),
  лямбды и методы, объявленные через поля/свойства.

Скобки параметров сопоставляются вручную (счётчик глубины), а не
регуляркой вида "[^)]*" — вложенные скобки (вызов в значении по
умолчанию, generic с запятой) иначе ломают разбор всего метода.
"""
import re

_MODIFIERS = (r'(?:public|private|protected|internal|static|override|virtual|'
              r'abstract|async|new|sealed|readonly|extern|unsafe|partial|ref)')

# Тип возврата: обычный/generic/массив (в т.ч. многомерный), с необязательным
# '?' (nullable) или '*' (unsafe pointer) — либо кортеж "(Тип a, Тип b)".
_RETURN_TYPE = (
    r'(?:'
    r'\([^()]*\)'                                     # кортеж
    r'|'
    r'[\w\.]+(?:<[^>{};]*>)?(?:\[[,\s]*\])*[?*]?'     # обычный/generic/массив
    r')'
)

# Имя метода: обычное (в т.ч. "IFoo.Bar" — явная реализация интерфейса)
# либо перегрузка оператора ("operator +", "operator ==", "operator true").
_OPERATOR_SYMBOLS = r'(?:[+\-*/%&|^!~<>=]+|true|false)'
_METHOD_NAME = r'(?:operator\s*' + _OPERATOR_SYMBOLS + r'|[\w\.]+)'

# Слова, которые по форме выглядят как "тип имя(" (например "return Foo(...)"
# или "if (...)"), но объявлением метода не являются.
_NOT_METHOD_HEAD = {
    "return", "if", "else", "while", "for", "foreach", "switch", "catch",
    "using", "lock", "throw", "yield", "await", "checked", "unchecked",
    "new", "typeof", "nameof", "sizeof", "case", "do", "fixed",
}

_METHOD_HEAD_RE = re.compile(
    r'(?:' + _MODIFIERS + r'\s+)*'
    r'(' + _RETURN_TYPE + r')'
    r'\s+(' + _METHOD_NAME + r')'
    r'(?:<[^>{};]*>)?'                # generic у самого метода
    r'\s*\('
)


def _match_paren(src: str, open_pos: int):
    """Позиция ')', соответствующей '(' в open_pos, с учётом вложенности."""
    depth = 0
    for i in range(open_pos, len(src)):
        if src[i] == '(':
            depth += 1
        elif src[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return None


def _extract_braced_body(src: str, open_pos: int) -> str:
    depth, start = 0, open_pos
    for i in range(open_pos, len(src)):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    return src[start:]


def _find_expr_end(src: str, start: int):
    """Конец expression-bodied тела (';' на верхнем уровне вложенности —
    сам ';' может быть внутри вложенных скобок лямбды, их не считаем)."""
    depth = 0
    for i in range(start, len(src)):
        c = src[i]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
        elif c == ';' and depth == 0:
            return i
    return None


def find_methods(src: str) -> list[tuple[str, str]]:
    """Возвращает [(имя_метода, текст_тела), ...] — и для {}-тела, и для
    expression-bodied (=> ...;). Объявления совсем без тела (интерфейсы,
    abstract — заканчиваются сразу на ';') пропускаются: анализировать нечего.
    """
    results = []
    for m in _METHOD_HEAD_RE.finditer(src):
        return_type = m.group(1).rsplit('.', 1)[-1]
        name = m.group(2)
        if return_type in _NOT_METHOD_HEAD or name in _NOT_METHOD_HEAD:
            continue

        close_paren = _match_paren(src, m.end() - 1)
        if close_paren is None:
            continue

        i = close_paren + 1
        while i < len(src) and src[i] in ' \t\r\n':
            i += 1

        # generic-ограничения ("where T : ...") стоят перед телом — если
        # они есть, тело всё равно начинается с ближайшей после них '{'.
        if src[i:i + 5] == 'where':
            j = src.find('{', i)
            if j == -1:
                continue
            i = j

        if i < len(src) and src[i] == '{':
            results.append((name, _extract_braced_body(src, i)))
        elif src[i:i + 2] == '=>':
            end = _find_expr_end(src, i + 2)
            if end is not None:
                results.append((name, src[i:end + 1]))
        # иначе объявление заканчивается ';' без тела — пропускаем

    return results
