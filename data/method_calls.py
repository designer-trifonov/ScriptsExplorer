"""Отвечает только за одно: найти имена методов, которые вызываются
в теле метода. Это приближённый анализ по совпадению имени — как и
остальной разбор в script_parser, без резолвинга типов."""
import re

_CALL_RE = re.compile(r'\b([A-Za-z_]\w*)\s*\(')

# Ключевые слова языка, которые выглядят как вызов, но им не являются.
_NOT_CALLS = {
    "if", "for", "foreach", "while", "switch", "catch", "using", "lock",
    "new", "typeof", "nameof", "sizeof", "return", "base", "this",
}


def find_calls(body: str) -> list[str]:
    return sorted({
        m.group(1) for m in _CALL_RE.finditer(body)
        if m.group(1) not in _NOT_CALLS
    })
