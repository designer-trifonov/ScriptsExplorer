"""Отвечает только за одно: найти известные Unity-антипаттерны в теле метода."""
import re

_ANTIPATTERNS: dict[str, re.Pattern] = {
    "FindObjectOfType": re.compile(r'\bFindObjectsOfType\b|\bFindObjectOfType\b'),
    "GameObject.Find":  re.compile(r'\bGameObject\.Find\b'),
    "Camera.main":      re.compile(r'\bCamera\.main\b'),
    "GetComponent":     re.compile(r'\bGetComponent\b'),
    "CompareTag":       re.compile(r'\bCompareTag\b'),
    "tag ==":           re.compile(r'\btag\s*==|==\s*\btag\b'),
    "SendMessage":      re.compile(r'\bSendMessage\b'),
    "Resources.Load":   re.compile(r'\bResources\.Load\b'),
}


def find_antipatterns(body: str) -> list[str]:
    return [name for name, pat in _ANTIPATTERNS.items() if pat.search(body)]
