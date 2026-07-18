"""openFDA drug label client.

Queries the openFDA ``drug/label`` endpoint for warnings, boxed warnings,
interaction texts and indications. All failures (network, quota, not found)
degrade gracefully to ``None`` so the rule-based analysis keeps working
offline.
"""

import os

import requests

OPENFDA_LABEL_URL = "https://api.fda.gov/drug/label.json"
REQUEST_TIMEOUT_SECONDS = 10
MAX_SECTION_LENGTH = 1500


def _first_section(result: dict, key: str) -> str | None:
    value = result.get(key)
    if isinstance(value, list) and value:
        text = str(value[0]).strip()
        if len(text) > MAX_SECTION_LENGTH:
            text = text[:MAX_SECTION_LENGTH].rstrip() + " […]"
        return text or None
    return None


class OpenFdaLabel:
    def __init__(
        self,
        generic_name: str | None,
        brand_name: str | None,
        boxed_warning: str | None,
        warnings: str | None,
        drug_interactions: str | None,
        indications: str | None,
        drug_interactions_full: str | None = None,
    ):
        self.generic_name = generic_name
        self.brand_name = brand_name
        self.boxed_warning = boxed_warning
        self.warnings = warnings
        self.drug_interactions = drug_interactions
        self.indications = indications
        # Untruncated interaction text, used for programmatic matching.
        self.drug_interactions_full = drug_interactions_full or drug_interactions


class OpenFdaClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("OPENFDA_API_KEY")
        self._cache: dict[str, OpenFdaLabel | None] = {}

    def get_label(self, drug_name: str) -> OpenFdaLabel | None:
        normalized = drug_name.strip().lower()
        if not normalized:
            return None

        if normalized in self._cache:
            return self._cache[normalized]

        label = self._fetch_label(normalized)
        self._cache[normalized] = label
        return label

    def _fetch_label(self, drug_name: str) -> OpenFdaLabel | None:
        # openFDA treats space-separated terms as OR; requests encodes spaces as '+'.
        search = (
            f'openfda.generic_name:"{drug_name}"'
            f' openfda.brand_name:"{drug_name}"'
            f' openfda.substance_name:"{drug_name}"'
        )
        params: dict[str, str | int] = {"search": search, "limit": 1}
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = requests.get(
                OPENFDA_LABEL_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException:
            return None

        if response.status_code != 200:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        results = payload.get("results")
        if not isinstance(results, list) or not results:
            return None

        result = results[0]
        openfda = result.get("openfda", {}) if isinstance(result, dict) else {}

        def _first_openfda(key: str) -> str | None:
            value = openfda.get(key)
            if isinstance(value, list) and value:
                return str(value[0])
            return None

        interactions_raw = result.get("drug_interactions")
        interactions_full = None
        if isinstance(interactions_raw, list) and interactions_raw:
            interactions_full = str(interactions_raw[0]).strip() or None

        return OpenFdaLabel(
            generic_name=_first_openfda("generic_name"),
            brand_name=_first_openfda("brand_name"),
            boxed_warning=_first_section(result, "boxed_warning"),
            warnings=_first_section(result, "warnings")
            or _first_section(result, "warnings_and_cautions"),
            drug_interactions=_first_section(result, "drug_interactions"),
            indications=_first_section(result, "indications_and_usage"),
            drug_interactions_full=interactions_full,
        )
