"""Local RxNorm name lookup.

Reads the small SQLite database produced by ``scripts/build_rxnorm_db.py``.
The database contains RXNORM ingredient (IN/PIN) and brand (BN) names plus
brand -> ingredient mappings, so brand names entered by the user can be
resolved to their active ingredients before interaction checks.

If the database file does not exist the provider degrades gracefully and
every lookup returns ``None``.
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "rxnorm.db"


class RxNormLookupResult:
    def __init__(
        self,
        rxcui: str,
        name: str,
        tty: str,
        ingredients: list[str],
    ):
        self.rxcui = rxcui
        self.name = name
        self.tty = tty
        self.is_brand = tty == "BN"
        self.ingredients = ingredients


class RxNormProvider:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH

    @property
    def available(self) -> bool:
        return self.db_path.exists()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def lookup(self, name: str) -> RxNormLookupResult | None:
        """Exact (case-insensitive) name lookup. Ingredients win over brands."""
        normalized = name.strip().lower()
        if not normalized or not self.available:
            return None

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT rxcui, name, tty FROM drugs
                WHERE name_lower = ?
                ORDER BY CASE tty WHEN 'IN' THEN 0 WHEN 'PIN' THEN 1 ELSE 2 END
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()

            if row is None:
                return None

            ingredients: list[str] = []
            if row["tty"] == "BN":
                ingredient_rows = connection.execute(
                    """
                    SELECT d.name FROM brand_ingredient b
                    JOIN drugs d ON d.rxcui = b.ingredient_rxcui AND d.tty IN ('IN', 'PIN')
                    WHERE b.brand_rxcui = ?
                    """,
                    (row["rxcui"],),
                ).fetchall()
                ingredients = sorted({r["name"] for r in ingredient_rows})
            else:
                ingredients = [row["name"]]

        return RxNormLookupResult(
            rxcui=row["rxcui"],
            name=row["name"],
            tty=row["tty"],
            ingredients=ingredients,
        )

    def suggest(self, prefix: str, limit: int = 10) -> list[str]:
        """Prefix-based name suggestions for the UI."""
        normalized = prefix.strip().lower()
        if not normalized or not self.available:
            return []

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT name FROM drugs
                WHERE name_lower LIKE ? || '%'
                ORDER BY CASE tty WHEN 'IN' THEN 0 WHEN 'PIN' THEN 1 ELSE 2 END, length(name)
                LIMIT ?
                """,
                (normalized, limit),
            ).fetchall()

        return [row["name"] for row in rows]
