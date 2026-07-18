"""Local JSON interaction rule provider.

Wraps ``data/demo_interactions.json`` behind a provider interface so the
InteractionAgent no longer reads files directly and alternative rule sources
can be plugged in later.
"""

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = PROJECT_ROOT / "data" / "demo_interactions.json"


class LocalJsonInteractionProvider:
    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or DEFAULT_RULES_PATH
        self._rules: list[dict[str, Any]] | None = None

    def get_interaction_rules(self) -> list[dict[str, Any]]:
        if self._rules is None:
            self._rules = self._load_rules()
        return self._rules

    def _load_rules(self) -> list[dict[str, Any]]:
        if not self.data_path.exists():
            return []

        with self.data_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise ValueError(
                "demo_interactions.json must contain a list of interaction rules."
            )

        return payload
