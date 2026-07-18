"""DrugDataService: the Sprint 2 DrugDataProvider facade.

Combines the local RxNorm name database and the openFDA label API into a
single ``get_drug_info`` call used by the orchestrator and the UI. Every
external dependency is optional; when RxNorm or openFDA is unavailable the
returned ``DrugInfo`` simply carries less detail.
"""

from models.schemas import DrugInfo

from providers.openfda_client import OpenFdaClient
from providers.rxnorm_provider import RxNormProvider


class DrugDataService:
    def __init__(
        self,
        rxnorm: RxNormProvider | None = None,
        openfda: OpenFdaClient | None = None,
        use_openfda: bool = True,
    ):
        self.rxnorm = rxnorm or RxNormProvider()
        self.openfda = openfda or OpenFdaClient()
        self.use_openfda = use_openfda

    def get_drug_info(self, drug_name: str) -> DrugInfo:
        info = DrugInfo(query_name=drug_name.strip())
        sources: list[str] = []

        rxnorm_result = self.rxnorm.lookup(drug_name)
        if rxnorm_result is not None:
            info.normalized_name = rxnorm_result.name
            info.rxcui = rxnorm_result.rxcui
            info.is_brand = rxnorm_result.is_brand
            info.ingredients = rxnorm_result.ingredients
            sources.append("RxNorm (local)")

        if self.use_openfda:
            label = self.openfda.get_label(self._openfda_query_name(info))
            if label is not None:
                info.openfda_found = True
                info.boxed_warning = label.boxed_warning
                info.warnings = label.warnings
                info.drug_interactions = label.drug_interactions
                info.indications = label.indications
                sources.append("openFDA drug label")

        info.source = " + ".join(sources) if sources else "local input only"
        return info

    def _openfda_query_name(self, info: DrugInfo) -> str:
        """Prefer the resolved ingredient for label search, else the raw input."""
        if info.is_brand and info.ingredients:
            return info.ingredients[0]
        return info.normalized_name or info.query_name

    def resolve_to_ingredients(self, drug_name: str) -> list[str]:
        """Return lowercase ingredient names for interaction matching.

        Falls back to the raw input name when RxNorm cannot resolve it.
        """
        result = self.rxnorm.lookup(drug_name)
        if result is not None and result.ingredients:
            return [ingredient.lower() for ingredient in result.ingredients]
        return [drug_name.strip().lower()]
