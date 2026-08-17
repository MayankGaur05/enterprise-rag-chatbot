from dataclasses import dataclass
from typing import Any


@dataclass
class SearchResult:
    content: str
    score: float
    metadata: dict[str, Any]