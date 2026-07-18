"""Build a small local SQLite database from a full RxNorm release.

Usage:
    python scripts/build_rxnorm_db.py /path/to/RxNorm_full/rrf [output.db]

Extracts from RXNCONSO.RRF (SAB=RXNORM, non-suppressed):
    - IN  : ingredient names
    - PIN : precise ingredient names
    - BN  : brand names

and from RXNREL.RRF the tradename relations so brand names can be resolved
to their active ingredients. The resulting database is a few megabytes and
ships with the repo, so end users never need the multi-gigabyte RxNorm
download.
"""

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "rxnorm.db"

# RXNCONSO.RRF columns (0-indexed)
CONSO_RXCUI = 0
CONSO_SAB = 11
CONSO_TTY = 12
CONSO_STR = 14
CONSO_SUPPRESS = 16

# RXNREL.RRF columns (0-indexed)
REL_RXCUI1 = 0
REL_RXCUI2 = 4
REL_RELA = 7
REL_SAB = 10

WANTED_TTYS = {"IN", "PIN", "BN"}
TRADENAME_RELAS = {"tradename_of", "has_tradename"}


def load_concepts(conso_path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    with conso_path.open("r", encoding="utf-8") as file:
        for line in file:
            fields = line.rstrip("\n").split("|")
            if len(fields) <= CONSO_SUPPRESS:
                continue
            if fields[CONSO_SAB] != "RXNORM":
                continue
            if fields[CONSO_TTY] not in WANTED_TTYS:
                continue
            if fields[CONSO_SUPPRESS] not in {"N", ""}:
                continue

            key = (fields[CONSO_RXCUI], fields[CONSO_TTY], fields[CONSO_STR])
            if key in seen:
                continue
            seen.add(key)
            rows.append(key)

    return rows


def load_brand_ingredient_pairs(
    rel_path: Path,
    brand_cuis: set[str],
    ingredient_cuis: set[str],
) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    with rel_path.open("r", encoding="utf-8") as file:
        for line in file:
            if "tradename" not in line:
                continue

            fields = line.rstrip("\n").split("|")
            if len(fields) <= REL_SAB:
                continue
            if fields[REL_SAB] != "RXNORM":
                continue
            if fields[REL_RELA] not in TRADENAME_RELAS:
                continue

            cui_1, cui_2 = fields[REL_RXCUI1], fields[REL_RXCUI2]
            if cui_1 in brand_cuis and cui_2 in ingredient_cuis:
                pairs.add((cui_1, cui_2))
            elif cui_2 in brand_cuis and cui_1 in ingredient_cuis:
                pairs.add((cui_2, cui_1))

    return pairs


def build_database(rrf_dir: Path, output_path: Path) -> None:
    conso_path = rrf_dir / "RXNCONSO.RRF"
    rel_path = rrf_dir / "RXNREL.RRF"

    if not conso_path.exists():
        raise SystemExit(f"RXNCONSO.RRF not found in {rrf_dir}")

    print(f"Reading {conso_path} ...")
    concepts = load_concepts(conso_path)
    print(f"  {len(concepts)} concept names (IN/PIN/BN)")

    brand_cuis = {rxcui for rxcui, tty, _ in concepts if tty == "BN"}
    ingredient_cuis = {rxcui for rxcui, tty, _ in concepts if tty in {"IN", "PIN"}}

    pairs: set[tuple[str, str]] = set()
    if rel_path.exists():
        print(f"Reading {rel_path} ...")
        pairs = load_brand_ingredient_pairs(rel_path, brand_cuis, ingredient_cuis)
        print(f"  {len(pairs)} brand->ingredient relations")
    else:
        print("RXNREL.RRF not found, skipping brand->ingredient relations.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    print(f"Writing {output_path} ...")
    with sqlite3.connect(output_path) as connection:
        connection.executescript(
            """
            CREATE TABLE drugs (
                rxcui TEXT NOT NULL,
                tty TEXT NOT NULL,
                name TEXT NOT NULL,
                name_lower TEXT NOT NULL
            );
            CREATE TABLE brand_ingredient (
                brand_rxcui TEXT NOT NULL,
                ingredient_rxcui TEXT NOT NULL
            );
            """
        )
        connection.executemany(
            "INSERT INTO drugs (rxcui, tty, name, name_lower) VALUES (?, ?, ?, ?)",
            [(rxcui, tty, name, name.lower()) for rxcui, tty, name in concepts],
        )
        connection.executemany(
            "INSERT INTO brand_ingredient (brand_rxcui, ingredient_rxcui) VALUES (?, ?)",
            sorted(pairs),
        )
        connection.executescript(
            """
            CREATE INDEX idx_drugs_name_lower ON drugs (name_lower);
            CREATE INDEX idx_drugs_rxcui ON drugs (rxcui);
            CREATE INDEX idx_brand_ingredient_brand ON brand_ingredient (brand_rxcui);
            """
        )

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Done. Database size: {size_mb:.1f} MB")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    rrf_dir = Path(sys.argv[1]).expanduser()
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    build_database(rrf_dir, output_path)


if __name__ == "__main__":
    main()
